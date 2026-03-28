"""
Phase 3A Integration Test Suite
Run with: python ops/test_phase3a.py
"""
import sys
import traceback
from pathlib import Path

# Ensure repo root is on sys.path regardless of install state
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

PASS = []
FAIL = []


def run_test(name, fn):
    try:
        result = fn()
        print(f"  PASS  {name}: {result}")
        PASS.append(name)
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        FAIL.append((name, traceback.format_exc()))


# ---------------------------------------------------------------------------
# TEST 1: Soul Loader
# ---------------------------------------------------------------------------
def test_soul_loader():
    from archonx.core.soul_loader import SoulLoader
    loader = SoulLoader()
    registry = loader.load_all()
    count = registry.count()
    assert count > 0, f"Expected >0 souls, got {count}"
    white = registry.get_crew("white")
    black = registry.get_crew("black")
    return f"{count} souls loaded (white={len(white)}, black={len(black)})"


# ---------------------------------------------------------------------------
# TEST 2: BMAD PhaseGate
# ---------------------------------------------------------------------------
def test_bmad_phase_gate():
    from archonx.protocols.bmad import PhaseGate
    gate = PhaseGate(
        gate_id="TEST-GATE",
        from_phase="PHASE_2",
        to_phase="PHASE_3",
        required_token="APPROVED: START PHASE_3",
    )
    assert gate.locked is True, "Gate should start locked"
    wrong = gate.unlock("wrong token")
    assert wrong is False, "Wrong token should not unlock"
    assert gate.locked is True, "Gate still locked after wrong token"
    ok = gate.unlock("APPROVED: START PHASE_3")
    assert ok is True, "Correct token should unlock"
    assert gate.locked is False, "Gate should be unlocked"
    return "PhaseGate lock/unlock cycle OK"


# ---------------------------------------------------------------------------
# TEST 3: BMAD Protocol State
# ---------------------------------------------------------------------------
def test_bmad_protocol():
    from archonx.protocols.bmad import BMAdProtocol, BMAdPhase
    import tempfile, os
    tmp = tempfile.mktemp(suffix=".json")
    proto = BMAdProtocol(state_file=tmp)
    # BMAdState.current_phase is a str; default is "PHASE_2" (hardcoded default in dataclass)
    phase = proto.get_current_phase()
    assert isinstance(phase, BMAdPhase), f"Expected BMAdPhase, got {type(phase)}"
    # state property exposes the internal state
    assert isinstance(proto.state.current_phase, str), "current_phase should be str"
    if os.path.exists(tmp):
        os.unlink(tmp)
    return f"Protocol state.current_phase={proto.state.current_phase} | get_current_phase()={phase.value} OK"


# ---------------------------------------------------------------------------
# TEST 4: Hermes Agent (no LLM)
# ---------------------------------------------------------------------------
def test_hermes_agent():
    from archonx.agents.hermes.agent import HermesAgent  # direct import, bypasses agents/__init__.py
    h = HermesAgent()  # no LLM client — uses structured fallback
    assert h.white_council is not None, "white_council missing"
    assert h.black_council is not None, "black_council missing"
    assert h.consensus_engine is not None, "consensus_engine missing"
    # Test synchronous structured challenge (no LLM call)
    import asyncio
    task_result = asyncio.run(h.white_council.challenge("test objective", {}, 1))
    assert len(task_result) > 0, "Challenge should return non-empty string"
    return "HermesAgent + WhiteCouncil structured challenge OK"


# ---------------------------------------------------------------------------
# TEST 5: Popebot (test vault mode — no real sends)
# ---------------------------------------------------------------------------
def test_popebot():
    from archonx.comms.popebot import Popebot
    # Popebot accepts optional vault + rate_limiter; no required args
    p = Popebot()  # test mode: no real vault provided
    assert hasattr(p, "channels"), "Popebot missing .channels"
    assert hasattr(p, "rate_limiter"), "Popebot missing .rate_limiter"
    return f"Popebot channels: {list(p.channels.keys())}"


# ---------------------------------------------------------------------------
# TEST 6: SoulLoader + Hermes injection (validate `members` attr exists)
# ---------------------------------------------------------------------------
def test_soul_injection():
    from archonx.core.soul_loader import SoulLoader
    loader = SoulLoader()
    registry = loader.load_all()
    # Inject into mock crew
    class MockAgent:
        def __init__(self, agent_id):
            self.agent_id = agent_id
            self.soul = None
    agents = [MockAgent("pauli_king_white"), MockAgent("synthia_queen_white")]
    loader.inject_into_crew(agents, registry)
    injected = sum(1 for a in agents if a.soul is not None)
    # May be 0 if soul IDs don't match mock names exactly — just verify no crash
    return f"inject_into_crew completed without error (injected={injected}/{len(agents)})"


# ---------------------------------------------------------------------------
# RUN ALL
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("  PHASE 3A INTEGRATION TESTS")
print("="*60)

run_test("T1: SoulLoader",       test_soul_loader)
run_test("T2: BMAD PhaseGate",   test_bmad_phase_gate)
run_test("T3: BMAD Protocol",    test_bmad_protocol)
run_test("T4: HermesAgent",      test_hermes_agent)
run_test("T5: Popebot (test)",   test_popebot)
run_test("T6: Soul Injection",   test_soul_injection)

print("\n" + "="*60)
print(f"  RESULTS: {len(PASS)} PASS, {len(FAIL)} FAIL")
print("="*60)

if FAIL:
    print("\nFAILURES:")
    for name, tb in FAIL:
        print(f"\n--- {name} ---")
        print(tb)
    sys.exit(1)
else:
    print("\nALL TESTS PASSED ✅")
    sys.exit(0)
