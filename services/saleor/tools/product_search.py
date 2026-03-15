"""
services/saleor/tools/product_search.py

Product search tool for the Saleor agentic commerce stack.

Queries the Saleor GraphQL API for products matching a search string within a
given channel. Designed to be called directly by agent tools or the SaleorAgent
wrapper.

Environment variables:
    SALEOR_API_URL  -- Full URL to the Saleor GraphQL endpoint (required)
    SALEOR_TOKEN    -- Bearer token for authenticated requests (optional for
                       public channels, required for restricted channels)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GraphQL document
# ---------------------------------------------------------------------------

PRODUCTS_QUERY = """
query SearchProducts($search: String!, $channel: String!, $first: Int!) {
  products(
    filter: { search: $search }
    channel: $channel
    first: $first
  ) {
    edges {
      node {
        id
        name
        slug
        description
        isAvailable
        pricing {
          priceRange {
            start {
              gross {
                amount
                currency
              }
            }
            stop {
              gross {
                amount
                currency
              }
            }
          }
        }
        thumbnail {
          url
          alt
        }
        category {
          id
          name
        }
        variants {
          id
          name
          sku
          quantityAvailable
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


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def search_products(
    query: str,
    channel: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for products in a Saleor channel.

    Args:
        query:   Full-text search string passed to Saleor's product filter.
        channel: Saleor channel slug (e.g. "dash-product", "blitz-people").
        limit:   Maximum number of products to return (default 10, max 100).

    Returns:
        A dict with keys:
            products   -- list of product dicts (id, name, slug, pricing, …)
            total      -- total number of matching products
            has_more   -- bool indicating additional pages exist
            error      -- present only on failure, contains error message string

    Raises:
        Does not raise — all exceptions are caught and returned in the ``error``
        key so that agent callers can handle failures gracefully.
    """
    api_url = os.getenv("SALEOR_API_URL")
    if not api_url:
        logger.error("SALEOR_API_URL is not set")
        return {"products": [], "total": 0, "has_more": False, "error": "SALEOR_API_URL environment variable is not set"}

    limit = max(1, min(limit, 100))  # clamp to [1, 100]

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    token = os.getenv("SALEOR_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "query": PRODUCTS_QUERY,
        "variables": {
            "search": query,
            "channel": channel,
            "first": limit,
        },
    }

    logger.debug(
        "Searching Saleor products | channel=%s query=%r limit=%d",
        channel,
        query,
        limit,
    )

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error("Saleor request timed out: %s", exc)
        return {"products": [], "total": 0, "has_more": False, "error": f"Request timed out: {exc}"}
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Saleor HTTP error %s: %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return {
            "products": [],
            "total": 0,
            "has_more": False,
            "error": f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
        }
    except httpx.RequestError as exc:
        logger.error("Saleor request error: %s", exc)
        return {"products": [], "total": 0, "has_more": False, "error": f"Request error: {exc}"}

    try:
        body = response.json()
    except Exception as exc:
        logger.error("Failed to parse Saleor response as JSON: %s", exc)
        return {"products": [], "total": 0, "has_more": False, "error": f"JSON parse error: {exc}"}

    if "errors" in body:
        gql_errors = body["errors"]
        messages = "; ".join(e.get("message", str(e)) for e in gql_errors)
        logger.error("Saleor GraphQL errors: %s", messages)
        return {"products": [], "total": 0, "has_more": False, "error": messages}

    data = body.get("data", {})
    products_connection = data.get("products", {})
    edges = products_connection.get("edges", [])
    total = products_connection.get("totalCount", 0)
    page_info = products_connection.get("pageInfo", {})

    products = [edge["node"] for edge in edges]

    logger.info(
        "Saleor product search complete | channel=%s query=%r found=%d total=%d",
        channel,
        query,
        len(products),
        total,
    )

    return {
        "products": products,
        "total": total,
        "has_more": page_info.get("hasNextPage", False),
        "end_cursor": page_info.get("endCursor"),
    }
