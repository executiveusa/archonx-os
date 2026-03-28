"""
BEAD-POPEBOT-001 — Rate Limiter
=================================
Per-channel token-bucket rate limiting for Popebot.
Prevents API abuse under high agent activity.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Bucket:
    capacity: int
    tokens: float
    refill_rate: float      # tokens per second
    last_refill: float = field(default_factory=time.monotonic)
    _lock: threading.Lock = field(default_factory=threading.Lock, compare=False, repr=False)


_CHANNEL_LIMITS: dict[str, tuple[int, float]] = {
    # channel_name: (capacity, tokens_per_second)
    "EMAIL":    (100, 1.0),     # 100 emails / burst; refill 1/sec (3600/hr)
    "SLACK":    (50,  2.0),
    "SMS":      (30,  0.5),     # Twilio limits
    "TWITTER":  (10,  0.1),     # Twitter API v2 free tier: 1500 tweets/month
    "LINKEDIN": (5,   0.05),
}


class RateLimiter:
    """Token-bucket rate limiter, one bucket per channel."""

    def __init__(self) -> None:
        self._buckets: dict[str, _Bucket] = {}
        for channel, (cap, rate) in _CHANNEL_LIMITS.items():
            self._buckets[channel] = _Bucket(
                capacity=cap, tokens=float(cap), refill_rate=rate
            )

    def consume(self, channel: str, bypass_for_critical: bool = False) -> bool:
        """
        Return True if the channel has capacity; False if rate-limited.
        CRITICAL priority bypasses; all others go through the bucket.
        """
        if bypass_for_critical:
            return True

        bucket = self._buckets.get(channel.upper())
        if bucket is None:
            return True     # Unknown channel — allow

        with bucket._lock:
            now = time.monotonic()
            elapsed = now - bucket.last_refill
            bucket.tokens = min(
                bucket.capacity,
                bucket.tokens + elapsed * bucket.refill_rate
            )
            bucket.last_refill = now

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False

    def get_wait_seconds(self, channel: str) -> float:
        """How many seconds until the channel bucket has a token."""
        bucket = self._buckets.get(channel.upper())
        if bucket is None or bucket.tokens >= 1.0:
            return 0.0
        deficit = 1.0 - bucket.tokens
        return deficit / bucket.refill_rate if bucket.refill_rate > 0 else float("inf")
