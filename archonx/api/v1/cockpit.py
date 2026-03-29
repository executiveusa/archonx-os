"""Cockpit control — remote command surface for pauli-vibe_cockpit repo."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/cockpit")


@router.get("/overview")
async def cockpit_overview(request: Request) -> JSONResponse:
    """Full system snapshot for the cockpit dashboard."""
    state = request.app.state.app_state
    kernel = state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    agents = kernel.registry.all()
    white = [a for a in agents if a.crew.value == "white"]
    black = [a for a in agents if a.crew.value == "black"]

    cost_data = None
    if kernel.cost_guard:
        agent_ids = list(kernel.cost_guard._usage.keys()) or ["kernel"]
        usages = [kernel.cost_guard.get_usage(aid) for aid in agent_ids]
        total_cents = sum(u["cost_cents"] for u in usages)
        budget_cents = kernel.cost_guard.budget.max_cost_per_day_cents
        cost_data = {
            "spent_usd": round(total_cents / 100, 2),
            "budget_usd": round(budget_cents / 100, 2),
            "remaining_pct": round(100 * max(0, budget_cents - total_cents) / max(1, budget_cents), 1),
            "circuit_breaker": total_cents >= budget_cents,
        }

    return JSONResponse({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kernel_version": "2.0.0",
        "booted": kernel._booted,
        "agents": {
            "total": len(agents),
            "white_crew": len(white),
            "black_crew": len(black),
        },
        "subsystems": {
            "hermes": kernel.hermes is not None,
            "popebot": kernel.popebot is not None,
            "cost_guard": kernel.cost_guard is not None,
            "flywheel": True,
            "theater": kernel.theater is not None,
            "revenue_engine": kernel.revenue_engine is not None,
        },
        "cost": cost_data,
        "machines": len(state.registered_machines),
        "active_tasks": len(state.task_status),
        "ws_clients": len(state.ws_clients),
    })


@router.post("/task")
async def cockpit_submit_task(body: dict[str, Any], request: Request) -> JSONResponse:
    """Submit a task from the cockpit — routes to execute_task."""
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    result = await kernel.execute_task(body)
    return JSONResponse(result)


@router.post("/hermes/council")
async def cockpit_hermes_council(
    body: dict[str, Any], request: Request
) -> JSONResponse:
    """Run a Hermes council session from the cockpit."""
    kernel = request.app.state.app_state.kernel
    if kernel is None or kernel.hermes is None:
        return JSONResponse({"error": "hermes not available"}, status_code=503)

    question = body.get("question", "")
    if not question:
        return JSONResponse({"error": "question required"}, status_code=400)

    result = kernel.hermes.white_council.challenge(question)
    return JSONResponse({"council_result": result})


@router.post("/popebot/send")
async def cockpit_popebot_send(
    body: dict[str, Any], request: Request
) -> JSONResponse:
    """Send a message through Popebot from the cockpit."""
    kernel = request.app.state.app_state.kernel
    if kernel is None or kernel.popebot is None:
        return JSONResponse({"error": "popebot not available"}, status_code=503)

    channel = body.get("channel", "email")
    agent_name = body.get("agent", "pauli")
    message = body.get("message", "")
    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)

    result = await kernel.popebot.send(channel=channel, agent_name=agent_name, message=message)
    return JSONResponse({"sent": True, "channel": channel, "result": result})


@router.get("/souls")
async def cockpit_list_souls(request: Request) -> JSONResponse:
    """List all loaded agent souls."""
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    souls = kernel.soul_loader.registry
    return JSONResponse({
        "souls": [
            {"agent_id": sid, "name": s.get("name", sid), "crew": s.get("crew", "unknown")}
            for sid, s in souls.items()
        ],
        "count": len(souls),
    })


@router.get("/revenue")
async def cockpit_revenue(request: Request) -> JSONResponse:
    """Get revenue engine status."""
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    return JSONResponse({
        "engine": "active" if kernel.revenue_engine else "inactive",
        "kpi_dashboard": kernel.kpi_dashboard is not None,
    })
