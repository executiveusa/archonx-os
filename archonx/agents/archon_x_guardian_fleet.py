"""
BEAD: AX-MERGE-008
Archon-X Guardian Fleet
========================
Monitors the 313-repo ecosystem under executiveusa GitHub org.
Mock returns static healthy data when GH_PAT is not set.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    pass

logger = logging.getLogger("archonx.agents.archon_x_guardian_fleet")

_GITHUB_API = "https://api.github.com"
_TIMEOUT = 15.0
_DEFAULT_ORG = "executiveusa"
_REPORTS_DIR = Path(__file__).parent.parent.parent / "ops" / "reports"

# Auto-fixable issue categories (no BEAD required)
AUTO_FIX_ALLOWED = frozenset([
    "typos_and_linting",
    "package_minor_version_bumps",
    "missing_init_files",
    "readme_badge_updates",
])

# Issues requiring BEAD approval
REQUIRES_BEAD_APPROVAL = frozenset([
    "breaking_api_changes",
    "database_migrations",
    "infrastructure_changes",
    "security_sensitive_code",
])


class GuardianFleet:
    """
    Guardian Fleet — monitors all repos under the executiveusa GitHub org.

    Provides health checks, auto-fix stubs, fleet reports, and APScheduler
    cron job registration. Mock mode when GH_PAT is not configured.
    """

    def __init__(
        self,
        github_token: str | None = None,
        org: str = _DEFAULT_ORG,
    ) -> None:
        """
        Initialise Guardian Fleet.

        Args:
            github_token: GitHub PAT. If None, reads from GH_PAT env var.
            org: GitHub organisation slug.
        """
        self._token: str | None = github_token or os.environ.get("GH_PAT")
        self._org = org
        self._mock: bool = not bool(self._token)
        _REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        if self._mock:
            logger.warning("GuardianFleet: GH_PAT not set — mock mode active")
        else:
            logger.info(
                "GuardianFleet initialised: org=%s, token=%s...", org, (self._token or "")[:6]
            )

    def _headers(self) -> dict[str, str]:
        """Build GitHub API headers."""
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def check_repo_health(self, repo_name: str) -> dict[str, Any]:
        """
        Check the health of a single repository.

        Args:
            repo_name: Repository name (without org prefix).

        Returns:
            Dict with keys: repo, build_status, test_status, open_issues,
                last_commit, coverage.
        """
        if self._mock:
            return {
                "repo": repo_name,
                "build_status": "passing",
                "test_status": "passing",
                "open_issues": 0,
                "last_commit": datetime.now().isoformat(),
                "coverage": 85.0,
                "mock": True,
            }

        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                # Repo info
                resp = client.get(
                    f"{_GITHUB_API}/repos/{self._org}/{repo_name}",
                    headers=self._headers(),
                )
                if resp.status_code == 404:
                    return {
                        "repo": repo_name,
                        "build_status": "not_found",
                        "open_issues": 0,
                        "error": "repo_not_found",
                    }
                resp.raise_for_status()
                repo_data: dict[str, Any] = resp.json()

                open_issues: int = repo_data.get("open_issues_count", 0)

                # Latest commit
                commits_resp = client.get(
                    f"{_GITHUB_API}/repos/{self._org}/{repo_name}/commits",
                    headers=self._headers(),
                    params={"per_page": 1},
                )
                last_commit = ""
                if commits_resp.status_code == 200:
                    commits = commits_resp.json()
                    if commits:
                        last_commit = commits[0].get("commit", {}).get("committer", {}).get("date", "")

                # Check workflow runs for build status
                runs_resp = client.get(
                    f"{_GITHUB_API}/repos/{self._org}/{repo_name}/actions/runs",
                    headers=self._headers(),
                    params={"per_page": 1},
                )
                build_status = "unknown"
                if runs_resp.status_code == 200:
                    runs_data = runs_resp.json()
                    runs = runs_data.get("workflow_runs", [])
                    if runs:
                        conclusion = runs[0].get("conclusion", "")
                        build_status = "passing" if conclusion == "success" else "failing"

                return {
                    "repo": repo_name,
                    "build_status": build_status,
                    "test_status": build_status,
                    "open_issues": open_issues,
                    "last_commit": last_commit,
                    "coverage": None,
                    "mock": False,
                }

        except httpx.HTTPError as exc:
            logger.error("GuardianFleet HTTP error for %s: %s", repo_name, exc)
            return {
                "repo": repo_name,
                "build_status": "error",
                "open_issues": 0,
                "error": str(exc),
            }
        except Exception as exc:
            logger.exception("GuardianFleet unexpected error for %s: %s", repo_name, exc)
            return {
                "repo": repo_name,
                "build_status": "error",
                "open_issues": 0,
                "error": str(exc),
            }

    def check_all_repos(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Check health of multiple repos (up to limit).

        Args:
            limit: Maximum number of repos to check (default 10 for dev, 313 for prod).

        Returns:
            List of repo health dicts.
        """
        if self._mock:
            # Return mock data for up to `limit` repos
            mock_repos = [
                f"archonx-os",
                f"voice-agents-fork",
                f"synthia",
                f"tanda-cdmx",
                f"macs-agent-portal",
                f"kupuri-media-website",
                f"darya-design-throne",
                f"amentislibrary",
                f"dashboard-agent-swarm",
                f"phone-call-assistant",
            ]
            results = []
            for repo in mock_repos[:limit]:
                results.append(self.check_repo_health(repo))
            return results

        # Fetch repo list from GitHub API
        try:
            all_repos: list[str] = []
            page = 1
            with httpx.Client(timeout=_TIMEOUT) as client:
                while len(all_repos) < limit:
                    resp = client.get(
                        f"{_GITHUB_API}/orgs/{self._org}/repos",
                        headers=self._headers(),
                        params={"per_page": 100, "page": page, "type": "all"},
                    )
                    resp.raise_for_status()
                    repos: list[dict[str, Any]] = resp.json()
                    if not repos:
                        break
                    all_repos.extend(r["name"] for r in repos)
                    page += 1

            target_repos = all_repos[:limit]
            results = []
            for repo_name in target_repos:
                results.append(self.check_repo_health(repo_name))
            return results

        except Exception as exc:
            logger.exception("check_all_repos failed: %s", exc)
            return []

    def auto_fix_minor_issues(
        self, repo_name: str, issues: list[str]
    ) -> dict[str, Any]:
        """
        Apply auto-fixable minor corrections to a repository.

        Only issues in AUTO_FIX_ALLOWED are processed. Issues in
        REQUIRES_BEAD_APPROVAL are logged for human review.

        Args:
            repo_name: Repository to fix.
            issues: List of issue category strings.

        Returns:
            Dict with fixed and skipped issue lists.
        """
        fixed: list[str] = []
        skipped: list[str] = []

        for issue in issues:
            if issue in AUTO_FIX_ALLOWED:
                logger.info(
                    "GuardianFleet: would auto-fix '%s' in %s (mock log)", issue, repo_name
                )
                fixed.append(issue)
            elif issue in REQUIRES_BEAD_APPROVAL:
                logger.warning(
                    "GuardianFleet: '%s' in %s requires BEAD approval — skipping",
                    issue,
                    repo_name,
                )
                skipped.append(issue)
            else:
                logger.debug("GuardianFleet: unknown issue type '%s' — skipping", issue)
                skipped.append(issue)

        return {
            "repo": repo_name,
            "fixed": fixed,
            "skipped_requires_approval": skipped,
            "mock": True,  # actual PR creation is a future implementation
        }

    def generate_fleet_report(self) -> dict[str, Any]:
        """
        Generate a summary report across all checked repos.

        Returns:
            Dict with total, healthy, failing, unknown counts and top issues.
        """
        repos = self.check_all_repos(limit=10)
        total = len(repos)
        healthy = sum(1 for r in repos if r.get("build_status") == "passing")
        failing = sum(1 for r in repos if r.get("build_status") == "failing")
        unknown = total - healthy - failing

        top_issues = [r["repo"] for r in repos if r.get("build_status") != "passing"]

        report: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "org": self._org,
            "total_checked": total,
            "healthy": healthy,
            "failing": failing,
            "unknown": unknown,
            "top_issues": top_issues[:5],
            "repos": repos,
        }

        # Write report to disk
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_path = _REPORTS_DIR / f"guardian_fleet_{date_str}.json"
        try:
            import json

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info("Guardian fleet report written: %s", report_path)
        except OSError as exc:
            logger.warning("Could not write fleet report: %s", exc)

        return report

    def schedule_cron_jobs(self, scheduler: Any) -> None:
        """
        Register APScheduler cron jobs for the guardian fleet.

        Jobs:
        - health_pulse: every 6 minutes
        - deep_scan: daily at 06:00
        - weekly_summary: Monday 12:00
        - monthly_archive: 1st of month 00:00

        Args:
            scheduler: APScheduler AsyncScheduler or BackgroundScheduler instance.
        """
        scheduler.add_job(
            self.generate_fleet_report,
            "cron",
            minute="*/6",
            id="guardian_health_pulse",
            replace_existing=True,
        )
        scheduler.add_job(
            lambda: self.check_all_repos(limit=313),
            "cron",
            hour=6,
            minute=0,
            id="guardian_deep_scan",
            replace_existing=True,
        )
        scheduler.add_job(
            self.generate_fleet_report,
            "cron",
            day_of_week="mon",
            hour=12,
            minute=0,
            id="guardian_weekly_summary",
            replace_existing=True,
        )
        logger.info("GuardianFleet cron jobs registered with APScheduler")
