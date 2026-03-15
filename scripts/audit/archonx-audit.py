#!/usr/bin/env python3
"""
ARCHONX Baseline Audit Script
Phase 0: Inventory and conformance baseline

This script:
1. Inventories all plan + doc artifacts
2. Maps repository cross-references
3. Checks conformance to spec
4. Generates machine-readable baseline report
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ArchonXAudit:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.ops_reports = self.repo_root / "ops" / "reports"
        self.ops_reports.mkdir(parents=True, exist_ok=True)

        self.report = {
            "timestamp": datetime.utcnow().isoformat(),
            "repo_root": str(self.repo_root),
            "phase": 0,
            "artifacts": {
                "plans": [],
                "docs": [],
                "agents": [],
                "scripts": []
            },
            "cross_references": {
                "valid": [],
                "unresolved": [],
                "missing_files": []
            },
            "conformance": {
                "plan_files": 0,
                "doc_files": 0,
                "conformant": 0,
                "non_conformant": 0,
                "issues": []
            },
            "repositories": {
                "connected": [],
                "submodules": [],
                "unconnected": []
            }
        }

    def inventory_artifacts(self):
        """Inventory all plans, docs, agents."""
        print("[P0] Inventorying artifacts...")

        # Plans
        plans_dir = self.repo_root / "plans"
        if plans_dir.exists():
            for f in plans_dir.glob("*.md"):
                self.report["artifacts"]["plans"].append({
                    "file": f.name,
                    "path": str(f.relative_to(self.repo_root)),
                    "size_bytes": f.stat().st_size
                })

        # Docs
        docs_dir = self.repo_root / "docs"
        if docs_dir.exists():
            for f in docs_dir.glob("**/*.md"):
                self.report["artifacts"]["docs"].append({
                    "file": f.name,
                    "path": str(f.relative_to(self.repo_root)),
                    "size_bytes": f.stat().st_size
                })

        # Agents
        agents_dir = self.repo_root / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir():
                    config_file = agent_dir / "config.json"
                    if config_file.exists():
                        self.report["artifacts"]["agents"].append({
                            "name": agent_dir.name,
                            "path": str(agent_dir.relative_to(self.repo_root)),
                            "has_config": True
                        })

        print(f"  ✓ Plans: {len(self.report['artifacts']['plans'])}")
        print(f"  ✓ Docs: {len(self.report['artifacts']['docs'])}")
        print(f"  ✓ Agents: {len(self.report['artifacts']['agents'])}")

    def check_cross_references(self):
        """Check referenced files exist."""
        print("[P0] Checking cross-references...")

        # Reference patterns to check
        ref_patterns = [
            r"\[.*?\]\((.*?\.md)\)",  # Markdown links
            r"@(.*?)/",  # Submodule refs
        ]

        all_files = list(self.repo_root.glob("**/*.md"))

        for md_file in all_files:
            if "/.git" in str(md_file):
                continue

            try:
                content = md_file.read_text()

                # Check markdown links
                import re
                for match in re.finditer(r"\[.*?\]\(([^)]+)\)", content):
                    ref = match.group(1)
                    if ref.endswith(".md"):
                        ref_path = (md_file.parent / ref).resolve()
                        rel_ref = str(ref_path.relative_to(self.repo_root))

                        if ref_path.exists():
                            self.report["cross_references"]["valid"].append({
                                "from_file": str(md_file.relative_to(self.repo_root)),
                                "to_file": rel_ref
                            })
                        else:
                            self.report["cross_references"]["unresolved"].append({
                                "from_file": str(md_file.relative_to(self.repo_root)),
                                "referenced": ref,
                                "status": "missing"
                            })

            except Exception as e:
                self.report["conformance"]["issues"].append({
                    "file": str(md_file),
                    "error": str(e)
                })

        print(f"  ✓ Valid refs: {len(self.report['cross_references']['valid'])}")
        print(f"  ⚠ Unresolved: {len(self.report['cross_references']['unresolved'])}")

    def check_repositories(self):
        """Identify connected and unconnected repositories."""
        print("[P0] Checking repository connections...")

        # Check git config for submodules
        gitmodules = self.repo_root / ".gitmodules"
        if gitmodules.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(gitmodules)

            for section in config.sections():
                if section.startswith("submodule"):
                    path = config.get(section, "path")
                    url = config.get(section, "url")
                    self.report["repositories"]["submodules"].append({
                        "path": path,
                        "url": url
                    })

        # Hardcoded known connected repos (from AGENTS.md, plans, etc)
        self.report["repositories"]["connected"] = [
            "archonx-os",
            "dashboard-agent-swarm",
            "paulisworld-openclaw-3d",
            "paulis-pope-bot",
            "agents/devika",
            "agents/darya",
            "agents/lightning"
        ]

        # Check for unconnected but referenced repos
        unconnected_refs = []
        for artifact in self.report["artifacts"]["plans"] + self.report["artifacts"]["docs"]:
            if "AGENT_ZERO" in artifact.get("file", ""):
                unconnected_refs.append("E:/AGENT_ZERO (external)")

        self.report["repositories"]["unconnected"] = list(set(unconnected_refs))

        print(f"  ✓ Submodules: {len(self.report['repositories']['submodules'])}")
        print(f"  ✓ Connected: {len(self.report['repositories']['connected'])}")
        print(f"  ⚠ Unconnected: {len(self.report['repositories']['unconnected'])}")

    def check_conformance(self):
        """Check documentation conformance to spec."""
        print("[P0] Checking conformance...")

        # Required sections per ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md
        required_sections = [
            "Objective",
            "Scope",
            "Architecture",
            "Implementation",
            "Success Criteria"
        ]

        all_md_files = list(self.repo_root.glob("plans/**/*.md"))

        for md_file in all_md_files:
            try:
                content = md_file.read_text()

                missing_sections = []
                for section in required_sections:
                    if f"## {section}" not in content and f"# {section}" not in content:
                        missing_sections.append(section)

                if missing_sections:
                    self.report["conformance"]["non_conformant"] += 1
                    self.report["conformance"]["issues"].append({
                        "file": str(md_file.relative_to(self.repo_root)),
                        "missing_sections": missing_sections
                    })
                else:
                    self.report["conformance"]["conformant"] += 1

                self.report["conformance"]["plan_files"] += 1

            except Exception as e:
                self.report["conformance"]["issues"].append({
                    "file": str(md_file),
                    "error": str(e)
                })

        print(f"  ✓ Conformant files: {self.report['conformance']['conformant']}")
        print(f"  ⚠ Non-conformant: {self.report['conformance']['non_conformant']}")

    def generate_report(self):
        """Write baseline report to disk."""
        print("[P0] Generating baseline report...")

        report_file = self.ops_reports / "baseline_audit.json"
        with open(report_file, "w") as f:
            json.dump(self.report, f, indent=2)

        print(f"  ✓ Report written to {report_file}")

        # Also generate markdown summary
        md_report = self.ops_reports / "P0_CONFORMANCE_REPORT.md"
        with open(md_report, "w") as f:
            f.write("# Phase 0 Baseline Audit Report\n\n")
            f.write(f"**Generated:** {self.report['timestamp']}\n\n")

            f.write("## Artifact Inventory\n\n")
            f.write(f"- Plan files: {len(self.report['artifacts']['plans'])}\n")
            f.write(f"- Doc files: {len(self.report['artifacts']['docs'])}\n")
            f.write(f"- Agents configured: {len(self.report['artifacts']['agents'])}\n\n")

            f.write("## Repository Status\n\n")
            f.write(f"- Submodules: {len(self.report['repositories']['submodules'])}\n")
            f.write(f"- Connected repos: {len(self.report['repositories']['connected'])}\n")
            f.write(f"- Unconnected/external: {len(self.report['repositories']['unconnected'])}\n\n")

            f.write("## Cross-Reference Health\n\n")
            f.write(f"- Valid references: {len(self.report['cross_references']['valid'])}\n")
            f.write(f"- Unresolved references: {len(self.report['cross_references']['unresolved'])}\n")
            if self.report['cross_references']['unresolved']:
                f.write("\n### Unresolved References\n")
                for ref in self.report['cross_references']['unresolved']:
                    f.write(f"- {ref['from_file']} → {ref['referenced']}\n")

            f.write("\n## Conformance Status\n\n")
            f.write(f"- Conformant files: {self.report['conformance']['conformant']}\n")
            f.write(f"- Non-conformant files: {self.report['conformance']['non_conformant']}\n")
            if self.report['conformance']['issues']:
                f.write("\n### Issues\n")
                for issue in self.report['conformance']['issues'][:5]:  # Show first 5
                    f.write(f"- {issue.get('file', 'unknown')}: {issue.get('error', 'conformance')}\n")

        print(f"  ✓ Markdown summary written to {md_report}")

    def run(self):
        """Execute full baseline audit."""
        print("\n" + "="*60)
        print("ARCHONX PHASE 0 BASELINE AUDIT")
        print("="*60 + "\n")

        self.inventory_artifacts()
        self.check_cross_references()
        self.check_repositories()
        self.check_conformance()
        self.generate_report()

        print("\n" + "="*60)
        print("PHASE 0 AUDIT COMPLETE")
        print("="*60 + "\n")
        print(f"Report: {self.ops_reports / 'baseline_audit.json'}")
        print(f"Summary: {self.ops_reports / 'P0_CONFORMANCE_REPORT.md'}\n")

        return self.report


if __name__ == "__main__":
    repo_root = os.getenv("ARCHONX_REPO_ROOT", "/c/archonx-os-main")
    audit = ArchonXAudit(repo_root)
    report = audit.run()

    # Exit with non-zero if critical issues
    if report["cross_references"]["unresolved"]:
        sys.exit(1)
