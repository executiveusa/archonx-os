"""ARCHONX:SYNTHIA — Server settings loaded from environment."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All settings sourced from env vars. Never hardcode secrets."""

    # ── Orgo ──────────────────────────────────────────────
    orgo_api_key: str = ""

    # ── GLM-5 / Z.ai ─────────────────────────────────────
    zai_api_key: str = ""

    # ── Notion ────────────────────────────────────────────
    notion_token: str = ""
    notion_tasks_db_id: str = ""
    notion_runs_db_id: str = ""
    notion_artifacts_db_id: str = ""
    notion_approvals_db_id: str = ""
    notion_profiles_db_id: str = ""
    notion_agents_db_id: str = ""
    notion_sops_db_id: str = ""

    # ── Twilio ────────────────────────────────────────────
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_number: str = ""

    # ── Network ───────────────────────────────────────────
    base_url: str = "http://localhost:8000"

    # ── Code Runner ───────────────────────────────────────
    runner_port: int = 9000
    runner_max_runtime_seconds: int = 300

    # ── Agent Budgets ─────────────────────────────────────
    max_steps_per_task: int = 40
    max_tool_calls_per_task: int = 80
    max_runtime_minutes_per_task: int = 30

    # ── Logging ───────────────────────────────────────────
    log_level: str = "info"
    log_format: str = "json"

    # ── Egress ────────────────────────────────────────────
    proxy_allowlist: str = "api.notion.com,api.orgo.ai,api.z.ai,api.twilio.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
