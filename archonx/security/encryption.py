"""
Encryption Module - AES-256-GCM + TLS 1.3
Enterprise-grade encryption for data at rest and in transit
"""

from __future__ import annotations
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64

logger = logging.getLogger("archonx.security.encryption")

class EncryptionManager:
    """
    AES-256-GCM encryption for data at rest.
    TLS 1.3 handles data in transit (configured in server).
    """
    
    def __init__(self, master_key: bytes | None = None) -> None:
        self.master_key = master_key or self._generate_master_key()
        logger.info("Encryption manager initialized (AES-256-GCM)")
    
    def _generate_master_key(self) -> bytes:
        """Generate cryptographically secure master key."""
        return AESGCM.generate_key(bit_length=256)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes | None = None) -> tuple[bytes, bytes]:
        """
        Encrypt data with AES-256-GCM.
        
        Returns:
            (ciphertext, nonce) tuple
        """
        aesgcm = AESGCM(self.master_key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        return ciphertext, nonce
    
    def decrypt(self, ciphertext: bytes, nonce: bytes, associated_data: bytes | None = None) -> bytes:
        """Decrypt data with AES-256-GCM."""
        aesgcm = AESGCM(self.master_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        return plaintext
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64-encoded ciphertext."""
        ciphertext, nonce = self.encrypt(text.encode('utf-8'))
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('ascii')
    
    def decrypt_string(self, encrypted: str) -> str:
        """Decrypt base64-encoded ciphertext to string."""
        combined = base64.b64decode(encrypted)
        nonce, ciphertext = combined[:12], combined[12:]
        plaintext = self.decrypt(ciphertext, nonce)
        return plaintext.decode('utf-8')
