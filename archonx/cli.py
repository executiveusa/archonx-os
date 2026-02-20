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
from pathlib import Path
from typing import Any

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


def _onboard(args: argparse.Namespace) -> None:
    """Run onboarding voice flow and execute onboarding task bundle."""
    from archonx.kernel import ArchonXKernel
    from archonx.onboarding.voice_agent.runner import OnboardingVoiceRunner

    async def _run() -> dict[str, Any]:
        kernel = ArchonXKernel()
        await kernel.boot()
        try:
            default_runner = OnboardingVoiceRunner()
            runner = OnboardingVoiceRunner(
                transcript_path=Path(args.transcript) if args.transcript else default_runner.transcript_path,
                tasks_path=Path(args.tasks) if args.tasks else default_runner.tasks_path,
            )
            transcript_text = (
                Path(args.transcript).read_text(encoding="utf-8")
                if args.transcript
                else runner.load_transcript()
            )
            return await runner.run_plan(
                executor=kernel.execute_task,
                transcript_text=transcript_text,
                org_id=args.org,
                project_id=args.project,
            )
        finally:
            await kernel.shutdown()

    print(json.dumps(asyncio.run(_run()), indent=2))


def _doctor(_args: argparse.Namespace) -> None:
    """Run system health check (archonx-ops doctor).

    Checks:
    - All 64 agents registered
    - All skills loadable
    - All tools loadable
    - Config file valid
    - Memory layer reachable

    Emits a JSON report to ops/reports/.
    """
    from datetime import datetime, timezone

    report: dict[str, Any] = {
        "command": "doctor",
        "timestamp": datetime.now(timezone.UTC).isoformat(),
        "checks": {},
        "overall": "healthy",
    }

    # 1. Agent registry
    try:
        from archonx.core.agents import AgentRegistry, build_all_agents

        reg = AgentRegistry()
        build_all_agents(reg)
        count = len(reg)
        report["checks"]["agents"] = {"status": "ok" if count == 64 else "warn", "count": count}
    except Exception as exc:
        report["checks"]["agents"] = {"status": "error", "error": str(exc)}
        report["overall"] = "unhealthy"

    # 2. Skills
    try:
        from archonx.skills.registry import SkillRegistry

        sr = SkillRegistry()
        sr.auto_discover()
        skills = sr.list_skills()
        report["checks"]["skills"] = {"status": "ok", "count": len(skills), "names": skills}
    except Exception as exc:
        report["checks"]["skills"] = {"status": "error", "error": str(exc)}
        report["overall"] = "unhealthy"

    # 3. Tools
    try:
        from archonx.tools.base import ToolRegistry
        from archonx.tools.fixer import FixerAgentTool
        from archonx.tools.browser_test import BrowserTestTool
        from archonx.tools.deploy import DeploymentTool
        from archonx.tools.analytics import AnalyticsTool
        from archonx.tools.computer_use import ComputerUseTool
        from archonx.tools.remotion import RemotionTool
        from archonx.tools.grep_mcp import GrepMCPTool

        tr = ToolRegistry()
        for tool_cls in [FixerAgentTool, BrowserTestTool, DeploymentTool, AnalyticsTool, ComputerUseTool, RemotionTool, GrepMCPTool]:
            tr.register(tool_cls())
        report["checks"]["tools"] = {"status": "ok", "count": len(tr._tools)}
    except Exception as exc:
        report["checks"]["tools"] = {"status": "error", "error": str(exc)}
        report["overall"] = "unhealthy"

    # 4. Config
    try:
        config_path = Path(__file__).resolve().parent / "config" / "archonx-config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        report["checks"]["config"] = {"status": "ok", "version": data.get("system", {}).get("version", "?")}
    except Exception as exc:
        report["checks"]["config"] = {"status": "error", "error": str(exc)}
        report["overall"] = "unhealthy"

    # 5. New modules importable
    module_checks = []
    for mod_name in ["archonx.auth", "archonx.mail", "archonx.beads", "archonx.kpis", "archonx.revenue", "archonx.automation", "archonx.memory"]:
        try:
            __import__(mod_name)
            module_checks.append({"module": mod_name, "status": "ok"})
        except Exception as exc:
            module_checks.append({"module": mod_name, "status": "error", "error": str(exc)})
            report["overall"] = "unhealthy"
    report["checks"]["modules"] = module_checks

    # Write report
    reports_dir = Path(__file__).resolve().parents[1] / "ops" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.UTC).strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"doctor_{ts}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to {report_path}")


def _graphbrain_run(args: argparse.Namespace) -> None:
    """Run GraphBrain runtime in full or light mode."""
    from services.graphbrain import GraphBrainRuntime, Reporter

    root = Path(__file__).resolve().parents[1]
    runtime = GraphBrainRuntime(root)
    payload = runtime.run(mode=args.mode)
    Reporter(root).write_all(payload)
    print(json.dumps({"mode": args.mode, "work_orders": len(payload["work_orders"])}, indent=2))


def _graphbrain_init_repo(args: argparse.Namespace) -> None:
    """Initialize .archonx template in a repo path."""
    from services.graphbrain import Propagator

    root = Path(__file__).resolve().parents[1]
    repo_path = Path(args.path) if args.path else root
    propagator = Propagator(root, root / "templates" / "archonx")
    propagator.init_repo(args.repo, repo_path)
    print(json.dumps({"repo": args.repo, "path": str(repo_path)}, indent=2))


def _graphbrain_propagate(args: argparse.Namespace) -> None:
    """Propagate .archonx standards to ecosystem repos."""
    from services.graphbrain import Propagator
    from services.graphbrain.repo_indexer import load_target_repos

    root = Path(__file__).resolve().parents[1]
    repos = load_target_repos(root)
    propagator = Propagator(root, root / "templates" / "archonx")
    results = propagator.propagate_all(repos if args.all else ["executiveusa/archonx-os"])
    print(json.dumps([r.__dict__ for r in results], indent=2))


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

    # doctor
    sub.add_parser("doctor", help="Run system health check (archonx-ops doctor)")

    # onboard
    p_onboard = sub.add_parser("onboard", help="Run onboarding voice flow")
    p_onboard.add_argument("--org", default="default-org", help="Organization identifier")
    p_onboard.add_argument("--project", default="default-project", help="Project identifier")
    p_onboard.add_argument("--transcript", help="Path to transcript markdown file")
    p_onboard.add_argument("--tasks", help="Path to onboarding task bundle JSON")

    # graphbrain
    p_graphbrain = sub.add_parser("graphbrain", help="GraphBrain runtime commands")
    gb_sub = p_graphbrain.add_subparsers(dest="graphbrain_command")

    p_graphbrain_run = gb_sub.add_parser("run", help="Run graphbrain")
    p_graphbrain_run.add_argument("--mode", choices=["full", "light"], default="full")

    p_graphbrain_init = gb_sub.add_parser("init-repo", help="Init .archonx in target repo")
    p_graphbrain_init.add_argument("repo", help="Repository slug")
    p_graphbrain_init.add_argument("--path", help="Local path override")

    p_graphbrain_propagate = gb_sub.add_parser("propagate", help="Propagate standards")
    p_graphbrain_propagate.add_argument("--all", action="store_true", help="Propagate to all repos")

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
        "onboard": _onboard,
        "doctor": _doctor,
    }

    if args.command == "graphbrain":
        graphbrain_handlers = {
            "run": _graphbrain_run,
            "init-repo": _graphbrain_init_repo,
            "propagate": _graphbrain_propagate,
        }
        handler = graphbrain_handlers.get(args.graphbrain_command)
        if handler:
            handler(args)
            return
        p_graphbrain.print_help()
        return

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
