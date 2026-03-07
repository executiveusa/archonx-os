import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ArchonXVault:
    """
    ZTE-compliant Secret Vault for ArchonX OS.
    Transitioning from plaintext .env files to encrypted structured storage.
    """
    
    def __init__(self, vault_path: str = ".archonx/vault.bin"):
        self.vault_path = Path(vault_path)
        self.master_key = os.getenv("ARCHONX_MASTER_KEY", "zte-default-insecure-key")
        self._fernet = self._init_fernet()
        
    def _init_fernet(self) -> Fernet:
        # Simple KDF to turn master_key into 32-byte Fernet key
        salt = b'archonx-salt' # In production, this should be unique and stored
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)

    def save_secrets(self, secrets: dict):
        self.vault_path.parent.mkdir(exist_ok=True)
        data = json.dumps(secrets).encode()
        encrypted = self._fernet.encrypt(data)
        with open(self.vault_path, "wb") as f:
            f.write(encrypted)

    def load_secrets(self) -> dict:
        if not self.vault_path.exists():
            return {}
        with open(self.vault_path, "rb") as f:
            encrypted = f.read()
        try:
            decrypted = self._fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"Vault decryption failed: {e}")
            return {}

if __name__ == "__main__":
    # Self-test / Initial Migration
    vault = ArchonXVault()
    # Migration stub - in practice, we'll read master.env here
    test_secrets = {"VERCEL_TOKEN": "migrated-from-env"}
    vault.save_secrets(test_secrets)
    print("Vault initialized and test secret saved.")
