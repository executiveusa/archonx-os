"""
Token Meter — Billing Engine
=============================
Tracks token usage across the system for billing purposes.

Token sources:
- Agent Theater viewing (watch agents work)
- Skill executions (pay per use)
- API calls (external integrations)
- Computer-use sessions (Orgo VM time)

Integrates with Stripe for payment processing.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("archonx.billing.token_meter")


@dataclass
class TokenTransaction:
    """A single token transaction."""
    id: str
    user_id: str
    amount: int          # positive = spend, negative = refund/credit
    source: str          # theater | skill | api | computer_use
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class TokenMeter:
    """
    Central billing engine for token-based usage tracking.

    All billable actions go through the meter. The meter maintains
    per-user balances and transaction history.
    """

    def __init__(self) -> None:
        self._balances: dict[str, int] = defaultdict(int)
        self._transactions: list[TokenTransaction] = []
        self._counter = 0

    def credit(self, user_id: str, amount: int, source: str = "purchase", description: str = "") -> TokenTransaction:
        """Add tokens to a user's balance."""
        self._counter += 1
        txn = TokenTransaction(
            id=f"txn-{self._counter:06d}",
            user_id=user_id,
            amount=-amount,  # negative = credit (tokens added)
            source=source,
            description=description or f"Credit {amount} tokens",
        )
        self._balances[user_id] += amount
        self._transactions.append(txn)
        logger.info("Token credit: %s +%d (%s)", user_id, amount, source)
        return txn

    def charge(self, user_id: str, amount: int, source: str, description: str = "") -> TokenTransaction | None:
        """
        Charge tokens from a user's balance.
        Returns None if insufficient balance.
        """
        if self._balances[user_id] < amount:
            logger.warning("Token charge failed: %s has %d, needs %d", user_id, self._balances[user_id], amount)
            return None

        self._counter += 1
        txn = TokenTransaction(
            id=f"txn-{self._counter:06d}",
            user_id=user_id,
            amount=amount,
            source=source,
            description=description or f"Charge {amount} tokens for {source}",
        )
        self._balances[user_id] -= amount
        self._transactions.append(txn)
        logger.info("Token charge: %s -%d (%s)", user_id, amount, source)
        return txn

    def balance(self, user_id: str) -> int:
        """Get current token balance for a user."""
        return self._balances.get(user_id, 0)

    def history(self, user_id: str, limit: int = 50) -> list[TokenTransaction]:
        """Get transaction history for a user."""
        user_txns = [t for t in self._transactions if t.user_id == user_id]
        return user_txns[-limit:]

    @property
    def stats(self) -> dict[str, Any]:
        total_charged = sum(t.amount for t in self._transactions if t.amount > 0)
        total_credited = sum(-t.amount for t in self._transactions if t.amount < 0)
        return {
            "total_users": len(self._balances),
            "total_charged": total_charged,
            "total_credited": total_credited,
            "total_transactions": len(self._transactions),
            "active_balances": {uid: bal for uid, bal in self._balances.items() if bal > 0},
        }
