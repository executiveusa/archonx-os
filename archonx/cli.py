"""
ArchonX CLI
===========
Command-line interface for the ArchonX Operating System.

Usage:
    archonx boot          — Boot the kernel (64 agents)
    archonx status        — Show system status
    archonx deploy        — Deploy to a client
    archonx meetings      — Show Pauli's Place schedule
    archonx serve         — Start the FastAPI visualization server
    archonx skills        — List registered skills
    archonx tools         — List registered tools
    archonx flywheel      — Show flywheel stats
    archonx scout         — Run Upwork scout
    archonx theater       — Show theater stats
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


def _boot(_args: argparse.Namespace) -> None:
    """Boot the ArchonX kernel."""
    from archonx.kernel import ArchonXKernel

    kernel = ArchonXKernel()
    asyncio.run(kernel.boot())
    print(f"\nArchonX Kernel v0.1.0 — 64 agents online.")
    print("Codename: Daily at Pauli's\n")
    print("Agents registered:", len(kernel.registry))
    print("White crew:", len(kernel.white_crew.agents))
    print("Black crew:", len(kernel.black_crew.agents))
    print("Meetings scheduled:", len(kernel.paulis_place.schedule))
    print("Tools registered:", len(kernel.tools.list_tools()))
    print("Skills discovered:", len(kernel.skill_registry.list_skills()))
    print("Flywheel:", "ACTIVE" if kernel.flywheel else "INACTIVE")
    print("Theater:", "LIVE" if kernel.theater else "OFFLINE")


def _status(_args: argparse.Namespace) -> None:
    """Show current system status."""
    from archonx.core.agents import AgentRegistry, Crew, build_all_agents
    from archonx.core.metrics import Leaderboard

    registry = AgentRegistry()
    build_all_agents(registry)

    white = registry.get_by_crew(Crew.WHITE)
    black = registry.get_by_crew(Crew.BLACK)

    print("=" * 50)
    print("  ArchonX OS — System Status")
    print("=" * 50)
    print(f"  Total agents:  {len(registry)}")
    print(f"  White crew:    {len(white)} agents")
    print(f"  Black crew:    {len(black)} agents")
    print()

    # Print back-rank for each crew
    for crew_name, agents in [("WHITE", white), ("BLACK", black)]:
        print(f"  {crew_name} Crew — Key Agents:")
        back = [a for a in agents if a.role.value in ("king", "queen", "rook", "knight", "bishop")]
        for a in back:
            print(f"    [{a.position}] {a.name:12s} ({a.role.value:6s}) — {a.specialty}")
        print()


def _deploy(args: argparse.Namespace) -> None:
    """Deploy ArchonX to a client."""
    from archonx.deploy.client_deployer import ClientDeployer

    deployer = ClientDeployer()
    instance = asyncio.run(
        deployer.deploy_client(
            client_id=args.client,
            client_name=args.name or args.client,
        )
    )
    print(f"\nDeployment complete!")
    print(f"  Client:    {instance.client_name}")
    print(f"  Instance:  {instance.instance_id}")
    print(f"  Status:    {instance.status}")
    print(f"  Agents:    {instance.agent_count}")


def _meetings(_args: argparse.Namespace) -> None:
    """Show Pauli's Place meeting schedule."""
    from archonx.meetings.paulis_place import DAILY_SCHEDULE

    print("=" * 50)
    print("  Pauli's Place — Daily Schedule")
    print("=" * 50)
    for m in DAILY_SCHEDULE:
        print(f"\n  {m.time_utc.strftime('%H:%M UTC')} — {m.description}")
        print(f"  Attendees: {m.attendees}")
        for item in m.agenda:
            print(f"    • {item}")
    print()


def _serve(args: argparse.Namespace) -> None:
    """Start the FastAPI visualization server."""
    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn not installed. Run: pip install archonx-os[viz]")
        sys.exit(1)

    from archonx.server import create_app

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)


def _skills(_args: argparse.Namespace) -> None:
    """List all registered skills."""
    from archonx.skills.registry import SkillRegistry

    reg = SkillRegistry()
    reg.auto_discover()
    skills = reg.list_skills()
    print("=" * 60)
    print("  ArchonX OS — Registered Skills")
    print("=" * 60)
    for s in skills:
        print(f"  [{s.category.value:14s}] {s.name:25s} — {s.description}")
    print(f"\n  Total: {len(skills)} skills")


def _tools(_args: argparse.Namespace) -> None:
    """List all registered tools."""
    from archonx.kernel import ArchonXKernel

    kernel = ArchonXKernel()
    tools = kernel.tools.list_tools()
    print("=" * 60)
    print("  ArchonX OS — Registered Tools")
    print("=" * 60)
    for name in tools:
        tool = kernel.tools.get(name)
        desc = tool.description if tool else ""
        print(f"  {name:25s} — {desc}")
    print(f"\n  Total: {len(tools)} tools")


def _flywheel(_args: argparse.Namespace) -> None:
    """Show flywheel stats."""
    from archonx.kernel import ArchonXKernel

    kernel = ArchonXKernel()
    stats = kernel.flywheel.stats
    print("=" * 50)
    print("  ArchonX OS — Flywheel Engine")
    print("=" * 50)
    for k, v in stats.items():
        print(f"  {k:25s}: {v}")


def _scout(args: argparse.Namespace) -> None:
    """Run an Upwork scout search."""
    from archonx.skills.upwork_scout import UpworkScoutSkill
    from archonx.skills.base import SkillContext

    skill = UpworkScoutSkill()
    ctx = SkillContext(
        task={"type": "upwork_scout"},
        agent_id="cli_scout",
        session_id="cli",
        params={"action": "search", "query": args.query, "skills_available": args.skills.split(",") if args.skills else []},
    )
    result = asyncio.run(skill.execute(ctx))
    print(json.dumps(result.data, indent=2))


def _theater(_args: argparse.Namespace) -> None:
    """Show agent theater stats."""
    from archonx.kernel import ArchonXKernel

    kernel = ArchonXKernel()
    stats = kernel.theater.stats
    print("=" * 50)
    print("  ArchonX OS — Agent Theater")
    print("=" * 50)
    for k, v in stats.items():
        print(f"  {k:25s}: {v}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="archonx",
        description="ArchonX Operating System — 64-agent dual-crew AI infrastructure",
    )
    sub = parser.add_subparsers(dest="command")

    # boot
    sub.add_parser("boot", help="Boot the ArchonX kernel")

    # status
    sub.add_parser("status", help="Show system status")

    # deploy
    p_deploy = sub.add_parser("deploy", help="Deploy to a client")
    p_deploy.add_argument("--client", required=True, help="Client ID")
    p_deploy.add_argument("--name", help="Client display name")

    # meetings
    sub.add_parser("meetings", help="Show Pauli's Place schedule")

    # serve
    p_serve = sub.add_parser("serve", help="Start visualization server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Bind host")
    p_serve.add_argument("--port", type=int, default=8080, help="Bind port")

    # skills
    sub.add_parser("skills", help="List registered skills")

    # tools
    sub.add_parser("tools", help="List registered tools")

    # flywheel
    sub.add_parser("flywheel", help="Show flywheel engine stats")

    # scout
    p_scout = sub.add_parser("scout", help="Run Upwork scout search")
    p_scout.add_argument("--query", default="python automation", help="Search query")
    p_scout.add_argument("--skills", default="", help="Comma-separated skills")

    # theater
    sub.add_parser("theater", help="Show agent theater stats")

    args = parser.parse_args()

    handlers = {
        "boot": _boot,
        "status": _status,
        "deploy": _deploy,
        "meetings": _meetings,
        "serve": _serve,
        "skills": _skills,
        "tools": _tools,
        "flywheel": _flywheel,
        "scout": _scout,
        "theater": _theater,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
