from typing import Protocol


class BiometricProvider(Protocol):
    def verify(self, caller: str, audio_ref: str) -> bool:
        ...


class DisabledBiometricProvider:
    def verify(self, caller: str, audio_ref: str) -> bool:
        # Biometric auth is intentionally disabled by default.
        return False
