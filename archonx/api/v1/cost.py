"""CostGuard budget endpoints — Emerald Tablets compliance."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/cost")


@router.get("")
async def get_cost_summary(request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    if kernel.cost_guard is None:
        return JSONResponse({"error": "cost_guard disabled"}, status_code=404)

    guard = kernel.cost_guard
    budget = guard.budget
    agent_ids = list(guard._usage.keys()) or ["kernel"]
    agents_usage = [guard.get_usage(aid) for aid in agent_ids]

    total_cost_cents = sum(u["cost_cents"] for u in agents_usage)
    total_actions = sum(u["actions_this_hour"] for u in agents_usage)
    budget_cents = budget.max_cost_per_day_cents

    return JSONResponse({
        "total_cost_usd": round(total_cost_cents / 100, 2),
        "budget_usd": round(budget_cents / 100, 2),
        "remaining_usd": round(max(0, budget_cents - total_cost_cents) / 100, 2),
        "budget_used_pct": round(100 * total_cost_cents / max(1, budget_cents), 1),
        "total_actions_this_hour": total_actions,
        "alert_threshold_pct": budget.alert_threshold_percent,
        "circuit_breaker_active": total_cost_cents >= budget_cents,
        "fallback_model": "qwen" if total_cost_cents >= budget_cents else None,
        "agents": agents_usage,
    })


@router.post("/reset")
async def reset_cost(body: dict[str, Any], request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    if kernel.cost_guard is None:
        return JSONResponse({"error": "cost_guard disabled"}, status_code=404)

    agent_id = body.get("agent_id", "")
    if not agent_id:
        return JSONResponse({"error": "agent_id required"}, status_code=400)
    kernel.cost_guard.reset(agent_id)
    return JSONResponse({"reset": True, "agent_id": agent_id})
