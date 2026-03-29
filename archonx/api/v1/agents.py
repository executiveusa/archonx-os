"""Agent roster and status endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/agents")


@router.get("")
async def list_agents(request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
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
            "soul": getattr(a, "soul", None) is not None,
        }
        for a in kernel.registry.all()
    ]
    return JSONResponse({"agents": agents, "count": len(agents)})


@router.get("/skills")
async def list_skills(request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    skills = kernel.skill_registry.list_skills()
    return JSONResponse({
        "skills": [
            {"name": s.name, "description": s.description, "category": s.category.value}
            for s in skills
        ],
        "count": len(skills),
    })


@router.get("/tools")
async def list_tools(request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    tools = kernel.tools.list_tools()
    return JSONResponse({"tools": tools})


@router.get("/{agent_id}")
async def get_agent(agent_id: str, request: Request) -> JSONResponse:
    kernel = request.app.state.app_state.kernel
    if kernel is None:
        return JSONResponse({"error": "not ready"}, status_code=503)

    agent = kernel.registry.get(agent_id)
    if agent is None:
        return JSONResponse({"error": "agent not found"}, status_code=404)

    return JSONResponse({
        "id": agent.agent_id,
        "name": agent.name,
        "crew": agent.crew.value,
        "role": agent.role.value,
        "position": agent.position,
        "specialty": agent.specialty,
        "status": agent.status.value,
        "health": agent.health,
        "tasks": agent.tasks_completed,
        "score": agent.score,
    })
