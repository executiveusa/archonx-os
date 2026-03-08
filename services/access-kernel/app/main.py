import datetime as dt
import json
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from jsonschema import validate

from .policy import PolicyEngine
from .security import decrypt_json, encrypt_json, mask_payload, mint_token
from .store import Store

app = FastAPI(title="ArchonX Access Kernel", version="0.1.0")

DB_PATH = os.getenv("ACCESS_KERNEL_DB_PATH", "./data/access-kernel.db")
AUDIT_PATH = Path(os.getenv("ACCESS_KERNEL_AUDIT_PATH", "./data/audit.jsonl"))
SCHEMA_PATH = Path(os.getenv("ACCESS_KERNEL_SECRETS_SCHEMA", "./config/secrets-json-schema.json"))
POLICY_PATH = os.getenv("ACCESS_KERNEL_POLICY_PATH", "./config/policy.json")

store = Store(DB_PATH)
policy = PolicyEngine(POLICY_PATH)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def require_work_item_id(work_item_id: str | None) -> str:
    if not work_item_id or not str(work_item_id).strip():
        raise HTTPException(status_code=400, detail="work_item_id is required for privileged operations")
    return str(work_item_id).strip()


def write_audit(event: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": now_iso(), **event}
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def parse_duration(minutes: int) -> str:
    expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
    return expires.replace(microsecond=0).isoformat()


@app.get("/v1/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "access-kernel",
        "policy_hash": policy.hash,
        "time": now_iso(),
    }


@app.post("/v1/login/mock")
def login_mock(body: dict[str, Any]) -> dict[str, Any]:
    principal = body.get("principal", "unknown")
    principal_type = body.get("principal_type", "human")
    duration = int(body.get("duration_minutes", 60))

    sid = str(uuid.uuid4())
    expires_at = parse_duration(duration)
    token = mint_token(
        {
            "sub": principal,
            "principal_type": principal_type,
            "sid": sid,
            "exp": expires_at,
            "mode": "mock",
        }
    )

    store.execute(
        "INSERT INTO sessions (id, principal, principal_type, expires_at, created_at) VALUES (?, ?, ?, ?, ?)",
        (sid, principal, principal_type, expires_at, now_iso()),
    )
    write_audit({"event": "login", "mode": "mock", "principal": principal, "principal_type": principal_type})
    return {"session_id": sid, "token": token, "expires_at": expires_at}


@app.post("/v1/secrets/upload")
def secrets_upload(body: dict[str, Any]) -> dict[str, Any]:
    principal = body.get("principal", "unknown")
    work_item_id = require_work_item_id(body.get("work_item_id"))
    metadata = body.get("metadata") or {}

    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    validate(instance={"name": body.get("name"), "payload": body.get("payload"), "metadata": metadata}, schema=schema)

    payload = body.get("payload", {})
    secret_id = str(uuid.uuid4())
    encrypted = encrypt_json(payload)
    store.execute(
        "INSERT INTO secrets (id, name, encrypted_payload, metadata_json, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            secret_id,
            body.get("name"),
            encrypted,
            json.dumps(metadata),
            principal,
            now_iso(),
        ),
    )
    write_audit(
        {
            "event": "secret.upload",
            "secret_id": secret_id,
            "name": body.get("name"),
            "principal": principal,
            "work_item_id": work_item_id,
            "keys": sorted(list(payload.keys())),
        }
    )
    return {
        "secret_id": secret_id,
        "name": body.get("name"),
        "preview": mask_payload(payload),
        "stored": True,
    }


@app.post("/v1/grants/request")
def grants_request(body: dict[str, Any]) -> dict[str, Any]:
    work_item_id = require_work_item_id(body.get("work_item_id"))
    principal = body.get("principal", "unknown")
    principal_type = body.get("principal_type", "agent")
    resource = body.get("resource")
    action = body.get("action")
    duration_minutes = int(body.get("duration_minutes", 30))

    decision = policy.evaluate(principal_type=principal_type, resource=resource, action=action)
    grant_id = str(uuid.uuid4())

    if not decision["allow"]:
        status = "denied"
    elif decision["approval_required"]:
        status = "pending_approval"
    else:
        status = "approved"

    expires_at = parse_duration(duration_minutes) if status == "approved" else None

    store.execute(
        """
        INSERT INTO grants (
            id, principal, principal_type, work_item_id, resource, action,
            duration_minutes, status, approval_required, approved_by, created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            grant_id,
            principal,
            principal_type,
            work_item_id,
            resource,
            action,
            duration_minutes,
            status,
            1 if decision["approval_required"] else 0,
            None,
            now_iso(),
            expires_at,
        ),
    )

    write_audit(
        {
            "event": "grant.request",
            "grant_id": grant_id,
            "principal": principal,
            "principal_type": principal_type,
            "resource": resource,
            "action": action,
            "status": status,
            "work_item_id": work_item_id,
        }
    )

    return {"grant_id": grant_id, "status": status, "approval_required": decision["approval_required"], "expires_at": expires_at}


@app.post("/v1/grants/approve")
def grants_approve(body: dict[str, Any]) -> dict[str, Any]:
    work_item_id = require_work_item_id(body.get("work_item_id"))
    grant_id = body.get("grant_id")
    approver = body.get("approver", "admin")

    row = store.fetchone("SELECT * FROM grants WHERE id = ?", (grant_id,))
    if not row:
        raise HTTPException(status_code=404, detail="grant not found")

    if row["status"] not in {"pending_approval", "approved"}:
        raise HTTPException(status_code=400, detail=f"cannot approve grant in status {row['status']}")

    expires_at = parse_duration(int(row["duration_minutes"]))
    store.execute(
        "UPDATE grants SET status = ?, approved_by = ?, expires_at = ? WHERE id = ?",
        ("approved", approver, expires_at, grant_id),
    )
    write_audit({"event": "grant.approve", "grant_id": grant_id, "approver": approver, "work_item_id": work_item_id})
    return {"grant_id": grant_id, "status": "approved", "expires_at": expires_at}


@app.post("/v1/grants/revoke")
def grants_revoke(body: dict[str, Any]) -> dict[str, Any]:
    work_item_id = require_work_item_id(body.get("work_item_id"))
    grant_id = body.get("grant_id")
    actor = body.get("actor", "admin")

    row = store.fetchone("SELECT * FROM grants WHERE id = ?", (grant_id,))
    if not row:
        raise HTTPException(status_code=404, detail="grant not found")

    store.execute("UPDATE grants SET status = ? WHERE id = ?", ("revoked", grant_id))
    write_audit({"event": "grant.revoke", "grant_id": grant_id, "actor": actor, "work_item_id": work_item_id})
    return {"grant_id": grant_id, "status": "revoked"}


@app.get("/v1/grants/list")
def grants_list(status: str | None = Query(default=None)) -> dict[str, Any]:
    if status:
        rows = store.fetchall("SELECT * FROM grants WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        rows = store.fetchall("SELECT * FROM grants ORDER BY created_at DESC")
    return {"items": rows}


@app.get("/v1/audit/export")
def audit_export(format: str = Query(default="jsonl")) -> Any:
    if format != "jsonl":
        raise HTTPException(status_code=400, detail="only jsonl export is supported")
    if not AUDIT_PATH.exists():
        return {"data": ""}
    return {"data": AUDIT_PATH.read_text(encoding="utf-8")}


@app.post("/v1/audit/event")
def audit_event(body: dict[str, Any]) -> dict[str, Any]:
    event = body.get("event", "custom")
    write_audit({"event": event, "payload": body.get("payload", {}), "work_item_id": body.get("work_item_id")})
    return {"status": "ok"}


@app.get("/v1/evidence/export")
def evidence_export(from_ts: str | None = Query(default=None), to_ts: str | None = Query(default=None)) -> dict[str, Any]:
    window = {"from": from_ts or "beginning", "to": to_ts or "now"}
    snapshot = {
        "policy_hash": policy.hash,
        "config": {
            "db_path": DB_PATH,
            "audit_path": str(AUDIT_PATH),
            "schema_path": str(SCHEMA_PATH),
            "policy_path": POLICY_PATH,
        },
    }
    payload = {"generated_at": now_iso(), "audit_window": window, "snapshot": snapshot}
    write_audit({"event": "evidence.export", "payload": payload})
    return payload


@app.post("/v1/secrets/resolve")
def secrets_resolve(body: dict[str, Any]) -> dict[str, Any]:
    # Dev endpoint used by self-test and tunnel/handle prototype; never returns raw values.
    work_item_id = require_work_item_id(body.get("work_item_id"))
    secret_id = body.get("secret_id")
    grant_id = body.get("grant_id")

    grant = store.fetchone("SELECT * FROM grants WHERE id = ?", (grant_id,))
    if not grant or grant["status"] != "approved":
        raise HTTPException(status_code=403, detail="approved grant required")

    secret = store.fetchone("SELECT * FROM secrets WHERE id = ?", (secret_id,))
    if not secret:
        raise HTTPException(status_code=404, detail="secret not found")

    masked = mask_payload(decrypt_json(secret["encrypted_payload"]))
    handle = mint_token({"secret_id": secret_id, "grant_id": grant_id, "exp": parse_duration(10)})
    write_audit({"event": "secret.resolve", "secret_id": secret_id, "grant_id": grant_id, "work_item_id": work_item_id})
    return {"handle": handle, "preview": masked}
