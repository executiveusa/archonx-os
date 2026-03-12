"""Tests for canonical worker registry."""

from archonx.orchestration import (
    WorkerKind,
    build_default_worker_registry,
)


def test_default_worker_registry_contains_canonical_workers() -> None:
    registry = build_default_worker_registry()
    worker_ids = [worker.worker_id for worker in registry.list_all()]

    assert "darya_openhands" in worker_ids
    assert "agency_agents" in worker_ids
    assert "agent_zero" in worker_ids
    assert "goose" in worker_ids
    assert "ralphy" in worker_ids


def test_worker_registry_finds_workers_by_intent() -> None:
    registry = build_default_worker_registry()

    code_change_workers = registry.find_by_intent("code_change")
    assert [worker.worker_id for worker in code_change_workers] == [
        "darya_openhands"
    ]

    cloud_workers = registry.find_by_intent("cloud_coding")
    assert [worker.worker_id for worker in cloud_workers] == ["goose"]


def test_worker_registry_enforces_controller_boundary() -> None:
    registry = build_default_worker_registry()

    assert registry.validate_controller_boundary() == []
    assert registry.get("agency_agents").kind == WorkerKind.MULTI_AGENT
