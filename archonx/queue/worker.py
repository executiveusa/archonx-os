"""
ARCHON-X Task Queue — Celery worker
====================================
Replaces blocking kernel.execute_task() with async Celery tasks.
Falls back to synchronous execution if Redis is not available.

Broker: Redis at REDIS_URL env var (defaults to redis://localhost:6379/0)
Backend: Same Redis (or set CELERY_RESULT_BACKEND)
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

logger = logging.getLogger("archonx.queue")

# Try to import Celery. Degrade gracefully if not installed.
try:
    from celery import Celery, Task
    _CELERY_AVAILABLE = True
except ImportError:
    _CELERY_AVAILABLE = False
    logger.warning("Celery not installed — task queue running in SYNCHRONOUS mode")


# ---------------------------------------------------------------------------
# Celery app factory
# ---------------------------------------------------------------------------

def make_celery_app() -> "Celery | None":
    if not _CELERY_AVAILABLE:
        return None

    broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    backend = os.getenv("CELERY_RESULT_BACKEND", broker)

    app = Celery(
        "archonx",
        broker=broker,
        backend=backend,
        include=["archonx.queue.worker"],
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_soft_time_limit=120,   # 2 min soft limit
        task_time_limit=300,        # 5 min hard kill
        worker_prefetch_multiplier=1,  # one task at a time per worker
        task_routes={
            "archonx.queue.worker.execute_agent_task": {"queue": "agents"},
            "archonx.queue.worker.run_cron_job": {"queue": "cron"},
        },
    )

    return app


celery_app = make_celery_app()


# ---------------------------------------------------------------------------
# Task definitions (only registered when Celery is available)
# ---------------------------------------------------------------------------

if _CELERY_AVAILABLE and celery_app:

    @celery_app.task(bind=True, name="archonx.queue.worker.execute_agent_task",
                     max_retries=2, default_retry_delay=10)
    def execute_agent_task(
        self: "Task",
        task_id: str,
        agent_id: str,
        prompt: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an AI agent task asynchronously.
        Returns result dict with: status, result, cost_usd, execution_ms.
        """
        start = time.monotonic()
        metadata = metadata or {}

        logger.info(f"[queue] Starting task {task_id} for agent {agent_id}")

        try:
            # Import kernel lazily to avoid circular imports
            from archonx.core.kernel import ArchonXKernel  # type: ignore
            kernel: ArchonXKernel = ArchonXKernel.get_instance()

            # Run the async kernel method in a sync context (Celery worker is sync)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result_text = loop.run_until_complete(
                    kernel.execute_task(agent_id, prompt, metadata)
                )
            finally:
                loop.close()

            elapsed_ms = int((time.monotonic() - start) * 1000)

            # Evaluate against goal function
            from archonx.paperclip import PaperclipEvaluator, TaskContext
            evaluator = PaperclipEvaluator(team=metadata.get("team", "white"))
            ctx = TaskContext(
                task_id=task_id,
                agent_id=agent_id,
                prompt=prompt,
                result=result_text,
                error=None,
                execution_time_ms=elapsed_ms,
                cost_usd=metadata.get("cost_usd", 0.0),
                token_count=metadata.get("token_count", 0),
            )
            reward = evaluator.evaluate(ctx)

            return {
                "status": "success",
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result_text,
                "execution_ms": elapsed_ms,
                "alignment_score": reward.alignment_score,
                "goal_met": reward.goal_met,
                "reward_value": reward.reward_value,
            }

        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"[queue] Task {task_id} failed: {exc}")

            try:
                raise self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                return {
                    "status": "failed",
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "error": str(exc),
                    "execution_ms": elapsed_ms,
                }

    @celery_app.task(name="archonx.queue.worker.run_cron_job")
    def run_cron_job(job_name: str) -> dict[str, Any]:
        """Execute a scheduled cron job by name."""
        from archonx.jobs.scheduler import run_job_by_name  # type: ignore
        start = time.monotonic()
        try:
            run_job_by_name(job_name)
            return {"status": "success", "job": job_name,
                    "elapsed_ms": int((time.monotonic() - start) * 1000)}
        except Exception as exc:
            logger.error(f"[queue] Cron job {job_name} failed: {exc}")
            return {"status": "failed", "job": job_name, "error": str(exc)}


# ---------------------------------------------------------------------------
# Synchronous fallback (used when Celery/Redis not available)
# ---------------------------------------------------------------------------

class SyncTaskRunner:
    """
    Drop-in replacement for Celery task dispatch when Redis is unavailable.
    Runs tasks synchronously in the same event loop.
    """

    async def execute_agent_task(
        self,
        task_id: str,
        agent_id: str,
        prompt: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata = metadata or {}
        start = time.monotonic()

        logger.warning(f"[queue] SYNC mode: running task {task_id} inline (no Celery)")

        try:
            from archonx.core.kernel import ArchonXKernel  # type: ignore
            kernel = ArchonXKernel.get_instance()
            result_text = await kernel.execute_task(agent_id, prompt, metadata)
            elapsed_ms = int((time.monotonic() - start) * 1000)

            return {
                "status": "success",
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result_text,
                "execution_ms": elapsed_ms,
            }
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"[queue] Sync task {task_id} failed: {exc}")
            return {
                "status": "failed",
                "task_id": task_id,
                "agent_id": agent_id,
                "error": str(exc),
                "execution_ms": elapsed_ms,
            }


# Singleton runner (used by routers)
_sync_runner = SyncTaskRunner()


def dispatch_task(
    task_id: str,
    agent_id: str,
    prompt: str,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """
    Dispatch a task to Celery (async) or sync runner.
    Returns AsyncResult if Celery is available, else a coroutine.
    """
    if _CELERY_AVAILABLE and celery_app:
        return execute_agent_task.apply_async(  # type: ignore[union-attr]
            args=[task_id, agent_id, prompt, metadata],
            task_id=task_id,
        )
    # Fallback: return coroutine to be awaited by caller
    return _sync_runner.execute_agent_task(task_id, agent_id, prompt, metadata)
