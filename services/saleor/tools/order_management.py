"""
services/saleor/tools/order_management.py

Order management tools for the Saleor agentic commerce stack.

Provides read-only helpers for agents that need to inspect order state,
list recent orders, or aggregate metrics across a channel.

Environment variables:
    SALEOR_API_URL  -- Full URL to the Saleor GraphQL endpoint (required)
    SALEOR_TOKEN    -- Bearer token with order read permissions (required for
                       all order queries — order data is never public)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_api_url() -> str:
    url = os.getenv("SALEOR_API_URL", "")
    if not url:
        raise EnvironmentError("SALEOR_API_URL environment variable is not set")
    return url


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    token = os.getenv("SALEOR_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _execute_query(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    """POST a GraphQL query to Saleor and return the parsed response body."""
    api_url = _get_api_url()
    headers = _build_headers()
    payload = {"query": query, "variables": variables}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

    return response.json()


# ---------------------------------------------------------------------------
# GraphQL documents
# ---------------------------------------------------------------------------

ORDER_STATUS_QUERY = """
query GetOrderStatus($orderId: ID!) {
  order(id: $orderId) {
    id
    number
    status
    paymentStatus
    created
    updatedAt
    total {
      gross {
        amount
        currency
      }
      net {
        amount
        currency
      }
    }
    shippingAddress {
      firstName
      lastName
      streetAddress1
      city
      country {
        code
        country
      }
      postalCode
    }
    lines {
      id
      productName
      variantName
      quantity
      totalPrice {
        gross {
          amount
          currency
        }
      }
    }
    fulfillments {
      id
      status
      trackingNumber
      lines {
        id
        quantity
        orderLine {
          productName
          variantName
        }
      }
    }
    events {
      id
      date
      type
      message
    }
  }
}
"""

LIST_RECENT_ORDERS_QUERY = """
query ListRecentOrders($channel: String!, $first: Int!) {
  orders(
    filter: { channels: [$channel] }
    first: $first
    sortBy: { field: CREATION_DATE, direction: DESC }
  ) {
    edges {
      node {
        id
        number
        status
        paymentStatus
        created
        total {
          gross {
            amount
            currency
          }
        }
        userEmail
        shippingAddress {
          firstName
          lastName
          city
          country {
            code
          }
        }
      }
    }
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

TOTAL_ORDER_COUNT_QUERY = """
query GetTotalOrderCount($channel: String!) {
  orders(filter: { channels: [$channel] }, first: 1) {
    totalCount
  }
}
"""


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def get_order_status(order_id: str) -> dict[str, Any]:
    """Fetch the full status of a single order by its Saleor global ID.

    Args:
        order_id: Saleor global order ID (base64-encoded, e.g.
                  ``"T3JkZXI6MQ=="``) or the plain numeric order number
                  (Saleor will accept both formats in the ``id`` argument).

    Returns:
        Dict with keys:
            order  -- full order object (status, lines, fulfillments, events…)
            error  -- present only on failure, contains error message string
    """
    logger.debug("Fetching Saleor order status | order_id=%s", order_id)

    try:
        body = _execute_query(ORDER_STATUS_QUERY, {"orderId": order_id})
    except EnvironmentError as exc:
        return {"order": None, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor get_order_status HTTP error: %s", msg)
        return {"order": None, "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor get_order_status request error: %s", exc)
        return {"order": None, "error": str(exc)}

    if "errors" in body:
        messages = "; ".join(e.get("message", str(e)) for e in body["errors"])
        logger.error("Saleor GraphQL errors for order %s: %s", order_id, messages)
        return {"order": None, "error": messages}

    order = body.get("data", {}).get("order")
    if order is None:
        logger.warning("Saleor order not found | order_id=%s", order_id)
        return {"order": None, "error": f"Order {order_id} not found"}

    logger.info(
        "Saleor order fetched | number=%s status=%s payment=%s",
        order.get("number"),
        order.get("status"),
        order.get("paymentStatus"),
    )
    return {"order": order}


def list_recent_orders(channel: str, limit: int = 5) -> dict[str, Any]:
    """List the most recently created orders for a given channel.

    Args:
        channel: Saleor channel slug (e.g. "dash-product").
        limit:   Number of orders to return (default 5, max 50).

    Returns:
        Dict with keys:
            orders    -- list of order summary dicts
            total     -- total order count in the channel
            has_more  -- bool indicating additional pages exist
            error     -- present only on failure
    """
    limit = max(1, min(limit, 50))
    logger.debug("Listing recent Saleor orders | channel=%s limit=%d", channel, limit)

    try:
        body = _execute_query(LIST_RECENT_ORDERS_QUERY, {"channel": channel, "first": limit})
    except EnvironmentError as exc:
        return {"orders": [], "total": 0, "has_more": False, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor list_recent_orders HTTP error: %s", msg)
        return {"orders": [], "total": 0, "has_more": False, "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor list_recent_orders request error: %s", exc)
        return {"orders": [], "total": 0, "has_more": False, "error": str(exc)}

    if "errors" in body:
        messages = "; ".join(e.get("message", str(e)) for e in body["errors"])
        logger.error("Saleor GraphQL errors listing orders: %s", messages)
        return {"orders": [], "total": 0, "has_more": False, "error": messages}

    orders_connection = body.get("data", {}).get("orders", {})
    edges = orders_connection.get("edges", [])
    total = orders_connection.get("totalCount", 0)
    page_info = orders_connection.get("pageInfo", {})

    orders = [edge["node"] for edge in edges]

    logger.info(
        "Saleor orders listed | channel=%s returned=%d total=%d",
        channel,
        len(orders),
        total,
    )
    return {
        "orders": orders,
        "total": total,
        "has_more": page_info.get("hasNextPage", False),
        "end_cursor": page_info.get("endCursor"),
    }


def get_total_order_count(channel: str) -> dict[str, Any]:
    """Return the total number of orders in a Saleor channel.

    Useful for agent dashboards, analytics, and threshold-based triggers.

    Args:
        channel: Saleor channel slug.

    Returns:
        Dict with keys:
            total  -- integer total order count
            error  -- present only on failure
    """
    logger.debug("Fetching total order count | channel=%s", channel)

    try:
        body = _execute_query(TOTAL_ORDER_COUNT_QUERY, {"channel": channel})
    except EnvironmentError as exc:
        return {"total": 0, "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor get_total_order_count HTTP error: %s", msg)
        return {"total": 0, "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor get_total_order_count request error: %s", exc)
        return {"total": 0, "error": str(exc)}

    if "errors" in body:
        messages = "; ".join(e.get("message", str(e)) for e in body["errors"])
        logger.error("Saleor GraphQL errors for order count: %s", messages)
        return {"total": 0, "error": messages}

    total = body.get("data", {}).get("orders", {}).get("totalCount", 0)

    logger.info("Saleor order count | channel=%s total=%d", channel, total)
    return {"total": total}
