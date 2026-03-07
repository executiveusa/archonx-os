"""CLI command handlers for repo-awareness system."""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

from archonx.repos.registry import RepoRegistry
from archonx.repos.router import Router


def _get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).resolve().parents[2]


def repos_ingest(args: argparse.Namespace) -> None:
    """Handle: archonx repos ingest --file <path> --mode index_only"""
    yaml_path = Path(args.file)

    if not yaml_path.is_absolute():
        yaml_path = _get_project_root() / yaml_path

    if args.mode != "index_only":
        print(f"ERROR: Only 'index_only' mode is supported. Got: {args.mode}", file=sys.stderr)
        sys.exit(1)

    registry = RepoRegistry()
    try:
        result = registry.ingest_yaml(yaml_path, mode=args.mode)
        result["message"] = f"Ingestion complete: {result['repo_count']} repos stored"
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        registry.close()


def repos_list(args: argparse.Namespace) -> None:
    """Handle: archonx repos list [--team <id>] [--type <id>] [--vis public|private] [--kind fork|orig]"""
    registry = RepoRegistry()
    try:
        repos = registry.get_repos(
            team_id=args.team,
            domain_type_id=args.type,
            visibility=args.vis,
            kind=args.kind,
        )

        output = {
            "total": len(repos),
            "filters": {
                "team": args.team,
                "type": args.type,
                "visibility": args.vis,
                "kind": args.kind,
            },
            "repos": [r.to_dict() for r in repos],
        }
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        registry.close()


def repos_show(args: argparse.Namespace) -> None:
    """Handle: archonx repos show --id <repo_id>"""
    registry = RepoRegistry()
    try:
        repo = registry.get_repo(args.id)
        if not repo:
            print(f"ERROR: Repo {args.id} not found", file=sys.stderr)
            sys.exit(1)

        team = registry.get_team(repo.team_id)
        output = {
            "repo": repo.to_dict(),
            "team": team.to_dict() if team else None,
        }
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        registry.close()


def repos_route(args: argparse.Namespace) -> None:
    """Handle: archonx repos route --repo-ids 1,2,3 --task <name>"""
    if not args.repo_ids:
        print("ERROR: --repo-ids is required", file=sys.stderr)
        sys.exit(1)

    try:
        repo_ids = [int(x.strip()) for x in args.repo_ids.split(",")]
    except ValueError:
        print("ERROR: --repo-ids must be comma-separated integers", file=sys.stderr)
        sys.exit(1)

    registry = RepoRegistry()
    try:
        router = Router(registry)
        plan = router.route(repo_ids, args.task)

        # Save artifact
        artifacts_dir = _get_project_root() / "artifacts" / "dispatch"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        artifact_path = artifacts_dir / f"dispatch_plan_{ts}.json"

        artifact_path.write_text(json.dumps(plan.to_dict(), indent=2), encoding="utf-8")

        output = {
            "status": "success",
            "dispatch_plan": plan.to_dict(),
            "artifact_saved": str(artifact_path),
        }
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        registry.close()


def zte_headers_plan(args: argparse.Namespace) -> None:
    """Handle: archonx zte headers plan --repo-ids <ids> [--all]"""
    registry = RepoRegistry()
    try:
        if args.all:
            repos = registry.get_repos()
            selected_repos = repos
        else:
            if not args.repo_ids:
                print("ERROR: --repo-ids or --all is required", file=sys.stderr)
                sys.exit(1)

            try:
                repo_ids = [int(x.strip()) for x in args.repo_ids.split(",")]
            except ValueError:
                print("ERROR: --repo-ids must be comma-separated integers", file=sys.stderr)
                sys.exit(1)

            selected_repos = []
            for repo_id in repo_ids:
                repo = registry.get_repo(repo_id)
                if repo:
                    selected_repos.append(repo)

        # Build plan
        modifications = []
        for repo in selected_repos:
            modifications.append({
                "repo_id": repo.id,
                "repo_name": repo.name,
                "file_to_modify_or_create": "agent.md or AGENTS.md or agents.md",
                "action": "create or update",
                "header_lines": 3,
                "remote_write": False,
                "status": "planned_no_execution",
            })

        # Save artifact
        artifacts_dir = _get_project_root() / "artifacts" / "zte"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        artifact_path = artifacts_dir / f"headers_plan_{ts}.json"

        plan_output = {
            "status": "plan_only_no_execution",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repos_count": len(selected_repos),
            "modifications": modifications,
            "universal_header_lines": [
                "archonx mcp connect --profile default && archonx mcp verify --require tools:playwright,puppeteer,git,github,vault",
                "archonx zte run --task \"$ARCHON_TASK\" --repo \"$ARCHON_REPO\" --id \"$ARCHON_REPO_ID\" --no-human --autofix --open-pr",
                "archonx tokens report --task \"$ARCHON_TASK\" --repo \"$ARCHON_REPO\" --compare baseline,token_saver --append logs/token_savings.csv",
            ],
            "next_step": "Review plan above. When ready, run: archonx zte headers install --artifact <path>",
        }

        artifact_path.write_text(json.dumps(plan_output, indent=2), encoding="utf-8")

        output = {
            "status": "success",
            "plan": plan_output,
            "artifact_saved": str(artifact_path),
        }
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        registry.close()


def mcp_preflight(args: argparse.Namespace) -> None:
    """Handle: archonx mcp preflight --require <tools>"""
    required_tools = args.require.split(",") if args.require else []

    # For now, this is a stub/mock verification
    # In production, this would connect to the actual MCP server
    result = {
        "status": "mock_success",
        "message": "Preflight verification (mock mode) — would require actual MCP server",
        "required_tools": required_tools,
        "verified_tools": required_tools,  # Mock: assume all verified
        "next_step": "Run: archonx mcp connect --profile default",
    }

    print(json.dumps(result, indent=2))
