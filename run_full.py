#!/usr/bin/env python3
"""
ArchonX Full Orchestrator v1.0
Runs vault agent audit + AI advisor recommendations in sequence.
Generates integrated report.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ArchonXOrchestrator:
    """Orchestrates vault agent and AI advisor."""

    def __init__(self, output_dir: str = "./ops/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }

    def run_vault_agent(self, env_file: str = None) -> bool:
        """Execute vault agent audit."""
        print("\n" + "="*60)
        print("STAGE 1: Vault Agent Audit")
        print("="*60)

        cmd = [sys.executable, "vault_agent.py", "--output-dir", str(self.output_dir)]
        if env_file:
            cmd.extend(["--file", env_file])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            self.report["stages"]["vault_agent"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode
            }

            return result.returncode == 0
        except Exception as e:
            print(f"ERROR: {e}")
            self.report["stages"]["vault_agent"] = {"status": "error", "error": str(e)}
            return False

    def load_vault_report(self) -> Dict[str, Any]:
        """Load the vault audit report."""
        report_path = self.output_dir / "vault_audit.json"
        if report_path.exists():
            with open(report_path) as f:
                return json.load(f)
        return {}

    def run_ai_advisor(self, vault_report: Dict[str, Any]) -> bool:
        """Execute AI advisor for recommendations."""
        print("\n" + "="*60)
        print("STAGE 2: AI Advisor Analysis")
        print("="*60)

        try:
            # Import and run advisor
            sys.path.insert(0, str(Path.cwd()))
            from ai_advisor import AIAdvisor

            advisor = AIAdvisor()
            print(f"Backend: {advisor.backend}")

            recommendations = {}
            secrets_inventory = vault_report.get("secrets_inventory", [])

            # Generate recommendations for critical secrets
            critical_secrets = [s for s in secrets_inventory if s.get("risk_level") == "CRITICAL"]

            print(f"Generating recommendations for {len(critical_secrets)} critical secrets...")

            for secret in critical_secrets[:5]:  # Limit to first 5 to avoid API rate limits
                key = secret.get("key", "UNKNOWN")
                classification = secret.get("classification", "GENERIC")
                risk = secret.get("risk_level", "UNKNOWN")

                advice = advisor.get_advice(key, classification, risk)
                recommendations[key] = {
                    "classification": classification,
                    "risk_level": risk,
                    "recommendation": advice
                }

            # Save recommendations
            rec_path = self.output_dir / "ai_recommendations.json"
            with open(rec_path, "w") as f:
                json.dump(recommendations, f, indent=2)
            print(f"Saved recommendations to {rec_path}")

            self.report["stages"]["ai_advisor"] = {
                "status": "success",
                "backend": advisor.backend,
                "recommendations_generated": len(recommendations)
            }

            return True
        except Exception as e:
            print(f"ERROR: {e}")
            self.report["stages"]["ai_advisor"] = {"status": "error", "error": str(e)}
            return False

    def generate_integrated_report(self, vault_report: Dict[str, Any]) -> None:
        """Generate final integrated report."""
        print("\n" + "="*60)
        print("STAGE 3: Integrated Report Generation")
        print("="*60)

        # Load recommendations if available
        rec_path = self.output_dir / "ai_recommendations.json"
        recommendations = {}
        if rec_path.exists():
            with open(rec_path) as f:
                recommendations = json.load(f)

        # Build integrated report
        integrated = {
            "executive_summary": {
                "timestamp": self.report["timestamp"],
                "audit_type": "vault_agent + ai_advisor",
                "total_secrets": vault_report.get("statistics", {}).get("total_secrets", 0),
                "critical_count": vault_report.get("statistics", {}).get("critical_count", 0),
                "high_count": vault_report.get("statistics", {}).get("high_count", 0),
                "recommendations_generated": len(recommendations)
            },
            "vault_audit": vault_report,
            "ai_recommendations": recommendations,
            "orchestrator_report": self.report
        }

        # Save integrated report
        report_path = self.output_dir / "integrated_report.json"
        with open(report_path, "w") as f:
            json.dump(integrated, f, indent=2)

        print(f"Integrated report saved to {report_path}")

        # Print summary
        print("\n" + "="*60)
        print("ORCHESTRATION SUMMARY")
        print("="*60)
        print(f"Total Secrets Found: {integrated['executive_summary']['total_secrets']}")
        print(f"Critical Secrets: {integrated['executive_summary']['critical_count']}")
        print(f"Recommendations Generated: {integrated['executive_summary']['recommendations_generated']}")
        print(f"Report Location: {report_path}")

    def run(self, env_file: str = None) -> int:
        """Execute full orchestration."""
        print("Starting ArchonX Full Orchestrator...")

        # Stage 1: Vault Agent
        if not self.run_vault_agent(env_file):
            print("Vault agent failed. Aborting.")
            return 1

        # Load vault report
        vault_report = self.load_vault_report()
        if not vault_report:
            print("No vault report found. Aborting.")
            return 1

        # Stage 2: AI Advisor
        if not self.run_ai_advisor(vault_report):
            print("AI advisor failed. Continuing with vault report only.")

        # Stage 3: Integrated Report
        self.generate_integrated_report(vault_report)

        return 0


if __name__ == "__main__":
    orchestrator = ArchonXOrchestrator()
    sys.exit(orchestrator.run())
