import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import requests

try:
    import keyring  # type: ignore
except Exception:
    keyring = None

from cryptography.fernet import Fernet

BASE_URL = os.getenv("ARCHONX_ACCESS_KERNEL_URL", "http://localhost:8090")
SESSION_SERVICE = "archonxctl"
SESSION_KEY = "session_token"
SESSION_FILE = Path.home() / ".archonx" / "session.enc"


def _fernet() -> Fernet:
    seed = os.getenv("ACCESS_KERNEL_MASTER_KEY", "dev-master-key-change-me")
    key = base64.urlsafe_b64encode(hashlib.sha256(seed.encode("utf-8")).digest())
    return Fernet(key)


def _save_token(token: str) -> None:
    if keyring is not None:
        try:
            keyring.set_password(SESSION_SERVICE, SESSION_KEY, token)
            return
        except Exception:
            pass
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(_fernet().encrypt(token.encode("utf-8")).decode("utf-8"), encoding="utf-8")


def _load_token() -> str | None:
    if keyring is not None:
        try:
            value = keyring.get_password(SESSION_SERVICE, SESSION_KEY)
            if value:
                return value
        except Exception:
            pass
    if SESSION_FILE.exists():
        raw = SESSION_FILE.read_text(encoding="utf-8")
        return _fernet().decrypt(raw.encode("utf-8")).decode("utf-8")
    return None


def _call(method: str, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    token = _load_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.request(method, f"{BASE_URL}{path}", json=body, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def cmd_login(args: argparse.Namespace) -> None:
    body = {
        "principal": args.principal,
        "principal_type": args.principal_type,
        "duration_minutes": args.duration,
    }
    data = _call("POST", "/v1/login/mock", body=body)
    _save_token(data["token"])
    print(json.dumps({"status": "ok", "session_id": data["session_id"], "expires_at": data["expires_at"]}, indent=2))


def cmd_grant_request(args: argparse.Namespace) -> None:
    data = _call(
        "POST",
        "/v1/grants/request",
        body={
            "principal": args.principal,
            "principal_type": args.principal_type,
            "work_item_id": args.work_item_id,
            "resource": args.resource,
            "action": args.action,
            "duration_minutes": args.duration,
        },
    )
    print(json.dumps(data, indent=2))


def cmd_grant_approve(args: argparse.Namespace) -> None:
    data = _call("POST", "/v1/grants/approve", body={"grant_id": args.grant_id, "approver": args.approver, "work_item_id": args.work_item_id})
    print(json.dumps(data, indent=2))


def cmd_grant_revoke(args: argparse.Namespace) -> None:
    data = _call("POST", "/v1/grants/revoke", body={"grant_id": args.grant_id, "actor": args.actor, "work_item_id": args.work_item_id})
    print(json.dumps(data, indent=2))


def cmd_grant_list(_args: argparse.Namespace) -> None:
    data = _call("GET", "/v1/grants/list")
    print(json.dumps(data, indent=2))


def cmd_secrets_upload(args: argparse.Namespace) -> None:
    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    body = {
        "principal": args.principal,
        "work_item_id": args.work_item_id,
        "name": payload["name"],
        "payload": payload["payload"],
        "metadata": payload.get("metadata", {}),
    }
    data = _call("POST", "/v1/secrets/upload", body=body)
    print(json.dumps(data, indent=2))


def cmd_audit_export(args: argparse.Namespace) -> None:
    data = _call("GET", "/v1/audit/export", params={"format": "jsonl"})
    Path(args.output).write_text(data.get("data", ""), encoding="utf-8")
    print(json.dumps({"status": "ok", "output": args.output}, indent=2))


def cmd_doctor(_args: argparse.Namespace) -> None:
    health = _call("GET", "/v1/health")
    print(json.dumps({"status": "ok", "health": health, "session_present": _load_token() is not None}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="archonxctl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    login = sub.add_parser("login")
    login.add_argument("--principal", required=True)
    login.add_argument("--principal-type", default="human", choices=["human", "agent"])
    login.add_argument("--duration", type=int, default=60)
    login.set_defaults(func=cmd_login)

    grants = sub.add_parser("grants")
    gsub = grants.add_subparsers(dest="grant_cmd", required=True)

    req = gsub.add_parser("request")
    req.add_argument("--principal", required=True)
    req.add_argument("--principal-type", default="human", choices=["human", "agent"])
    req.add_argument("--work-item-id", required=True)
    req.add_argument("--resource", required=True)
    req.add_argument("--action", required=True)
    req.add_argument("--duration", type=int, default=30)
    req.set_defaults(func=cmd_grant_request)

    approve = gsub.add_parser("approve")
    approve.add_argument("--grant-id", required=True)
    approve.add_argument("--approver", required=True)
    approve.add_argument("--work-item-id", required=True)
    approve.set_defaults(func=cmd_grant_approve)

    revoke = gsub.add_parser("revoke")
    revoke.add_argument("--grant-id", required=True)
    revoke.add_argument("--actor", required=True)
    revoke.add_argument("--work-item-id", required=True)
    revoke.set_defaults(func=cmd_grant_revoke)

    glist = gsub.add_parser("list")
    glist.set_defaults(func=cmd_grant_list)

    secrets = sub.add_parser("secrets")
    ssub = secrets.add_subparsers(dest="secrets_cmd", required=True)
    upload = ssub.add_parser("upload")
    upload.add_argument("--file", required=True)
    upload.add_argument("--principal", required=True)
    upload.add_argument("--work-item-id", required=True)
    upload.set_defaults(func=cmd_secrets_upload)

    audit = sub.add_parser("audit")
    asub = audit.add_subparsers(dest="audit_cmd", required=True)
    export = asub.add_parser("export")
    export.add_argument("--output", required=True)
    export.set_defaults(func=cmd_audit_export)

    doctor = sub.add_parser("doctor")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
