"""
services/saleor/agents/saleor_agent.py

BaseSkill-compatible agent wrapper for the Saleor agentic commerce stack.

Exposes product search, checkout creation, and order management as named
agent actions that can be invoked by the ArchonX orchestrator or any knight
crew that imports it.

Usage example::

    from services.saleor.agents.saleor_agent import SaleorAgent

    agent = SaleorAgent()
    result = agent.run("search_products", query="blue hoodie", channel="dash-product")
    print(result.data)
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.skills.base import BaseSkill, SkillResult

from services.saleor.tools.checkout_flow import (
    add_shipping_address,
    complete_checkout,
    create_checkout,
)
from services.saleor.tools.order_management import (
    get_order_status,
    get_total_order_count,
    list_recent_orders,
)
from services.saleor.tools.product_search import search_products

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported actions
# ---------------------------------------------------------------------------

ACTIONS = frozenset(
    [
        "search_products",
        "create_checkout",
        "add_shipping_address",
        "complete_checkout",
        "get_order_status",
        "get_recent_orders",
        "get_total_order_count",
    ]
)


class SaleorAgent(BaseSkill):
    """ArchonX skill that routes commerce actions to the Saleor GraphQL API.

    Supported actions
    -----------------
    search_products
        kwargs: query (str), channel (str), limit (int, default 10)

    create_checkout
        kwargs: channel (str), lines (list of {variantId, quantity})

    add_shipping_address
        kwargs: checkout_id (str), address (dict of AddressInput fields)

    complete_checkout
        kwargs: checkout_id (str), payment_data (dict)

    get_order_status
        kwargs: order_id (str)

    get_recent_orders
        kwargs: channel (str), limit (int, default 5)

    get_total_order_count
        kwargs: channel (str)
    """

    name: str = "saleor_commerce"

    # ------------------------------------------------------------------
    # BaseSkill interface
    # ------------------------------------------------------------------

    def run(self, action: str, **kwargs: Any) -> SkillResult:
        """Dispatch an action to the appropriate Saleor tool.

        Args:
            action: One of the supported action strings listed above.
            **kwargs: Action-specific keyword arguments.

        Returns:
            SkillResult with ``success=True`` and ``data`` populated on success,
            or ``success=False`` and ``error`` set on failure.
        """
        logger.debug("SaleorAgent.run | action=%s kwargs=%s", action, list(kwargs.keys()))

        if action not in ACTIONS:
            return SkillResult(
                success=False,
                error=f"Unknown action '{action}'. Supported: {sorted(ACTIONS)}",
            )

        try:
            return self._dispatch(action, **kwargs)
        except TypeError as exc:
            # Missing or unexpected kwargs for the underlying tool function
            logger.error("SaleorAgent parameter error | action=%s error=%s", action, exc)
            return SkillResult(success=False, error=f"Parameter error for action '{action}': {exc}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("SaleorAgent unexpected error | action=%s", action)
            return SkillResult(success=False, error=f"Unexpected error in action '{action}': {exc}")

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, action: str, **kwargs: Any) -> SkillResult:
        if action == "search_products":
            return self._search_products(**kwargs)
        if action == "create_checkout":
            return self._create_checkout(**kwargs)
        if action == "add_shipping_address":
            return self._add_shipping_address(**kwargs)
        if action == "complete_checkout":
            return self._complete_checkout(**kwargs)
        if action == "get_order_status":
            return self._get_order_status(**kwargs)
        if action == "get_recent_orders":
            return self._get_recent_orders(**kwargs)
        if action == "get_total_order_count":
            return self._get_total_order_count(**kwargs)
        # Should never reach here given the ACTIONS guard above
        return SkillResult(success=False, error=f"Unhandled action: {action}")

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _search_products(
        self,
        query: str,
        channel: str,
        limit: int = 10,
    ) -> SkillResult:
        result = search_products(query=query, channel=channel, limit=limit)
        if "error" in result:
            return SkillResult(success=False, error=result["error"], data=result)
        return SkillResult(success=True, data=result)

    def _create_checkout(
        self,
        channel: str,
        lines: list[dict[str, Any]],
    ) -> SkillResult:
        result = create_checkout(channel=channel, lines=lines)
        if result.get("error") or result.get("errors"):
            return SkillResult(
                success=False,
                error=result.get("error") or str(result.get("errors")),
                data=result,
            )
        return SkillResult(success=True, data=result)

    def _add_shipping_address(
        self,
        checkout_id: str,
        address: dict[str, Any],
    ) -> SkillResult:
        result = add_shipping_address(checkout_id=checkout_id, address=address)
        if result.get("error") or result.get("errors"):
            return SkillResult(
                success=False,
                error=result.get("error") or str(result.get("errors")),
                data=result,
            )
        return SkillResult(success=True, data=result)

    def _complete_checkout(
        self,
        checkout_id: str,
        payment_data: dict[str, Any],
    ) -> SkillResult:
        result = complete_checkout(checkout_id=checkout_id, payment_data=payment_data)
        if result.get("error") or result.get("errors"):
            return SkillResult(
                success=False,
                error=result.get("error") or str(result.get("errors")),
                data=result,
            )
        return SkillResult(success=True, data=result)

    def _get_order_status(self, order_id: str) -> SkillResult:
        result = get_order_status(order_id=order_id)
        if "error" in result:
            return SkillResult(success=False, error=result["error"], data=result)
        return SkillResult(success=True, data=result)

    def _get_recent_orders(
        self,
        channel: str,
        limit: int = 5,
    ) -> SkillResult:
        result = list_recent_orders(channel=channel, limit=limit)
        if "error" in result:
            return SkillResult(success=False, error=result["error"], data=result)
        return SkillResult(success=True, data=result)

    def _get_total_order_count(self, channel: str) -> SkillResult:
        result = get_total_order_count(channel=channel)
        if "error" in result:
            return SkillResult(success=False, error=result["error"], data=result)
        return SkillResult(success=True, data=result)
