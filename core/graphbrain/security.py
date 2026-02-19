import hmac
import hashlib


def verify_github_signature(secret: str, payload: bytes, signature_header: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
