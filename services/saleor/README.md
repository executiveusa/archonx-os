# Saleor — ArchonX Default Ecommerce Stack

## What Is Saleor?

Saleor is a GraphQL-first, open-source headless ecommerce platform. Everything
in Saleor is exposed through a single, strongly-typed GraphQL API — products,
orders, checkouts, customers, payments, channels, and fulfilment. There is no
legacy REST surface to work around. The schema is the contract.

Key characteristics:

- GraphQL-native — every operation (query, mutation, subscription) speaks GraphQL
- Multi-channel — a single instance serves multiple storefronts, marketplaces, or
  agent contexts through isolated channel slugs
- Webhook-driven — every state change (order created, payment captured, stock
  updated) emits a structured webhook payload that downstream systems can react to
- Open-source (BSD-2) — self-hostable or available as Saleor Cloud

---

## Why Saleor Is the ArchonX Choice

| Property | Why It Matters for Agents |
|---|---|
| API-first GraphQL | Agents consume the API directly — no scraping, no UI automation |
| Multi-channel | Each agent crew or product line gets its own channel slug |
| Webhook-driven events | Agents subscribe to events and react autonomously |
| Strong schema typing | LLMs can introspect the schema and generate valid queries |
| No monolithic frontend | Nothing to bypass — agents are first-class API consumers |
| Fine-grained permissions | Service accounts scoped per agent team |

---

## The Agentic Commerce Thesis

Traditional ecommerce assumes a human sitting in front of a browser. ArchonX
inverts this. In an agentic commerce architecture:

1. **Agents are the storefront.** There is no React/Next.js frontend required for
   agent-driven purchasing flows. An agent calls `checkout_create`, then
   `checkoutShippingAddressUpdate`, then `checkoutComplete` — the same mutations a
   human-facing storefront would call, but programmatically and at machine speed.

2. **GraphQL is the universal interface.** Because Saleor's entire surface is
   GraphQL, any agent that can construct a JSON payload can participate in commerce
   without custom adapters.

3. **Webhooks close the loop.** After an order is placed the agent subscribes to
   `ORDER_UPDATED`, `FULFILLMENT_CREATED`, and `INVOICE_SENT` webhooks to track
   lifecycle events autonomously — no polling required.

4. **Multi-channel = multi-agent.** Each knight crew operates in its own Saleor
   channel, meaning pricing rules, stock rules, and payment methods can be tuned
   per department without interference.

---

## Knight Assignments (4 Departments)

| Knight | Department | Saleor Channel Slug (suggested) |
|---|---|---|
| Blitz | People Department | `blitz-people` |
| Patch | Process Department | `patch-process` |
| Dash | Product Department | `dash-product` |
| Stitch | Gratitude / BENEVOLENCIA | `stitch-benevolencia` |

Each knight has a dedicated Saleor service account token stored in the secrets
vault and injected at runtime. Cross-channel queries are reserved for
orchestrator-level agents only.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SALEOR_API_URL` | Full URL to the Saleor GraphQL endpoint, e.g. `https://store.example.com/graphql/` |
| `SALEOR_TOKEN` | Bearer token for authenticated mutations (service account) |

Minimum required: `SALEOR_API_URL`.

For authenticated operations (checkout, order management) `SALEOR_TOKEN` must
also be present. Tokens are issued per-channel service account in the Saleor
Dashboard under **Settings → Service Accounts**.

---

## Directory Layout

```
services/saleor/
├── README.md               # This file
├── agents/
│   ├── __init__.py
│   └── saleor_agent.py     # BaseSkill-compatible agent wrapper
├── data/
│   └── stack_entry.json    # Stack registry entry
└── tools/
    ├── __init__.py
    ├── checkout_flow.py    # Checkout lifecycle mutations
    ├── order_management.py # Order query helpers
    └── product_search.py   # Product search query helper
```

---

## Quick Start

```bash
export SALEOR_API_URL="https://your-saleor-instance.saleor.cloud/graphql/"
export SALEOR_TOKEN="your-service-account-token"

python - <<'EOF'
from services.saleor.tools.product_search import search_products
results = search_products(query="shirt", channel="dash-product", limit=5)
for p in results.get("products", []):
    print(p["name"], p["id"])
EOF
```
