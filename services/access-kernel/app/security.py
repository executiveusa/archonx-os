import base64
import hashlib
import json
import os
import secrets
from typing import Any

from cryptography.fernet import Fernet


def _derive_fernet_key(raw: str) -> bytes:
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def get_master_fernet() -> Fernet:
    raw = os.getenv("ACCESS_KERNEL_MASTER_KEY", "")
    if not raw:
        # Dev fallback; still encrypted-at-rest but not suitable for production.
        raw = "dev-master-key-change-me"
    return Fernet(_derive_fernet_key(raw))


def encrypt_json(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    token = get_master_fernet().encrypt(data)
    return token.decode("utf-8")


def decrypt_json(token: str) -> dict[str, Any]:
    raw = get_master_fernet().decrypt(token.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def mint_token(payload: dict[str, Any]) -> str:
    body = payload.copy()
    body["jti"] = secrets.token_hex(12)
    return encrypt_json(body)


def mask_payload(payload: dict[str, str]) -> dict[str, str]:
    masked: dict[str, str] = {}
    for key, value in payload.items():
        suffix = value[-4:] if len(value) >= 4 else "****"
        masked[key] = f"***{suffix}"
    return masked
