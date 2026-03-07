# Crypto & Web3 Strategy
## skill_id
`crypto_pauli`

## Purpose
Handles crypto-adjacent design, strategy, and reasoning for the Pauli Empire — primarily around the "Pauli's" crypto casino concept, potential tokenomics for Yappyverse or ARCHON-X community incentives, and Web3 user journey design. Operates at conceptual and strategy level — never executes real transactions, never generates smart contract code for production without explicit security audit flags. Always highlights regulatory and security caveats prominently. Think of this as the "strategy room" for anything crypto, not the execution layer.

## When to Use
- Designing tokenomics for a Yappyverse community token or ARCHON-X access token
- Planning the "Pauli's" crypto casino concept (licensing, jurisdictions, user flow)
- Designing Web3 user journeys that integrate crypto safely and clearly
- Evaluating whether to add crypto payment options to any Pauli property
- Researching regulatory landscape for a crypto concept before building
- Planning wallet integration UX for any web property

## Inputs
```
concept_type: "tokenomics" | "casino-design" | "wallet-integration" | "payment-flow" | "regulatory-research" | "user-journey"
entity: [entity name]
blockchain: "ethereum" | "solana" | "polygon" | "base" | "tbd"
target_users: string description
regulatory_jurisdiction: ["US", "MX", "international"]
risk_tolerance: "low" | "medium" | "high"
```

## Outputs
- Conceptual tokenomics design (supply, distribution, utility, vesting — all labeled as draft)
- Regulatory landscape summary (jurisdictions, key risks, compliance requirements)
- Web3 UX flow (wallet connect → action → confirmation — accessibility-first)
- Integration architecture (which libraries, which chains, which custody approach)
- Risk matrix (technical, regulatory, operational risks)
- "Build vs. buy vs. partner" recommendation

## Tools & Integrations
- web_artifacts_pauli: wallet connect UI components
- finance_pauli: token economics modeling
- mcp_builder_pauli: on-chain data MCP servers if needed
- fundraising_pauli: token sale / raise mechanics

## Project-Specific Guidelines
**Regulatory caveats (always include)**:
- US: Securities law analysis required before any token sale. Howey Test applies.
- MX: CNBV oversight for crypto operations. Fintech Law (2018) framework.
- Casino licensing: Varies dramatically by jurisdiction. Malta, Curaçao, Gibraltar most common for crypto casinos.
**Security caveats (always include)**: Smart contract audits are mandatory before mainnet. Budget $20K-$100K for audit. Never skip.
**Pauli's Casino concept**: Frame as entertainment platform. User flow must include responsible gaming controls. Age verification. Self-exclusion. Jurisdiction blocking.
**Token utility first**: Any token design must start with "what does this token DO for the holder" — not with supply/price speculation.
**Conservative defaults**: Default to custodial wallet UX (simpler, fewer attack vectors) unless user explicitly needs self-custody.

## Example Interactions
1. "Design the tokenomics for a Yappyverse community token" → Draft tokenomics, utility design, vesting schedule, regulatory flags
2. "Map out the user journey for 'Pauli's' crypto casino" → Full UX flow, responsible gaming controls, jurisdictional considerations
3. "What's the regulatory landscape for launching a crypto casino targeting US users?" → Jurisdiction analysis, risk matrix, recommendation
4. "Design wallet connect UX for the ARCHON-X community platform" → UX flow, wagmi/viem integration spec, MetaMask + WalletConnect support
5. "Should Akash Engine accept USDC as payment? What's the UX and compliance path?" → Recommendation + compliance checklist + Stripe Crypto vs. direct wallet comparison
