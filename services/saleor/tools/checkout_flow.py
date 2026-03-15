"""
services/saleor/tools/checkout_flow.py

Checkout lifecycle tools for the Saleor agentic commerce stack.

Covers the three-stage checkout flow used by agent-driven purchasing:

    1. create_checkout          -- initialise a checkout with line items
    2. add_shipping_address     -- attach a shipping address to the checkout
    3. complete_checkout        -- finalise payment and convert to an order

All functions communicate with Saleor via GraphQL mutations over httpx.

Environment variables:
    SALEOR_API_URL  -- Full URL to the Saleor GraphQL endpoint (required)
    SALEOR_TOKEN    -- Bearer token for authenticated requests (required for
                       protected channels / payment operations)
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


def _execute_mutation(mutation: str, variables: dict[str, Any]) -> dict[str, Any]:
    """POST a GraphQL mutation to Saleor and return the parsed response body.

    Returns the full parsed JSON body. Callers are responsible for extracting
    the relevant ``data`` keys and inspecting ``errors``.

    Raises:
        EnvironmentError: if SALEOR_API_URL is not configured.
        httpx.HTTPStatusError: on 4xx/5xx responses.
        httpx.RequestError: on network-level failures.
    """
    api_url = _get_api_url()
    headers = _build_headers()
    payload = {"query": mutation, "variables": variables}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

    return response.json()


def _extract_errors(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect top-level GraphQL errors and inline mutation errors."""
    errors: list[dict[str, Any]] = []
    if "errors" in body:
        errors.extend(body["errors"])
    return errors


# ---------------------------------------------------------------------------
# GraphQL mutations
# ---------------------------------------------------------------------------

CHECKOUT_CREATE_MUTATION = """
mutation CheckoutCreate($channel: String!, $lines: [CheckoutLineInput!]!) {
  checkoutCreate(input: { channel: $channel, lines: $lines }) {
    checkout {
      id
      token
      email
      totalPrice {
        gross {
          amount
          currency
        }
      }
      lines {
        id
        quantity
        variant {
          id
          name
          sku
        }
        totalPrice {
          gross {
            amount
            currency
          }
        }
      }
      shippingAddress {
        firstName
        lastName
        streetAddress1
        city
        country {
          code
        }
      }
      availableShippingMethods {
        id
        name
        price {
          amount
          currency
        }
      }
    }
    errors {
      field
      message
      code
    }
  }
}
"""

SHIPPING_ADDRESS_UPDATE_MUTATION = """
mutation CheckoutShippingAddressUpdate(
  $checkoutId: ID!
  $shippingAddress: AddressInput!
) {
  checkoutShippingAddressUpdate(
    id: $checkoutId
    shippingAddress: $shippingAddress
  ) {
    checkout {
      id
      token
      shippingAddress {
        firstName
        lastName
        streetAddress1
        streetAddress2
        city
        postalCode
        country {
          code
        }
        phone
      }
      availableShippingMethods {
        id
        name
        price {
          amount
          currency
        }
      }
    }
    errors {
      field
      message
      code
    }
  }
}
"""

CHECKOUT_COMPLETE_MUTATION = """
mutation CheckoutComplete(
  $checkoutId: ID!
  $paymentData: JSONString
  $storeSource: Boolean
  $redirectUrl: String
) {
  checkoutComplete(
    id: $checkoutId
    paymentData: $paymentData
    storeSource: $storeSource
    redirectUrl: $redirectUrl
  ) {
    order {
      id
      number
      status
      total {
        gross {
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
        }
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
    }
    confirmationNeeded
    confirmationData
    errors {
      field
      message
      code
    }
  }
}
"""


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def create_checkout(channel: str, lines: list[dict[str, Any]]) -> dict[str, Any]:
    """Initialise a Saleor checkout with one or more line items.

    Args:
        channel: Saleor channel slug (e.g. "dash-product").
        lines:   List of dicts with keys ``variantId`` (str) and ``quantity``
                 (int). Example::

                     [{"variantId": "UHJvZHVjdFZhcmlhbnQ6MQ==", "quantity": 2}]

    Returns:
        Dict with keys:
            checkout  -- checkout object from Saleor (id, token, lines, …)
            errors    -- list of error objects (empty on success)
            error     -- top-level error string (present only on failure)
    """
    logger.debug("Creating Saleor checkout | channel=%s lines=%d", channel, len(lines))

    # Saleor expects CheckoutLineInput: { variantId, quantity }
    formatted_lines = [
        {"variantId": line["variantId"], "quantity": int(line["quantity"])}
        for line in lines
    ]

    try:
        body = _execute_mutation(
            CHECKOUT_CREATE_MUTATION,
            {"channel": channel, "lines": formatted_lines},
        )
    except EnvironmentError as exc:
        return {"checkout": None, "errors": [], "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor checkout create HTTP error: %s", msg)
        return {"checkout": None, "errors": [], "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor checkout create request error: %s", exc)
        return {"checkout": None, "errors": [], "error": str(exc)}

    top_errors = _extract_errors(body)
    mutation_data = body.get("data", {}).get("checkoutCreate", {})
    inline_errors = mutation_data.get("errors", [])
    all_errors = top_errors + inline_errors

    checkout = mutation_data.get("checkout")

    if all_errors:
        logger.warning("Saleor checkoutCreate errors: %s", all_errors)
    else:
        logger.info("Saleor checkout created | id=%s", checkout.get("id") if checkout else "N/A")

    return {"checkout": checkout, "errors": all_errors}


def add_shipping_address(checkout_id: str, address: dict[str, Any]) -> dict[str, Any]:
    """Attach a shipping address to an existing Saleor checkout.

    Args:
        checkout_id: The Saleor checkout ``id`` returned by ``create_checkout``.
        address:     Dict conforming to Saleor's ``AddressInput`` type. Keys:
                     firstName, lastName, streetAddress1, streetAddress2 (opt),
                     city, postalCode, country (2-letter ISO code), phone (opt).

                     Example::

                         {
                             "firstName": "Ada",
                             "lastName": "Lovelace",
                             "streetAddress1": "1 Infinite Loop",
                             "city": "San Francisco",
                             "postalCode": "94102",
                             "country": "US",
                         }

    Returns:
        Dict with keys:
            checkout  -- updated checkout object
            errors    -- list of error objects (empty on success)
            error     -- top-level error string (present only on failure)
    """
    logger.debug("Adding shipping address to checkout | checkout_id=%s", checkout_id)

    try:
        body = _execute_mutation(
            SHIPPING_ADDRESS_UPDATE_MUTATION,
            {"checkoutId": checkout_id, "shippingAddress": address},
        )
    except EnvironmentError as exc:
        return {"checkout": None, "errors": [], "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor shipping address update HTTP error: %s", msg)
        return {"checkout": None, "errors": [], "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor shipping address update request error: %s", exc)
        return {"checkout": None, "errors": [], "error": str(exc)}

    top_errors = _extract_errors(body)
    mutation_data = body.get("data", {}).get("checkoutShippingAddressUpdate", {})
    inline_errors = mutation_data.get("errors", [])
    all_errors = top_errors + inline_errors

    checkout = mutation_data.get("checkout")

    if all_errors:
        logger.warning("Saleor checkoutShippingAddressUpdate errors: %s", all_errors)
    else:
        logger.info("Shipping address updated | checkout_id=%s", checkout_id)

    return {"checkout": checkout, "errors": all_errors}


def complete_checkout(checkout_id: str, payment_data: dict[str, Any]) -> dict[str, Any]:
    """Finalise a Saleor checkout and convert it into an order.

    This mutation confirms payment intent and creates the order record. For
    Saleor payment gateways that require client-side tokenisation the
    ``payment_data`` dict is serialised to a JSON string and passed as the
    ``paymentData`` argument.

    Args:
        checkout_id:  The Saleor checkout ``id``.
        payment_data: Gateway-specific payment payload. For stripe-like flows:
                      ``{"token": "tok_visa"}``. For dummy gateway testing:
                      ``{}``.

    Returns:
        Dict with keys:
            order                -- created order object (id, number, status, …)
            confirmation_needed  -- bool; True if 3DS/additional step required
            confirmation_data    -- opaque data for the confirmation step
            errors               -- list of error objects (empty on success)
            error                -- top-level error string (present only on failure)
    """
    import json

    logger.debug("Completing Saleor checkout | checkout_id=%s", checkout_id)

    try:
        body = _execute_mutation(
            CHECKOUT_COMPLETE_MUTATION,
            {
                "checkoutId": checkout_id,
                "paymentData": json.dumps(payment_data) if payment_data else None,
                "storeSource": False,
            },
        )
    except EnvironmentError as exc:
        return {"order": None, "confirmation_needed": False, "confirmation_data": None, "errors": [], "error": str(exc)}
    except httpx.HTTPStatusError as exc:
        msg = f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        logger.error("Saleor checkout complete HTTP error: %s", msg)
        return {"order": None, "confirmation_needed": False, "confirmation_data": None, "errors": [], "error": msg}
    except httpx.RequestError as exc:
        logger.error("Saleor checkout complete request error: %s", exc)
        return {"order": None, "confirmation_needed": False, "confirmation_data": None, "errors": [], "error": str(exc)}

    top_errors = _extract_errors(body)
    mutation_data = body.get("data", {}).get("checkoutComplete", {})
    inline_errors = mutation_data.get("errors", [])
    all_errors = top_errors + inline_errors

    order = mutation_data.get("order")
    confirmation_needed = mutation_data.get("confirmationNeeded", False)
    confirmation_data = mutation_data.get("confirmationData")

    if all_errors:
        logger.warning("Saleor checkoutComplete errors: %s", all_errors)
    elif order:
        logger.info(
            "Saleor order created | order_id=%s number=%s status=%s",
            order.get("id"),
            order.get("number"),
            order.get("status"),
        )

    return {
        "order": order,
        "confirmation_needed": confirmation_needed,
        "confirmation_data": confirmation_data,
        "errors": all_errors,
    }
