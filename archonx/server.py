"""
ArchonX FastAPI Server
======================
WebSocket + REST API for the visualization frontend.
Serves:
    - /api/board       — Chessboard state
    - /api/dashboard   — Metrics dashboard
    - /api/meetings    — Pauli's Place scene
    - /ws              — Real-time WebSocket updates
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx

from archonx.kernel import ArchonXKernel
from archonx.core.metrics import Leaderboard
from archonx.onboarding.voice_agent.runner import OnboardingVoiceRunner
from archonx.visualization.chessboard import ChessboardView
from archonx.visualization.dashboard import MetricsDashboard
from archonx.visualization.paulis_place_view import PaulisPlaceView
from archonx.orchestration.orchestrator import Orchestrator, TaskType
from archonx.monitoring.metrics import metrics

logger = logging.getLogger("archonx.server")
_PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

# ---------------------------------------------------------------------------
# Globals (populated at startup)
# ---------------------------------------------------------------------------
_kernel: ArchonXKernel | None = None
_chessboard: ChessboardView | None = None
_dashboard: MetricsDashboard | None = None
_paulis_view: PaulisPlaceView | None = None
_leaderboard: Leaderboard | None = None
_ws_clients: set[WebSocket] = set()
_task_status: dict[str, dict[str, Any]] = {}
_registered_machines: dict[str, dict[str, Any]] = {}


class TaskWebhookPayload(BaseModel):
    message: str
    source: str = "webhook"
    priority: str = "normal"
    repo: str = ""
    environment: str = "staging"
    metadata: dict[str, Any] = Field(default_factory=dict)


def _parse_allowed_origins() -> list[str]:
    raw = os.getenv(
        "ARCHONX_ALLOWED_ORIGINS",
        "http://localhost:8080,http://localhost:5173,http://localhost:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _kernel, _chessboard, _dashboard, _paulis_view, _leaderboard

    # Boot kernel
    _kernel = ArchonXKernel()
    await _kernel.boot()

    # Build visualization state
    _leaderboard = Leaderboard()
    _chessboard = ChessboardView(_kernel.registry)
    _dashboard = MetricsDashboard(_kernel.registry, _leaderboard)
    _paulis_view = PaulisPlaceView()

    logger.info("Server ready — visualization live.")
    yield

    # Shutdown
    await _kernel.shutdown()
    logger.info("Server shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ArchonX OS",
        description="64-agent dual-crew AI operating system",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_allowed_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_api_token(request: Request, call_next):  # type: ignore[no-redef]
        token = os.getenv("ARCHONX_API_TOKEN", "").strip()
        if token and request.url.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            auth_header = request.headers.get("authorization", "")
            expected = f"Bearer {token}"
            if auth_header != expected:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

    # ----- REST endpoints -----

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({
            "status": "ok",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": "operational" if _kernel is not None else "booting",
        })

    @app.post("/webhook/task")
    async def create_task_webhook(payload: TaskWebhookPayload) -> JSONResponse:
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        result = await orchestrator.create_task(
            title=payload.message[:120],
            task_type=TaskType.CODE,
            priority=payload.priority,
            metadata={
                "source": payload.source,
                "repo": payload.repo,
                "environment": payload.environment,
                **payload.metadata,
            },
        )

        if not result.success:
            return JSONResponse({"status": "error", "message": result.message}, status_code=400)

        task_id = str(result.data.get("task_id", ""))
        _task_status[task_id] = {
            "status": "accepted",
            "task_id": task_id,
            "bead_id": f"ZTE-{task_id}",
            "source": payload.source,
            "environment": payload.environment,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        async def _progress_tracker() -> None:
            _task_status[task_id]["status"] = "queued"
            _task_status[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            await asyncio.sleep(0)
            _task_status[task_id]["status"] = "complete"
            _task_status[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

        asyncio.create_task(_progress_tracker())

        return JSONResponse({
            "status": "accepted",
            "task_id": task_id,
            "bead_id": f"ZTE-{task_id}",
            "message": "Task queued for autonomous execution",
        })

    @app.get("/status/{task_id}")
    async def task_status(task_id: str) -> JSONResponse:
        data = _task_status.get(task_id)
        if not data:
            return JSONResponse({"status": "not_found", "task_id": task_id}, status_code=404)
        return JSONResponse(data)

    @app.get("/api/board")
    async def get_board() -> JSONResponse:
        if _chessboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_chessboard.to_dict())

    @app.get("/api/dashboard")
    async def get_dashboard() -> JSONResponse:
        if _dashboard is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_dashboard.to_dict())

    @app.get("/api/meetings")
    async def get_meetings() -> JSONResponse:
        if _paulis_view is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_paulis_view.to_dict())

    @app.get("/api/agents")
    async def get_agents() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        agents = [
            {
                "id": a.agent_id,
                "name": a.name,
                "crew": a.crew.value,
                "role": a.role.value,
                "position": a.position,
                "specialty": a.specialty,
                "status": a.status.value,
                "health": a.health,
                "tasks": a.tasks_completed,
                "score": a.score,
            }
            for a in _kernel.registry.all()
        ]
        return JSONResponse({"agents": agents, "count": len(agents)})

    @app.post("/api/task")
    async def submit_task(task: dict[str, Any]) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        result = await _kernel.execute_task(task)
        # Emit to theater
        _kernel.theater.emit(
            "task_complete", "", "kernel", f"Task completed: {task.get('type', 'unknown')}",
            data=result,
        )
        # Broadcast update to all WS clients
        await _broadcast({"event": "task_result", "data": result})
        return JSONResponse(result)

    @app.get("/api/stats")
    async def get_stats() -> JSONResponse:
        return JSONResponse(metrics.get_summary())

    # ----- CostGuard endpoints (Emerald Tablets compliance) -----

    @app.get("/api/cost")
    async def get_cost_summary() -> JSONResponse:
        """Return current cost/budget status for all agents + global totals."""
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        if _kernel.cost_guard is None:
            return JSONResponse({"error": "cost_guard disabled"}, status_code=404)

        guard = _kernel.cost_guard
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

    @app.post("/api/cost/reset")
    async def reset_cost(body: dict[str, Any]) -> JSONResponse:
        """Reset cost tracking for an agent. Requires human approval context."""
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        if _kernel.cost_guard is None:
            return JSONResponse({"error": "cost_guard disabled"}, status_code=404)

        agent_id = body.get("agent_id", "")
        if not agent_id:
            return JSONResponse({"error": "agent_id required"}, status_code=400)
        _kernel.cost_guard.reset(agent_id)
        return JSONResponse({"reset": True, "agent_id": agent_id})

    # ----- Theater endpoints -----

    @app.get("/api/theater/events")
    async def get_theater_events(limit: int = 50) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        events = _kernel.theater.get_recent_events(limit)
        return JSONResponse({
            "events": [
                {
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "agent": e.agent_name,
                    "description": e.description,
                    "crew": e.crew,
                }
                for e in events
            ],
            "stats": _kernel.theater.stats,
        })

    @app.post("/api/theater/session")
    async def start_theater_session(body: dict[str, Any]) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        viewer_id = body.get("viewer_id", "anonymous")
        session = _kernel.theater.start_session(viewer_id)
        return JSONResponse({"session_id": session.session_id, "viewer_id": viewer_id})

    @app.delete("/api/theater/session/{session_id}")
    async def end_theater_session(session_id: str) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        session = _kernel.theater.end_session(session_id)
        if not session:
            return JSONResponse({"error": "session not found"}, status_code=404)
        return JSONResponse({
            "session_id": session.session_id,
            "tokens_spent": session.tokens_spent,
            "events_watched": session.events_watched,
        })

    # ----- Flywheel + Billing endpoints -----

    @app.get("/api/flywheel")
    async def get_flywheel_stats() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse(_kernel.flywheel.stats)

    @app.get("/api/billing/{user_id}")
    async def get_billing(user_id: str) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        return JSONResponse({
            "user_id": user_id,
            "balance": _kernel.billing.balance(user_id),
            "history": [
                {"id": t.id, "amount": t.amount, "source": t.source, "description": t.description}
                for t in _kernel.billing.history(user_id)
            ],
        })

    @app.get("/api/skills")
    async def list_skills() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        skills = _kernel.skill_registry.list_skills()
        return JSONResponse({
            "skills": [
                {"name": s.name, "description": s.description, "category": s.category.value}
                for s in skills
            ],
            "count": len(skills),
        })

    @app.get("/api/tools")
    async def list_tools() -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)
        tools = _kernel.tools.list_tools()
        return JSONResponse({"tools": tools})

    @app.post("/api/onboarding/run")
    async def run_onboarding(body: dict[str, Any]) -> JSONResponse:
        if _kernel is None:
            return JSONResponse({"error": "not ready"}, status_code=503)

        org_id = str(body.get("org_id", "default-org"))
        project_id = str(body.get("project_id", "default-project"))
        transcript = str(body.get("transcript", "")).strip()

        runner = OnboardingVoiceRunner()
        transcript_text = transcript or runner.load_transcript()
        result = await runner.run_plan(
            executor=_kernel.execute_task,
            transcript_text=transcript_text,
            org_id=org_id,
            project_id=project_id,
        )
        return JSONResponse(result)

    # ----- ConX Layer endpoints -----

    @app.get("/conx/status")
    async def conx_status() -> JSONResponse:
        """Get status of all registered machines."""
        machines = []
        for machine_id, machine_data in _registered_machines.items():
            machines.append({
                "machine_id": machine_id,
                **machine_data,
            })
        return JSONResponse({
            "machines": machines,
            "total": len(machines),
        })

    @app.post("/conx/register")
    async def conx_register(body: dict[str, Any]) -> JSONResponse:
        """Register a machine with the ConX layer."""
        hostname = body.get("hostname", "unknown")
        tunnel_url = body.get("tunnel_url", "")
        os_name = body.get("os", "unknown")
        mcp_servers = body.get("mcp_servers", [])

        if not tunnel_url:
            return JSONResponse(
                {"error": "tunnel_url required"},
                status_code=400,
            )

        # Generate machine ID
        machine_id = f"{hostname}-{datetime.now(timezone.utc).timestamp()}"

        # Store machine registration
        _registered_machines[machine_id] = {
            "hostname": hostname,
            "tunnel_url": tunnel_url,
            "os": os_name,
            "mcp_servers_wired": mcp_servers,
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

        return JSONResponse({
            "registered": True,
            "machine_id": machine_id,
        })

    @app.delete("/conx/register/{machine_id}")
    async def conx_deregister(machine_id: str) -> JSONResponse:
        """Deregister a machine from the ConX layer."""
        if machine_id in _registered_machines:
            del _registered_machines[machine_id]
            return JSONResponse({"deregistered": True})
        return JSONResponse(
            {"error": "machine not found"},
            status_code=404,
        )

    @app.get("/conx/machines")
    async def conx_machines() -> JSONResponse:
        """Get all registered machines with health status."""
        machines = []
        for machine_id, machine_data in _registered_machines.items():
            # Check tunnel health if possible
            health_status = "unknown"
            try:
                tunnel_url = machine_data.get("tunnel_url", "")
                if tunnel_url:
                    async with httpx.AsyncClient() as client:
                        try:
                            response = await client.get(
                                f"{tunnel_url}/health",
                                timeout=5.0,
                            )
                            health_status = "alive" if response.status_code == 200 else "offline"
                        except Exception:
                            health_status = "offline"
            except Exception:
                pass

            machines.append({
                "machine_id": machine_id,
                "health": health_status,
                **machine_data,
            })
        return JSONResponse({
            "machines": machines,
            "total": len(machines),
        })

    @app.post("/conx/launch")
    async def conx_launch(body: dict[str, Any]) -> JSONResponse:
        """Launch a task on a specific machine."""
        machine_id = body.get("machine_id", "")
        task = body.get("task", "")
        agent = body.get("agent", "")

        if not machine_id or not task:
            return JSONResponse(
                {"error": "machine_id and task required"},
                status_code=400,
            )

        if machine_id not in _registered_machines:
            return JSONResponse(
                {"error": "machine not found"},
                status_code=404,
            )

        machine = _registered_machines[machine_id]

        # Generate task ID
        task_id = f"CONX-{datetime.now(timezone.utc).timestamp()}"

        # Store task status
        _task_status[task_id] = {
            "status": "queued",
            "task_id": task_id,
            "machine_id": machine_id,
            "agent": agent,
            "tunnel_url": machine.get("tunnel_url"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Try to route to machine via tunnel
        tunnel_url = machine.get("tunnel_url", "")
        if tunnel_url and agent != "orgo":
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{tunnel_url}/webhook/task",
                        json={"message": task, "source": "conx"},
                        timeout=10.0,
                    )
                _task_status[task_id]["status"] = "sent"
            except Exception as e:
                logger.error(f"Failed to route to machine: {e}")
                _task_status[task_id]["status"] = "error"
                _task_status[task_id]["error"] = str(e)

        return JSONResponse({
            "task_id": task_id,
            "status": _task_status[task_id]["status"],
        })

    # ----- CLI-Anything endpoints -----

    @app.get("/api/skills/cli-anything")
    async def list_cli_skills() -> JSONResponse:
        """List all available CLI-Anything skills across network."""
        try:
            from archonx.skills.cli_anything.registry import CLIRegistry

            registry = CLIRegistry()
            skills = registry.get_all()

            return JSONResponse({
                "skills": skills,
                "total_apps": len(skills),
                "local_machine": True,
            })
        except ImportError:
            return JSONResponse({
                "error": "CLI-Anything module not available",
                "skills": {},
                "total_apps": 0,
            })

    @app.get("/api/skills/cli-anything/{app_name}")
    async def get_cli_app_schema(app_name: str) -> JSONResponse:
        """Get CLI schema for a specific application."""
        try:
            from archonx.skills.cli_anything.generator import CLIGenerator

            generator = CLIGenerator(app_name)
            schema = generator.generate()

            if not schema:
                return JSONResponse(
                    {"error": f"No schema for {app_name}"},
                    status_code=404,
                )

            return JSONResponse(schema)
        except Exception as e:
            return JSONResponse(
                {"error": str(e)},
                status_code=400,
            )

    @app.post("/api/skills/cli-anything/execute")
    async def execute_cli_command(body: dict[str, Any]) -> JSONResponse:
        """Execute a CLI command."""
        app = body.get("app", "")
        command = body.get("command", "")
        params = body.get("params", {})
        machine_id = body.get("machine_id")

        if not app or not command:
            return JSONResponse(
                {"error": "app and command required"},
                status_code=400,
            )

        try:
            from archonx.skills.cli_anything.executor import CLIExecutor

            executor = CLIExecutor()
            result = executor.execute_with_validation(
                app=app,
                command=command,
                params=params,
                machine_id=machine_id,
            )

            return JSONResponse(result)

        except Exception as e:
            return JSONResponse(
                {"status": "error", "error": str(e)},
                status_code=500,
            )

    @app.get("/api/skills/cli-anything/discover")
    async def discover_cli_apps() -> JSONResponse:
        """Discover installed applications with CLI support."""
        try:
            from archonx.skills.cli_anything.discovery import discover_all_apps

            apps = discover_all_apps()

            return JSONResponse({
                "discovered_apps": apps,
                "total": len(apps),
            })
        except Exception as e:
            return JSONResponse(
                {"error": str(e), "discovered_apps": [], "total": 0},
                status_code=500,
            )

    # ----- WebSocket -----

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        _ws_clients.add(ws)
        logger.info("WebSocket client connected (%d total)", len(_ws_clients))
        try:
            while True:
                data = await ws.receive_text()
                msg = json.loads(data)
                # Handle incoming WS commands
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
                elif msg.get("type") == "subscribe_board":
                    if _chessboard:
                        await ws.send_json({"type": "board", "data": _chessboard.to_dict()})
                elif msg.get("type") == "subscribe_dashboard":
                    if _dashboard:
                        await ws.send_json({"type": "dashboard", "data": _dashboard.to_dict()})
        except WebSocketDisconnect:
            _ws_clients.discard(ws)
            logger.info("WebSocket client disconnected (%d remaining)", len(_ws_clients))

    # Frontend static app (served last so /api and /ws stay authoritative)
    if _PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(_PUBLIC_DIR), html=True), name="frontend")

    return app


async def _broadcast(message: dict[str, Any]) -> None:
    """Send a message to all connected WebSocket clients."""
    dead: set[WebSocket] = set()
    for ws in _ws_clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    _ws_clients -= dead
