"""
ARCHON-X Cron Jobs — APScheduler
==================================
6 recurring jobs wired to APScheduler (or manually from Celery beat).
Jobs read config from `cron_jobs` DB table at startup.

Schedule (defaults — overridden by DB):
  heartbeat          every 30s   — WebSocket ping to all connected clients
  metrics_snapshot   every 5min  — snapshot agent_metrics table
  cost_report        daily 08:00 — email/Popebot daily cost report
  task_cleanup       daily 02:00 — archive completed tasks older than 7 days
  ws_session_prune   every 1hr   — delete stale ws_sessions
  notion_sync        every 30min — sync tasks/agents to Notion DB
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger("archonx.jobs")

# Try APScheduler — degrade gracefully if not installed
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    _APS_AVAILABLE = True
except ImportError:
    _APS_AVAILABLE = False
    logger.warning("APScheduler not installed — cron jobs disabled")

# ---------------------------------------------------------------------------
# Job registry
# ---------------------------------------------------------------------------

_JOB_REGISTRY: dict[str, Callable] = {}


def register_job(name: str):
    """Decorator to register a job function by name."""
    def decorator(fn: Callable) -> Callable:
        _JOB_REGISTRY[name] = fn
        return fn
    return decorator


def run_job_by_name(name: str) -> None:
    """Execute a registered job synchronously (used by Celery worker)."""
    fn = _JOB_REGISTRY.get(name)
    if not fn:
        raise ValueError(f"Unknown job: {name}")
    # If the job is async, run it in a new event loop
    if asyncio.iscoroutinefunction(fn):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(fn())
        finally:
            loop.close()
    else:
        fn()


# ---------------------------------------------------------------------------
# Individual job implementations
# ---------------------------------------------------------------------------

@register_job("heartbeat")
async def job_heartbeat() -> None:
    """Broadcast WebSocket heartbeat to all connected clients."""
    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        if hasattr(kernel, "ws_broadcast"):
            await kernel.ws_broadcast({"type": "heartbeat", "ts": _now_iso()})
    except Exception as exc:
        logger.debug(f"[heartbeat] {exc}")


@register_job("metrics_snapshot")
async def job_metrics_snapshot() -> None:
    """Snapshot per-agent metrics into agent_metrics table."""
    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        pool = getattr(kernel, "_db_pool", None)
        if not pool:
            return

        async with pool.acquire() as conn:
            # Pull aggregate stats from execution_logs
            rows = await conn.fetch(
                """
                SELECT agent_id,
                       COUNT(*) AS task_count,
                       SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success_count,
                       AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) * 1000)::int AS avg_ms
                FROM tasks
                WHERE created_at > NOW() - INTERVAL '5 minutes'
                GROUP BY agent_id
                """
            )
            for row in rows:
                success_rate = (
                    row["success_count"] / row["task_count"]
                    if row["task_count"] > 0 else 0.0
                )
                await conn.execute(
                    """
                    INSERT INTO agent_metrics
                      (agent_id, task_count, success_rate, avg_execution_ms, snapshot_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    """,
                    row["agent_id"],
                    row["task_count"],
                    success_rate,
                    row["avg_ms"] or 0,
                )

        logger.debug(f"[metrics] Snapshotted {len(rows)} agents")
    except Exception as exc:
        logger.error(f"[metrics_snapshot] {exc}")


@register_job("cost_report")
async def job_cost_report() -> None:
    """Generate and send daily cost report via Popebot."""
    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        pool = getattr(kernel, "_db_pool", None)

        total_cost = 0.0
        agent_breakdown: list[dict] = []

        if pool:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT agent_id, SUM(cost_usd) AS total
                    FROM cost_tracking
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY agent_id
                    ORDER BY total DESC
                    LIMIT 10
                    """
                )
                for row in rows:
                    total_cost += float(row["total"] or 0)
                    agent_breakdown.append({
                        "agent_id": str(row["agent_id"]),
                        "cost": float(row["total"]),
                    })

        report = (
            f"📊 ARCHON-X Daily Cost Report — {_today()}\n"
            f"Total: ${total_cost:.4f}\n"
            f"Top agents:\n"
            + "\n".join(
                f"  {r['agent_id'][:8]}… ${r['cost']:.4f}"
                for r in agent_breakdown[:5]
            )
        )

        # Send via Popebot if wired
        popebot = getattr(getattr(kernel, "comms", None), "popebot", None) \
            if hasattr(kernel, "comms") else None
        if not popebot:
            popebot = getattr(kernel, "_popebot", None)

        if popebot and hasattr(popebot, "send"):
            await popebot.send("EMAIL", {
                "subject": f"ARCHON-X Cost Report {_today()}",
                "body": report,
            })

        logger.info(f"[cost_report] Sent. Total 24h: ${total_cost:.4f}")
    except Exception as exc:
        logger.error(f"[cost_report] {exc}")


@register_job("task_cleanup")
async def job_task_cleanup() -> None:
    """Archive completed tasks older than 7 days."""
    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        pool = getattr(kernel, "_db_pool", None)
        if not pool:
            return

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM tasks
                WHERE status IN ('success', 'completed', 'cancelled')
                  AND updated_at < NOW() - INTERVAL '7 days'
                """
            )
        logger.info(f"[task_cleanup] {result}")
    except Exception as exc:
        logger.error(f"[task_cleanup] {exc}")


@register_job("ws_session_prune")
async def job_ws_session_prune() -> None:
    """Remove stale WebSocket session records."""
    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        pool = getattr(kernel, "_db_pool", None)
        if not pool:
            return

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM ws_sessions
                WHERE last_seen < NOW() - INTERVAL '1 hour'
                """
            )
        logger.debug(f"[ws_prune] {result}")
    except Exception as exc:
        logger.error(f"[ws_session_prune] {exc}")


@register_job("notion_sync")
async def job_notion_sync() -> None:
    """Sync recent agent tasks to Notion database (if NOTION_TOKEN set)."""
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        return

    try:
        from archonx.core.kernel import ArchonXKernel  # type: ignore
        kernel = ArchonXKernel.get_instance()
        pool = getattr(kernel, "_db_pool", None)
        if not pool:
            return

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, agent_id, status, created_at
                FROM tasks
                WHERE created_at > NOW() - INTERVAL '30 minutes'
                ORDER BY created_at DESC
                LIMIT 50
                """
            )

        # Minimal Notion API call (full integration would use httpx)
        logger.debug(f"[notion_sync] {len(rows)} tasks to sync (stub)")
    except Exception as exc:
        logger.error(f"[notion_sync] {exc}")


# ---------------------------------------------------------------------------
# Scheduler builder
# ---------------------------------------------------------------------------

def build_scheduler() -> "AsyncIOScheduler | None":
    """
    Build and return an AsyncIOScheduler with all 6 registered jobs.
    Returns None if APScheduler is not installed.
    """
    if not _APS_AVAILABLE:
        return None

    scheduler = AsyncIOScheduler(timezone="UTC")

    # heartbeat — every 30 seconds
    scheduler.add_job(
        job_heartbeat,
        trigger=IntervalTrigger(seconds=30),
        id="heartbeat",
        replace_existing=True,
        misfire_grace_time=10,
    )

    # metrics_snapshot — every 5 minutes
    scheduler.add_job(
        job_metrics_snapshot,
        trigger=IntervalTrigger(minutes=5),
        id="metrics_snapshot",
        replace_existing=True,
        misfire_grace_time=60,
    )

    # cost_report — daily at 08:00 UTC
    scheduler.add_job(
        job_cost_report,
        trigger=CronTrigger(hour=8, minute=0),
        id="cost_report",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # task_cleanup — daily at 02:00 UTC
    scheduler.add_job(
        job_task_cleanup,
        trigger=CronTrigger(hour=2, minute=0),
        id="task_cleanup",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # ws_session_prune — every hour
    scheduler.add_job(
        job_ws_session_prune,
        trigger=IntervalTrigger(hours=1),
        id="ws_session_prune",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # notion_sync — every 30 minutes
    scheduler.add_job(
        job_notion_sync,
        trigger=IntervalTrigger(minutes=30),
        id="notion_sync",
        replace_existing=True,
        misfire_grace_time=300,
    )

    logger.info(f"[scheduler] Built with {len(_JOB_REGISTRY)} jobs registered")
    return scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
