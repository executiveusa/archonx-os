import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

from .biometric import DisabledBiometricProvider

app = FastAPI(title="ArchonX Voice Gateway", version="0.1.0")

ACCESS_KERNEL_BASE_URL = os.getenv("ACCESS_KERNEL_BASE_URL", "http://localhost:8090")
ALLOWLIST = {x.strip() for x in os.getenv("VOICE_ALLOWLIST", "").split(",") if x.strip()}
PASSPHRASE = os.getenv("VOICE_PASSPHRASE", "archonx-passphrase")
PIN = os.getenv("VOICE_PIN", "1234")
MAX_ATTEMPTS = int(os.getenv("VOICE_MAX_ATTEMPTS", "5"))
LOCKOUT_SECONDS = int(os.getenv("VOICE_LOCKOUT_SECONDS", "300"))
STORE_TRANSCRIPTS = os.getenv("VOICE_STORE_TRANSCRIPTS", "false").lower() == "true"
BIOMETRIC_ENABLED = os.getenv("VOICE_BIOMETRIC_ENABLED", "false").lower() == "true"
BIOMETRIC_PROVIDER = DisabledBiometricProvider()

ATTEMPTS: dict[str, int] = {}
LOCKED_UNTIL: dict[str, float] = {}


def _audit(event: str, payload: dict[str, Any], work_item_id: str | None = None) -> None:
    try:
        httpx.post(
            f"{ACCESS_KERNEL_BASE_URL}/v1/audit/event",
            json={"event": event, "payload": payload, "work_item_id": work_item_id},
            timeout=5.0,
        )
    except Exception:
        pass


def _authenticate(caller: str, passphrase: str, pin: str) -> None:
    now = time.time()
    if caller in LOCKED_UNTIL and LOCKED_UNTIL[caller] > now:
        raise HTTPException(status_code=429, detail="caller temporarily locked")

    if caller not in ALLOWLIST:
        _audit("voice.auth.denied", {"caller": caller, "reason": "not_allowlisted"})
        raise HTTPException(status_code=403, detail="caller not allowlisted")

    if passphrase != PASSPHRASE or pin != PIN:
        ATTEMPTS[caller] = ATTEMPTS.get(caller, 0) + 1
        if ATTEMPTS[caller] >= MAX_ATTEMPTS:
            LOCKED_UNTIL[caller] = now + LOCKOUT_SECONDS
            ATTEMPTS[caller] = 0
        _audit("voice.auth.failed", {"caller": caller})
        raise HTTPException(status_code=401, detail="invalid passphrase or pin")

    ATTEMPTS[caller] = 0
    if BIOMETRIC_ENABLED:
        # Optional plugin point. Default provider rejects unless replaced by deployment.
        if not BIOMETRIC_PROVIDER.verify(caller=caller, audio_ref="n/a"):
            raise HTTPException(status_code=403, detail="biometric verification failed")
    _audit("voice.auth.success", {"caller": caller})


def _run_action(action: str, args: dict[str, Any], caller: str, work_item_id: str) -> dict[str, Any]:
    if action == "status":
        r = httpx.get(f"{ACCESS_KERNEL_BASE_URL}/v1/health", timeout=10.0)
        return {"status": r.json()}

    if action == "list_approvals":
        r = httpx.get(f"{ACCESS_KERNEL_BASE_URL}/v1/grants/list", params={"status": "pending_approval"}, timeout=10.0)
        return r.json()

    if action == "approve_grant":
        grant_id = args.get("grant_id")
        r = httpx.post(
            f"{ACCESS_KERNEL_BASE_URL}/v1/grants/approve",
            json={"grant_id": grant_id, "approver": caller, "work_item_id": work_item_id},
            timeout=10.0,
        )
        return r.json()

    if action == "request_grant":
        r = httpx.post(
            f"{ACCESS_KERNEL_BASE_URL}/v1/grants/request",
            json={
                "principal": caller,
                "principal_type": "human",
                "resource": args.get("resource"),
                "action": args.get("resource_action"),
                "duration_minutes": int(args.get("duration_minutes", 15)),
                "work_item_id": work_item_id,
            },
            timeout=10.0,
        )
        return r.json()

    if action in {"doctor", "sync_check"}:
        # Placeholder actions for orchestration hooks.
        return {"status": "queued", "action": action}

    raise HTTPException(status_code=400, detail=f"unknown action: {action}")


@app.post("/v1/voice/dev/simulate")
def simulate(body: dict[str, Any]) -> dict[str, Any]:
    caller = body.get("caller", "")
    passphrase = body.get("passphrase", "")
    pin = body.get("pin", "")
    action = body.get("action", "status")
    args = body.get("args", {})
    work_item_id = body.get("work_item_id")

    if not work_item_id:
        raise HTTPException(status_code=400, detail="work_item_id is required")

    _authenticate(caller=caller, passphrase=passphrase, pin=pin)
    result = _run_action(action=action, args=args, caller=caller, work_item_id=work_item_id)

    _audit(
        "voice.action",
        {"caller": caller, "action": action, "args": args, "transcript_saved": STORE_TRANSCRIPTS},
        work_item_id=work_item_id,
    )
    return {"ok": True, "result": result}


@app.post("/v1/voice/twilio/incoming")
def twilio_incoming(body: dict[str, Any]) -> dict[str, Any]:
    # Twilio-compatible webhook payload shape can be transformed by caller.
    caller = body.get("From", body.get("caller", ""))
    command = body.get("SpeechResult", body.get("command", "status"))
    passphrase = body.get("passphrase", "")
    pin = body.get("pin", "")
    work_item_id = body.get("work_item_id")

    if not work_item_id:
        raise HTTPException(status_code=400, detail="work_item_id is required")

    _authenticate(caller=caller, passphrase=passphrase, pin=pin)

    if command.startswith("approve grant "):
        action = "approve_grant"
        args = {"grant_id": command.replace("approve grant ", "", 1).strip()}
    elif command.startswith("request grant "):
        action = "request_grant"
        parts = command.split()
        args = {
            "resource": parts[2] if len(parts) > 2 else "unknown",
            "resource_action": parts[3] if len(parts) > 3 else "read",
            "duration_minutes": int(parts[4]) if len(parts) > 4 else 15,
        }
    elif command == "list approvals":
        action = "list_approvals"
        args = {}
    elif command in {"status", "doctor", "sync check", "sync_check"}:
        action = command.replace(" ", "_")
        args = {}
    else:
        raise HTTPException(status_code=400, detail="unsupported voice command")

    result = _run_action(action=action, args=args, caller=caller, work_item_id=work_item_id)
    _audit("voice.twilio.action", {"caller": caller, "action": action}, work_item_id=work_item_id)
    return {"ok": True, "action": action, "result": result}


@app.get("/v1/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "voice-gateway"}
