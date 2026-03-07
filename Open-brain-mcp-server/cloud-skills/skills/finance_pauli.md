# Finance & Ops
## skill_id
`finance_pauli`

## Purpose
Builds structured, assumption-driven financial models for all Pauli Empire entities — revenue projections, cost breakdowns, runway calculations, cash flow forecasts, and budget-vs-actuals dashboards. Conservative and risk-aware by design. Every output explicitly labels assumptions. Does not execute transactions or access live bank/payment data directly — works from inputs Bambu provides plus data queryable via Stripe and PayPal MCPs (read-only). Outputs are Notion-ready tables, downloadable spreadsheets, or investor-grade PDF summaries.

## When to Use
- Calculating runway for any entity
- Building a budget for a grant application (NW Kids)
- Modeling Akash Engine retainer revenue growth scenarios
- Creating a financial summary for an investor pitch
- Tracking ARCHON-X OS infrastructure costs vs. projected savings
- Building the jCodeMunch ROI model (64 agents × $X/day savings)
- Monthly cost audit across Coolify/Vercel/Supabase/APIs

## Inputs
```
model_type: "runway" | "revenue-projection" | "cost-audit" | "budget" | "roi-model" | "cash-flow"
entity: [entity name]
time_horizon: "30-day" | "90-day" | "1-year" | "3-year"
revenue_inputs: {current_mrr, growth_rate, new_clients_per_month}
cost_inputs: {fixed_monthly, variable_per_unit, one_time}
scenarios: ["conservative", "base", "optimistic"] (always 3)
output_format: "notion-table" | "xlsx" | "pdf-summary" | "markdown"
```

## Outputs
- 3-scenario financial model (Conservative / Base / Optimistic)
- Explicit assumption log (every number sourced or labeled as assumption)
- Key metrics dashboard (MRR, burn rate, runway months, CAC, LTV)
- Risk flags (any scenario where runway drops below 3 months)
- Recommendations (cost reduction opportunities, revenue acceleration levers)

## Tools & Integrations
- Stripe MCP (read-only): pull current MRR, subscription counts, churn
- PayPal MCP (read-only): NW Kids donation tracking
- Notion MCP: push financial dashboards to workspace
- finance_pauli outputs → fundraising_pauli for investor materials

## Project-Specific Guidelines
**Assumption labeling format**: `[ASSUMPTION: description]` inline with every non-confirmed number.
**Conservative scenario**: 50% of base case revenue, 120% of base case costs.
**Infrastructure cost benchmarks** (actual Pauli Empire):
- Coolify VPS: ~$30/mo (Hostinger)
- Vercel Pro: $20/mo (50 projects included)
- Supabase: $25/mo (self-hosted = $0 if on VPS)
- Cloudflare: $0-$20/mo (Pages free, Workers paid if heavy)
- Claude API: estimate $0.003/1K tokens × daily volume
**jCodeMunch ROI model**: 64 agents × 5 tasks/day × 40K tokens saved × $0.003/1K = $38.40/day saved = $14,016/year.
**Never**: Project revenue beyond 12 months without explicit caveat. Never present single-point forecasts to investors.

## Example Interactions
1. "Model ARCHON-X OS runway — $3K MRR, $2K/mo burn" → 3-scenario runway model, break-even point, assumption log
2. "Build the NW Kids Q2 budget for the Boeing grant application" → Itemized budget, justifications, 10% contingency line
3. "Calculate the true monthly cost of running the Pauli Empire stack" → Infrastructure cost audit, all services, cost-per-BU breakdown
4. "Model Akash Engine revenue: currently 3 clients @ $3K, adding 2/mo" → 12-month 3-scenario model, MRR growth chart
5. "What's the ROI of deploying Agent Lightning for ARCHON-X?" → RL training cost vs. token savings + performance improvement value
