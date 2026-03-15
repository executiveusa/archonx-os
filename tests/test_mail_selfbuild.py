"""
Tests — Agent Mail + Self-Build Directive
"""

import asyncio
from archonx.core.agent_mail import AgentMailbox, AgentMessage, MessageType
from archonx.core.self_build import SelfBuildDirective, SelfBuildReport


# ==================== Agent Mailbox ====================


def test_send_and_read() -> None:
    mb = AgentMailbox()
    msg = mb.send("agent_a", "agent_b", MessageType.REQUEST, "Help needed", {"data": "test"})
    assert msg.id == "mail-000001"
    msgs = mb.read("agent_b")
    assert len(msgs) == 1
    assert msgs[0].subject == "Help needed"
    assert msgs[0].read


def test_read_marks_as_read() -> None:
    mb = AgentMailbox()
    mb.send("a", "b", MessageType.REQUEST, "Test")
    mb.read("b")  # marks as read
    unread = mb.read("b", unread_only=True)
    assert len(unread) == 0


def test_read_all_includes_read() -> None:
    mb = AgentMailbox()
    mb.send("a", "b", MessageType.REQUEST, "Test")
    mb.read("b")  # marks as read
    all_msgs = mb.read("b", unread_only=False)
    assert len(all_msgs) == 1


def test_broadcast_delivers_to_all() -> None:
    mb = AgentMailbox()
    # Pre-create inboxes by sending direct messages first
    mb.send("sys", "agent_1", MessageType.ALERT, "init")
    mb.send("sys", "agent_2", MessageType.ALERT, "init")
    mb.read("agent_1")  # clear
    mb.read("agent_2")  # clear
    # Now broadcast
    mb.send("sys", "broadcast", MessageType.BROADCAST, "System update", {"version": "2.0"})
    for agent_id in ("agent_1", "agent_2"):
        msgs = mb.read(agent_id, unread_only=False)
        broadcasts = [m for m in msgs if m.message_type == MessageType.BROADCAST]
        assert len(broadcasts) == 1


def test_crew_message() -> None:
    mb = AgentMailbox()
    mb.send("king", "crew:white", MessageType.BROADCAST, "White crew rally")
    msgs = mb.read("crew:white")
    assert len(msgs) == 1
    assert msgs[0].subject == "White crew rally"


def test_reply_to() -> None:
    mb = AgentMailbox()
    original = mb.send("a", "b", MessageType.REQUEST, "Question?")
    reply = mb.send("b", "a", MessageType.RESPONSE, "Answer!", reply_to=original.id)
    assert reply.reply_to == original.id


def test_flywheel_message_type() -> None:
    mb = AgentMailbox()
    msg = mb.send("flywheel", "agent_a", MessageType.FLYWHEEL, "New improvement", {"imp_id": "imp-00001"})
    assert msg.message_type == MessageType.FLYWHEEL


def test_stats() -> None:
    mb = AgentMailbox()
    mb.send("a", "b", MessageType.REQUEST, "msg1")
    mb.send("a", "c", MessageType.REQUEST, "msg2")
    mb.read("b")
    stats = mb.stats
    assert stats["total_messages"] == 2
    assert stats["unread"] == 1  # "c" hasn't read yet


# ==================== Self-Build Directive ====================


def test_generate_report_success() -> None:
    sbd = SelfBuildDirective()
    report = sbd.generate_report("agent_1", "task_1", {"status": "ok", "via": "skill"})
    assert report.execution_quality == 0.9
    assert len(report.improvements_found) == 0


def test_generate_report_placeholder_flags_gap() -> None:
    sbd = SelfBuildDirective()
    report = sbd.generate_report("agent_1", "task_1", {"via": "placeholder", "subtask": "quantum"})
    assert report.execution_quality == 0.5
    assert len(report.improvements_found) >= 1
    assert "quantum" in report.skills_needed


def test_generate_report_error() -> None:
    sbd = SelfBuildDirective()
    report = sbd.generate_report("agent_1", "task_1", {"status": "error"})
    assert report.execution_quality == 0.2
    assert len(report.improvements_found) >= 1


def test_slow_execution_flagged() -> None:
    sbd = SelfBuildDirective()
    report = sbd.generate_report("agent_1", "task_1", {"status": "ok"}, time_taken_ms=10000)
    bottlenecks = report.bottlenecks
    assert len(bottlenecks) >= 1
    assert "10000" in bottlenecks[0]


def test_average_quality() -> None:
    sbd = SelfBuildDirective()
    sbd.generate_report("a", "t1", {"via": "skill"})   # 0.9
    sbd.generate_report("a", "t2", {"via": "placeholder", "subtask": "x"})  # 0.5
    avg = sbd.average_quality
    assert 0.6 < avg < 0.8


def test_total_improvements_found() -> None:
    sbd = SelfBuildDirective()
    sbd.generate_report("a", "t1", {"status": "error"})
    sbd.generate_report("a", "t2", {"via": "placeholder", "subtask": "x"})
    assert sbd.total_improvements_found >= 2


def test_stats() -> None:
    sbd = SelfBuildDirective()
    sbd.generate_report("a", "t1", {"via": "skill"})
    stats = sbd.stats
    assert stats["total_reports"] == 1
    assert stats["average_quality"] == 0.9
    assert isinstance(stats["skill_gaps"], list)


def test_empty_stats() -> None:
    sbd = SelfBuildDirective()
    assert sbd.average_quality == 0.0
    assert sbd.total_improvements_found == 0
