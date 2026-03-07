# Pauli MCP Builder
## skill_id
`mcp_builder_pauli`

## Purpose
Designs and generates production-ready MCP (Model Context Protocol) servers for the Pauli Empire stack. Specializes in connecting ARCHON-X OS agents to our actual external services: Coolify API, Vercel API, Supabase, Stripe, PayPal, GitHub, Notion, Cloudflare, and any new integrations. All MCP servers are built with security-first design (least-privilege, secret injection via Vault Agent, no hardcoded keys), Docker-ready, and deploy-ready to Coolify VPS at 31.220.58.212. Follows the mcp-builder SKILL.md patterns enhanced for our specific stack.

## When to Use
- Any new external API needs to be accessible to ARCHON-X agents
- Building the second-brain-mcp server (Supabase pgvector)
- Building the coolify-mcp server (deploy/rollback/health)
- Adding Stripe or PayPal as agent-accessible tools
- Wrapping any Akash Engine client API for agent access
- Creating sandboxed MCP servers for crypto/Web3 integrations

## Inputs
```
service_name: string
api_type: "REST" | "GraphQL" | "WebSocket" | "SDK"
auth_method: "api-key" | "oauth2" | "jwt" | "bearer"
tools_to_expose: [tool_name: string, description: string, params: {}]
deploy_target: "coolify" | "local" | "cloudflare-worker"
language: "python-fastmcp" | "node-mcp-sdk" (default: python-fastmcp)
security_level: "internal" | "client-facing" (affects permission scope)
```

## Outputs
- Complete MCP server source code (Python FastMCP or Node MCP SDK)
- Dockerfile for Coolify deployment
- `mcp-config.json` entry (copy-paste ready)
- Vault Agent secret registration instructions
- Test suite (pytest or jest)

## Tools & Integrations
- Coolify API for deploy target provisioning
- Vault Agent (archonx/vault/vault_agent.py) for secret management
- GitHub Actions template for CI/CD of the MCP server itself
- jCodeMunch Gate Zero — reads existing MCP servers before generating new ones to avoid duplication

## Project-Specific Guidelines
**Security rules (non-negotiable)**:
- All API keys injected via environment variables — NEVER in source code
- Vault Agent must register new secrets: `vault_agent.register(key_name, rotation_days)`
- Coolify-hosted MCP servers get their own Docker network, never shared with other services
- internal-level servers: only accessible from ARCHON-X network
- client-facing servers: rate-limited, logged, require request signing

**Server structure** (Python FastMCP pattern):
```python
from fastmcp import FastMCP
import os
mcp = FastMCP("service-name-mcp")
API_KEY = os.environ["SERVICE_API_KEY"]  # Always from env

@mcp.tool()
async def tool_name(param: str) -> dict:
    """Clear description of what this tool does."""
    # implementation
    pass

if __name__ == "__main__":
    mcp.run()
```
Always include health check endpoint. Always log tool calls to agent_telemetry table.

## Example Interactions
1. "Build the second-brain-mcp server for Supabase pgvector" → Full FastMCP server + Docker + config entry
2. "Create a coolify-mcp with deploy, rollback, and health_check tools" → Node MCP SDK server, Coolify API integration
3. "Build a Stripe MCP for ARCHON-X to check subscription status" → Stripe SDK wrapped in FastMCP, least-privilege (read-only)
4. "Make an MCP server for the NW Kids donation tracking API" → FastMCP + Supabase nwkids_ schema, donor privacy compliant
5. "Wrap the Cloudflare API as an MCP tool for DNS management" → CF API MCP, zone/DNS record tools only, no firewall mutation
