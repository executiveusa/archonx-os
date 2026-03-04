import asyncio

from archonx.automation.self_improvement import DailySelfImprovement


class _ProcResult:
    def __init__(self, returncode=0, stdout="ok", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_self_improvement_handlers_execute(monkeypatch):
    improvement = DailySelfImprovement()

    def fake_run(*_args, **_kwargs):
        return _ProcResult()

    monkeypatch.setattr("subprocess.run", fake_run)

    quality = asyncio.run(improvement._run_code_quality())
    assert quality["status"] == "success"
    assert quality["health"]["tests_passed"] is True

    perf = asyncio.run(improvement._run_performance_optimization())
    assert perf["status"] == "success"

    knowledge = asyncio.run(improvement._run_knowledge_extraction())
    assert knowledge["status"] == "success"
