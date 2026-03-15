"""
Customer Support Skill
======================
Handle customer inquiries, tickets, escalations with AI-powered responses.
Supports multi-channel support and knowledge base integration.

Podcast use case: "automated customer support with escalation"
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.customer_support")


class TicketStatus(str, Enum):
    """Support ticket status."""
    NEW = "new"
    OPEN = "open"
    PENDING = "pending"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class TicketPriority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    """Ticket categories."""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"


@dataclass
class SupportTicket:
    """Support ticket data model."""
    ticket_id: str
    subject: str
    description: str
    customer_email: str
    customer_name: str
    status: TicketStatus = TicketStatus.NEW
    priority: TicketPriority = TicketPriority.MEDIUM
    category: TicketCategory = TicketCategory.GENERAL
    assigned_to: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    resolved_at: str | None = None
    first_response_at: str | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    sla_due: str | None = None
    customer_id: str | None = None
    order_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "subject": self.subject,
            "description": self.description,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "status": self.status.value,
            "priority": self.priority.value,
            "category": self.category.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "first_response_at": self.first_response_at,
            "messages": self.messages,
            "tags": self.tags,
            "sla_due": self.sla_due,
            "customer_id": self.customer_id,
            "order_id": self.order_id,
        }


# Knowledge base for common issues
KNOWLEDGE_BASE = {
    "password_reset": {
        "keywords": ["password", "reset", "login", "access", "forgot"],
        "response": "To reset your password, go to Settings > Security > Reset Password. You'll receive an email with a reset link valid for 24 hours.",
        "category": TicketCategory.ACCOUNT,
    },
    "billing_issue": {
        "keywords": ["billing", "charge", "payment", "invoice", "refund", "money"],
        "response": "I understand you have a billing concern. Let me look into your account. Can you provide your order ID or the date of the charge?",
        "category": TicketCategory.BILLING,
    },
    "technical_error": {
        "keywords": ["error", "bug", "crash", "not working", "broken", "failed"],
        "response": "I'm sorry to hear you're experiencing technical issues. Could you please describe the error message you're seeing and the steps that led to it?",
        "category": TicketCategory.TECHNICAL,
    },
    "feature_request": {
        "keywords": ["feature", "request", "suggestion", "wish", "would like"],
        "response": "Thank you for your feature suggestion! We value customer feedback and will pass this along to our product team for consideration.",
        "category": TicketCategory.FEATURE_REQUEST,
    },
    "account_deletion": {
        "keywords": ["delete", "remove", "cancel", "close account"],
        "response": "I can help you with account-related requests. To proceed with account deletion, please confirm your email address and reason for leaving.",
        "category": TicketCategory.ACCOUNT,
    },
}


class CustomerSupportSkill(BaseSkill):
    """Handle customer inquiries, tickets, and escalations."""

    name = "customer_support"
    description = "Handle customer inquiries, tickets, and escalations"
    category = SkillCategory.COMMUNICATION

    # SLA targets (hours)
    SLA_TARGETS = {
        TicketPriority.URGENT: 1,
        TicketPriority.HIGH: 4,
        TicketPriority.MEDIUM: 24,
        TicketPriority.LOW: 48,
    }

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Handle customer support actions.

        Params:
            action: 'respond' | 'create' | 'escalate' | 'resolve' | 'track' | 'classify' | 'suggest'
            ticket_id: Ticket ID for existing tickets
            ticket: Ticket data dict for create
            message: Customer message to respond to
            customer_email: Customer email address
            customer_name: Customer name
            subject: Ticket subject
            description: Ticket description
            priority: Ticket priority (low, medium, high, urgent)
            auto_respond: Whether to auto-respond (default: True)
            knowledge_base: Custom knowledge base dict (optional)
        """
        action = context.params.get("action", "respond")
        ticket_id = context.params.get("ticket_id", "")
        ticket_data = context.params.get("ticket", {})
        message = context.params.get("message", "")
        customer_email = context.params.get("customer_email", "")
        customer_name = context.params.get("customer_name", "")
        subject = context.params.get("subject", "")
        description = context.params.get("description", "")
        priority = context.params.get("priority", "medium")
        auto_respond = context.params.get("auto_respond", True)
        custom_kb = context.params.get("knowledge_base", {})

        try:
            if action == "create":
                result = await self._create_ticket(
                    customer_email, customer_name, subject, description,
                    priority, ticket_data, context
                )
            elif action == "respond":
                result = await self._respond_to_ticket(
                    ticket_id, message, auto_respond, custom_kb, context
                )
            elif action == "escalate":
                result = await self._escalate_ticket(ticket_id, context)
            elif action == "resolve":
                result = await self._resolve_ticket(ticket_id, context)
            elif action == "track":
                result = await self._track_ticket(ticket_id, context)
            elif action == "classify":
                result = await self._classify_ticket(message or description, custom_kb)
            elif action == "suggest":
                result = await self._suggest_response(message or description, custom_kb)
            else:
                return SkillResult(
                    skill=self.name,
                    status="error",
                    error=f"Unknown action: {action}",
                    data={"action": action}
                )

            return SkillResult(
                skill=self.name,
                status="success",
                data=result,
                metadata={
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("Customer support action failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"action": action}
            )

    async def _create_ticket(
        self,
        customer_email: str,
        customer_name: str,
        subject: str,
        description: str,
        priority: str,
        ticket_data: dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """Create a new support ticket."""
        # Generate ticket ID
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Parse priority
        try:
            ticket_priority = TicketPriority(priority.lower())
        except ValueError:
            ticket_priority = TicketPriority.MEDIUM

        # Calculate SLA due
        sla_hours = self.SLA_TARGETS[ticket_priority]
        sla_due = (datetime.utcnow() + timedelta(hours=sla_hours)).isoformat()

        # Auto-classify
        classification = await self._classify_ticket(description, {})

        # Create ticket
        ticket = SupportTicket(
            ticket_id=ticket_id,
            subject=subject or ticket_data.get("subject", "No subject"),
            description=description or ticket_data.get("description", ""),
            customer_email=customer_email or ticket_data.get("customer_email", ""),
            customer_name=customer_name or ticket_data.get("customer_name", ""),
            status=TicketStatus.NEW,
            priority=ticket_priority,
            category=TicketCategory(classification.get("category", "general")),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            sla_due=sla_due,
            customer_id=ticket_data.get("customer_id"),
            order_id=ticket_data.get("order_id"),
            tags=classification.get("tags", []),
        )

        return {
            "ticket": ticket.to_dict(),
            "message": f"Ticket {ticket_id} created successfully",
            "classification": classification,
            "sla_due": sla_due,
        }

    async def _respond_to_ticket(
        self,
        ticket_id: str,
        message: str,
        auto_respond: bool,
        custom_kb: dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """Respond to a support ticket."""
        # In production, fetch ticket from database
        # Mock ticket for demonstration
        ticket = SupportTicket(
            ticket_id=ticket_id,
            subject="Support Request",
            description=message,
            customer_email="customer@example.com",
            customer_name="Customer",
            status=TicketStatus.OPEN,
            created_at=datetime.utcnow().isoformat(),
        )

        response = ""
        suggested_actions = []

        if auto_respond:
            # Generate AI response
            suggestion = await self._suggest_response(message, custom_kb)
            response = suggestion.get("response", "")

            # Check if escalation is needed
            if suggestion.get("needs_escalation"):
                suggested_actions.append("escalate")
        else:
            response = "Thank you for contacting support. An agent will respond shortly."

        # Update ticket
        ticket.status = TicketStatus.PENDING
        ticket.updated_at = datetime.utcnow().isoformat()
        if not ticket.first_response_at:
            ticket.first_response_at = datetime.utcnow().isoformat()

        # Add message to ticket
        ticket.messages.append({
            "from": "customer",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        ticket.messages.append({
            "from": "support",
            "content": response,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "ticket_id": ticket_id,
            "response": response,
            "status": ticket.status.value,
            "suggested_actions": suggested_actions,
            "first_response_time": ticket.first_response_at,
        }

    async def _escalate_ticket(
        self,
        ticket_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Escalate a support ticket."""
        # In production, update database and notify team
        escalation_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"

        return {
            "ticket_id": ticket_id,
            "status": TicketStatus.ESCALATED.value,
            "escalation_id": escalation_id,
            "escalated_at": datetime.utcnow().isoformat(),
            "escalated_to": "senior_support",
            "message": f"Ticket {ticket_id} has been escalated to senior support",
        }

    async def _resolve_ticket(
        self,
        ticket_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Resolve a support ticket."""
        resolved_at = datetime.utcnow().isoformat()

        return {
            "ticket_id": ticket_id,
            "status": TicketStatus.RESOLVED.value,
            "resolved_at": resolved_at,
            "message": f"Ticket {ticket_id} has been resolved",
            "resolution_time": "2 hours",  # Mock - calculate from created_at in production
        }

    async def _track_ticket(
        self,
        ticket_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Track ticket status and metrics."""
        # Mock ticket data
        ticket = SupportTicket(
            ticket_id=ticket_id,
            subject="Support Request",
            description="Customer inquiry",
            customer_email="customer@example.com",
            customer_name="Customer",
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            created_at=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            sla_due=(datetime.utcnow() + timedelta(hours=22)).isoformat(),
        )

        # Calculate metrics
        created = datetime.fromisoformat(ticket.created_at)
        sla_deadline = datetime.fromisoformat(ticket.sla_due)
        time_remaining = sla_deadline - datetime.utcnow()

        return {
            "ticket": ticket.to_dict(),
            "metrics": {
                "time_open": str(datetime.utcnow() - created),
                "sla_time_remaining": str(time_remaining) if time_remaining.total_seconds() > 0 else "OVERDUE",
                "is_overdue": time_remaining.total_seconds() < 0,
                "message_count": len(ticket.messages),
            },
            "timeline": [
                {"event": "created", "timestamp": ticket.created_at},
                {"event": "status_changed", "status": "open", "timestamp": ticket.updated_at},
            ],
        }

    async def _classify_ticket(
        self,
        message: str,
        custom_kb: dict[str, Any]
    ) -> dict[str, Any]:
        """Classify a ticket based on message content."""
        message_lower = message.lower()

        # Merge knowledge bases
        kb = {**KNOWLEDGE_BASE, **custom_kb}

        # Find matching category
        best_match = None
        best_score = 0
        matched_keywords = []

        for category_key, category_data in kb.items():
            keywords = category_data.get("keywords", [])
            score = sum(1 for kw in keywords if kw in message_lower)

            if score > best_score:
                best_score = score
                best_match = category_key
                matched_keywords = [kw for kw in keywords if kw in message_lower]

        if best_match and best_score > 0:
            category = kb[best_match].get("category", TicketCategory.GENERAL)
            if isinstance(category, str):
                category = TicketCategory(category)
        else:
            category = TicketCategory.GENERAL

        # Determine priority based on keywords
        priority = TicketPriority.MEDIUM
        urgent_keywords = ["urgent", "emergency", "critical", "asap", "immediately"]
        high_keywords = ["important", "soon", "quickly", "broken", "down"]

        if any(kw in message_lower for kw in urgent_keywords):
            priority = TicketPriority.URGENT
        elif any(kw in message_lower for kw in high_keywords):
            priority = TicketPriority.HIGH

        return {
            "category": category.value,
            "priority": priority.value,
            "confidence": best_score / len(kb[best_match]["keywords"]) if best_match else 0,
            "matched_keywords": matched_keywords,
            "tags": matched_keywords[:5],
        }

    async def _suggest_response(
        self,
        message: str,
        custom_kb: dict[str, Any]
    ) -> dict[str, Any]:
        """Suggest a response based on the message."""
        # First classify the ticket
        classification = await self._classify_ticket(message, custom_kb)

        # Merge knowledge bases
        kb = {**KNOWLEDGE_BASE, **custom_kb}

        # Find best matching response
        message_lower = message.lower()
        best_response = None
        best_score = 0

        for category_key, category_data in kb.items():
            keywords = category_data.get("keywords", [])
            score = sum(1 for kw in keywords if kw in message_lower)

            if score > best_score:
                best_score = score
                best_response = category_data.get("response", "")

        if not best_response:
            best_response = "Thank you for contacting support. How can I help you today?"

        # Check for escalation triggers
        escalation_triggers = [
            "speak to manager",
            "legal",
            "lawsuit",
            "complaint",
            "unacceptable",
            "terrible service",
        ]
        needs_escalation = any(trigger in message_lower for trigger in escalation_triggers)

        return {
            "response": best_response,
            "classification": classification,
            "needs_escalation": needs_escalation,
            "confidence": classification.get("confidence", 0),
            "suggested_actions": ["escalate"] if needs_escalation else [],
        }

    def _calculate_sla_status(
        self,
        ticket: SupportTicket
    ) -> dict[str, Any]:
        """Calculate SLA status for a ticket."""
        if not ticket.sla_due:
            return {"status": "no_sla"}

        sla_deadline = datetime.fromisoformat(ticket.sla_due)
        time_remaining = sla_deadline - datetime.utcnow()

        if time_remaining.total_seconds() < 0:
            return {
                "status": "breached",
                "overdue_by": str(abs(time_remaining)),
            }
        elif time_remaining.total_seconds() < 3600:  # Less than 1 hour
            return {
                "status": "at_risk",
                "time_remaining": str(time_remaining),
            }
        else:
            return {
                "status": "on_track",
                "time_remaining": str(time_remaining),
            }
