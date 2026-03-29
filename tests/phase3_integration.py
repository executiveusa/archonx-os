"""Phase 3 Production Integration Tests -- ARCHON-X OS"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0
ERRORS = []

def test(name, fn):
    global PASS, FAIL, ERRORS
    try:
        fn()
        PASS += 1
        print(f"  PASS {name}")
    except Exception as e:
        FAIL += 1
        ERRORS.append((name, str(e)))
        print(f"  FAIL {name}: {e}")

# T1: Soul Loader — SoulRegistry.all() returns list
def t1():
    from archonx.core.soul_loader import SoulLoader
    loader = SoulLoader()
    registry = loader.load_all()
    souls = registry.all()
    assert len(souls) >= 30, f"Expected 30+ souls, got {len(souls)}"
test("T1: SoulLoader", t1)

# T2: BMAD PhaseGate — dataclass with required_token
def t2():
    from archonx.protocols.bmad import PhaseGate
    gate = PhaseGate(
        gate_id="test-gate",
        from_phase="PHASE_1",
        to_phase="PHASE_2",
        required_token="APPROVED: START PHASE_2",
    )
    assert gate.locked is True
    result = gate.unlock("APPROVED: START PHASE_2")
    assert result is True, "PhaseGate unlock failed"
    assert gate.locked is False
test("T2: BMAD PhaseGate", t2)

# T3: BMAD State
def t3():
    from archonx.protocols.bmad import BMAdProtocol
    proto = BMAdProtocol(state_file=".archonx/bmad_state_test.json")
    phase = proto.get_current_phase()
    assert phase is not None, "No current phase"
test("T3: BMAD Protocol State", t3)

# T4: Hermes WhiteCouncil — async challenge(objective, context, round_num)
def t4():
    from archonx.agents.hermes.white_council import WhiteCouncil
    wc = WhiteCouncil()
    result = asyncio.run(wc.challenge("test objective", {"task": "test"}, 1))
    assert isinstance(result, str), f"Expected str, got {type(result)}"
test("T4: WhiteCouncil", t4)

# T5: Popebot Channels — vault kwarg, not vault_mode
def t5():
    from archonx.comms.popebot import Popebot
    bot = Popebot(vault=None)
    assert len(bot.channels) >= 5, f"Expected 5 channels, got {len(bot.channels)}"
test("T5: Popebot Channels", t5)

# T6: Soul Injection — inject_into_crew(crew_agents, registry)
def t6():
    from archonx.core.soul_loader import SoulLoader
    loader = SoulLoader()
    registry = loader.load_all()
    loader.inject_into_crew([], registry)
test("T6: Soul Injection", t6)

# T7: V1 Router Package — named v1_router not router
def t7():
    from archonx.api.v1 import v1_router
    route_count = len(v1_router.routes)
    assert route_count >= 20, f"Expected 20+ routes, got {route_count}"
test("T7: V1 Router Package", t7)

# T8: Server create_app
def t8():
    from archonx.server import create_app
    app = create_app()
    assert app is not None, "create_app returned None"
    route_paths = [r.path for r in app.routes]
    assert any("/v1/" in p for p in route_paths), f"No /v1/ routes found in {route_paths[:10]}"
test("T8: Server create_app", t8)

# T9: Health endpoint exists
def t9():
    from archonx.server import create_app
    app = create_app()
    route_paths = [r.path for r in app.routes]
    assert any("health" in p for p in route_paths), f"No health route"
test("T9: Health Endpoint", t9)

# T10: ConX Auth function exists
def t10():
    from archonx.api.v1.conx import _verify_conx_auth
    assert callable(_verify_conx_auth), "_verify_conx_auth not callable"
test("T10: ConX Auth", t10)

# Cleanup
try:
    os.remove(".archonx/bmad_state_test.json")
except Exception:
    pass

print(f"\n{'='*40}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
if ERRORS:
    print(f"\nFAILURES:")
    for name, err in ERRORS:
        print(f"  - {name}: {err}")
print(f"{'='*40}")
sys.exit(0 if FAIL == 0 else 1)
