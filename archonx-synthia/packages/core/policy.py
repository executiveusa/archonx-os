"""Policy engine — tool allowlisting, approval gating, budget enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field

# Actions that ALWAYS require human approval
APPROVAL_REQUIRED_ACTIONS = frozenset(
    {
        "send_email",
        "send_message",
        "post_publish",
        "calendar_invite_external",
        "payment_checkout",
        "delete_production_data",
        "transfer_funds",
    }
)

# Default tool allowlist
DEFAULT_TOOL_ALLOWLIST = frozenset(
    {
        "notion.query_tasks",
        "notion.create_task",
        "notion.update_task",
        "notion.create_run",
        "notion.append_run_log",
        "notion.create_artifact",
        "notion.create_approval_request",
        "notion.resolve_approval_request",
        "orgo.create_computer",
        "orgo.destroy_computer",
        "orgo.get_computer_status",
        "orgo.screenshot",
        "orgo.input",
        "orgo.open_url",
        "runner.exec",
        "runner.put_file",
        "runner.get_file",
        "voice.say",
        "voice.transcribe_callback",
        "policy.request_approval",
        "policy.check_allowlist",
    }
)

# Default domain egress allowlist
DEFAULT_EGRESS_ALLOWLIST = frozenset(
    {
        "api.notion.com",
        "api.orgo.ai",
        "api.z.ai",
        "api.twilio.com",
    }
)


@dataclass
class PolicyViolation:
    code: str
    message: str
    tool_name: str = ""
    domain: str = ""


@dataclass
class PolicyEngine:
    tool_allowlist: frozenset[str] = DEFAULT_TOOL_ALLOWLIST
    egress_allowlist: frozenset[str] = DEFAULT_EGRESS_ALLOWLIST
    violations: list[PolicyViolation] = field(default_factory=list)

    def check_tool_allowed(self, tool_name: str) -> bool:
        if tool_name not in self.tool_allowlist:
            self.violations.append(
                PolicyViolation(
                    code="TOOL_NOT_ALLOWED",
                    message=f"Tool '{tool_name}' not in allowlist",
                    tool_name=tool_name,
                )
            )
            return False
        return True

    def check_requires_approval(self, action: str) -> bool:
        return action in APPROVAL_REQUIRED_ACTIONS

    def check_egress_allowed(self, domain: str) -> bool:
        if domain not in self.egress_allowlist:
            self.violations.append(
                PolicyViolation(
                    code="EGRESS_BLOCKED",
                    message=f"Domain '{domain}' not in egress allowlist",
                    domain=domain,
                )
            )
            return False
        return True
