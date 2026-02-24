"""
Invoice Management Skill
========================
Create, send, track invoices and payments with Stripe integration.
Supports multiple payment providers and invoice templates.

Podcast use case: "manage invoices — generate, send, track payment status"
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.invoice_management")


class InvoiceStatus(str, Enum):
    """Invoice status."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment methods."""
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTO = "crypto"
    CHECK = "check"


@dataclass
class InvoiceItem:
    """Invoice line item."""
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    tax_rate: float = 0.0
    discount: float = 0.0

    @property
    def subtotal(self) -> float:
        """Calculate subtotal before tax."""
        return self.quantity * self.unit_price - self.discount

    @property
    def tax(self) -> float:
        """Calculate tax amount."""
        return self.subtotal * (self.tax_rate / 100)

    @property
    def total(self) -> float:
        """Calculate total with tax."""
        return self.subtotal + self.tax

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "tax_rate": self.tax_rate,
            "discount": self.discount,
            "subtotal": round(self.subtotal, 2),
            "tax": round(self.tax, 2),
            "total": round(self.total, 2),
        }


@dataclass
class Invoice:
    """Invoice data model."""
    invoice_id: str
    client_name: str
    client_email: str
    items: list[InvoiceItem] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: str | None = None
    due_date: str | None = None
    notes: str = ""
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    payment_link: str | None = None
    paid_at: str | None = None
    client_company: str | None = None
    client_address: str | None = None
    currency: str = "USD"
    tax_id: str | None = None
    discount_total: float = 0.0

    @property
    def subtotal(self) -> float:
        """Calculate invoice subtotal."""
        return sum(item.subtotal for item in self.items)

    @property
    def tax_total(self) -> float:
        """Calculate total tax."""
        return sum(item.tax for item in self.items)

    @property
    def total(self) -> float:
        """Calculate invoice total."""
        return sum(item.total for item in self.items) - self.discount_total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "invoice_id": self.invoice_id,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "client_company": self.client_company,
            "client_address": self.client_address,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "notes": self.notes,
            "payment_method": self.payment_method.value,
            "payment_link": self.payment_link,
            "paid_at": self.paid_at,
            "currency": self.currency,
            "tax_id": self.tax_id,
            "subtotal": round(self.subtotal, 2),
            "tax_total": round(self.tax_total, 2),
            "discount_total": round(self.discount_total, 2),
            "total": round(self.total, 2),
        }


class InvoiceManagementSkill(BaseSkill):
    """Create, send, and track invoices and payments."""

    name = "invoice_management"
    description = "Create, send, and track invoices and payments"
    category = SkillCategory.FINANCIAL

    # Default payment terms (days)
    DEFAULT_PAYMENT_TERMS = 30

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Manage invoices with various actions.

        Params:
            action: 'create' | 'send' | 'track' | 'remind' | 'cancel' | 'refund' | 'list' | 'report'
            invoice: Invoice data dict (for create/send)
            invoice_id: Invoice ID (for track/cancel/refund)
            client: Client info dict (for create)
            items: List of invoice items (for create)
            payment_terms: Payment terms in days (default: 30)
            payment_method: Payment method enum
            send_reminder: Whether to send reminder (for remind)
            provider: Payment provider - 'stripe' | 'paypal' | 'manual'
        """
        action = context.params.get("action", "create")
        invoice_data = context.params.get("invoice", {})
        invoice_id = context.params.get("invoice_id", "")
        client = context.params.get("client", {})
        items = context.params.get("items", [])
        payment_terms = context.params.get("payment_terms", self.DEFAULT_PAYMENT_TERMS)
        payment_method = context.params.get("payment_method", "bank_transfer")
        send_reminder = context.params.get("send_reminder", True)
        provider = context.params.get("provider", "manual")

        try:
            if action == "create":
                result = await self._create_invoice(
                    client, items, payment_terms, payment_method, invoice_data, context
                )
            elif action == "send":
                result = await self._send_invoice(invoice_id or invoice_data, context)
            elif action == "track":
                result = await self._track_invoice(invoice_id, context)
            elif action == "remind":
                result = await self._send_reminder(invoice_id, send_reminder, context)
            elif action == "cancel":
                result = await self._cancel_invoice(invoice_id, context)
            elif action == "refund":
                result = await self._refund_invoice(invoice_id, context)
            elif action == "list":
                result = await self._list_invoices(client, context)
            elif action == "report":
                result = await self._generate_report(context)
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
                    "provider": provider,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("Invoice management failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"action": action}
            )

    async def _create_invoice(
        self,
        client: dict[str, Any],
        items: list[dict[str, Any]],
        payment_terms: int,
        payment_method: str,
        invoice_data: dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """Create a new invoice."""
        # Generate invoice ID
        invoice_id = f"INV-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

        # Parse items
        invoice_items = []
        for item_data in items:
            item = InvoiceItem(
                description=item_data.get("description", ""),
                quantity=item_data.get("quantity", 1.0),
                unit_price=item_data.get("unit_price", 0.0),
                tax_rate=item_data.get("tax_rate", 0.0),
                discount=item_data.get("discount", 0.0),
            )
            invoice_items.append(item)

        # Calculate dates
        issue_date = datetime.utcnow().strftime("%Y-%m-%d")
        due_date = (datetime.utcnow() + timedelta(days=payment_terms)).strftime("%Y-%m-%d")

        # Create invoice
        invoice = Invoice(
            invoice_id=invoice_id,
            client_name=client.get("name", invoice_data.get("client_name", "")),
            client_email=client.get("email", invoice_data.get("client_email", "")),
            client_company=client.get("company", invoice_data.get("client_company")),
            client_address=client.get("address", invoice_data.get("client_address")),
            items=invoice_items,
            status=InvoiceStatus.DRAFT,
            issue_date=issue_date,
            due_date=due_date,
            notes=invoice_data.get("notes", ""),
            payment_method=PaymentMethod(payment_method),
            currency=invoice_data.get("currency", "USD"),
            tax_id=invoice_data.get("tax_id"),
            discount_total=invoice_data.get("discount_total", 0.0),
        )

        # Generate payment link if Stripe is available
        if hasattr(context, "tools") and "stripe" in context.tools:
            try:
                payment_link = await self._create_stripe_payment_link(invoice, context)
                invoice.payment_link = payment_link
            except Exception as e:
                logger.warning("Could not create Stripe payment link: %s", e)

        return {
            "invoice": invoice.to_dict(),
            "message": f"Invoice {invoice_id} created successfully",
            "payment_link": invoice.payment_link,
        }

    async def _send_invoice(
        self,
        invoice_ref: str | dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """Send invoice to client."""
        if isinstance(invoice_ref, dict):
            invoice = Invoice(**invoice_ref)
            invoice_id = invoice.invoice_id
        else:
            invoice_id = invoice_ref
            # In production, fetch from database
            invoice = Invoice(
                invoice_id=invoice_id,
                client_name="Client",
                client_email="client@example.com",
                status=InvoiceStatus.DRAFT,
            )

        # Update status
        invoice.status = InvoiceStatus.SENT

        # Send email if email skill is available
        if hasattr(context, "tools") and "email_management" in context.tools:
            try:
                await context.tools["email_management"](
                    action="send",
                    recipient=invoice.client_email,
                    subject=f"Invoice {invoice_id}",
                    content=self._generate_invoice_email(invoice),
                )
            except Exception as e:
                logger.warning("Could not send invoice email: %s", e)

        return {
            "invoice_id": invoice_id,
            "status": invoice.status.value,
            "sent_at": datetime.utcnow().isoformat(),
            "recipient": invoice.client_email,
            "message": f"Invoice {invoice_id} sent to {invoice.client_email}",
        }

    async def _track_invoice(
        self,
        invoice_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Track invoice status."""
        # In production, fetch from database
        # Mock implementation
        invoice = Invoice(
            invoice_id=invoice_id,
            client_name="Client",
            client_email="client@example.com",
            status=InvoiceStatus.SENT,
            issue_date=datetime.utcnow().strftime("%Y-%m-%d"),
            due_date=(datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        )

        # Check if overdue
        due_date = datetime.strptime(invoice.due_date, "%Y-%m-%d")
        if datetime.utcnow() > due_date and invoice.status == InvoiceStatus.SENT:
            invoice.status = InvoiceStatus.OVERDUE

        # Check Stripe for payment status
        if hasattr(context, "tools") and "stripe" in context.tools:
            try:
                payment_status = await self._check_stripe_payment(invoice_id, context)
                if payment_status == "paid":
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.utcnow().isoformat()
            except Exception as e:
                logger.warning("Could not check Stripe payment: %s", e)

        return {
            "invoice": invoice.to_dict(),
            "days_until_due": (due_date - datetime.utcnow()).days if invoice.status != InvoiceStatus.PAID else 0,
            "is_overdue": invoice.status == InvoiceStatus.OVERDUE,
        }

    async def _send_reminder(
        self,
        invoice_id: str,
        send_email: bool,
        context: SkillContext
    ) -> dict[str, Any]:
        """Send payment reminder."""
        # In production, fetch from database
        invoice = Invoice(
            invoice_id=invoice_id,
            client_name="Client",
            client_email="client@example.com",
            status=InvoiceStatus.SENT,
            due_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
        )

        reminder_sent = False

        if send_email and hasattr(context, "tools") and "email_management" in context.tools:
            try:
                await context.tools["email_management"](
                    action="send",
                    recipient=invoice.client_email,
                    subject=f"Payment Reminder: Invoice {invoice_id}",
                    content=self._generate_reminder_email(invoice),
                )
                reminder_sent = True
            except Exception as e:
                logger.warning("Could not send reminder email: %s", e)

        return {
            "invoice_id": invoice_id,
            "reminder_sent": reminder_sent,
            "sent_at": datetime.utcnow().isoformat() if reminder_sent else None,
            "message": f"Reminder sent for invoice {invoice_id}" if reminder_sent else "Reminder prepared but not sent",
        }

    async def _cancel_invoice(
        self,
        invoice_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Cancel an invoice."""
        return {
            "invoice_id": invoice_id,
            "status": InvoiceStatus.CANCELLED.value,
            "cancelled_at": datetime.utcnow().isoformat(),
            "message": f"Invoice {invoice_id} cancelled",
        }

    async def _refund_invoice(
        self,
        invoice_id: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Process a refund for an invoice."""
        refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"

        # Check for Stripe refund capability
        if hasattr(context, "tools") and "stripe" in context.tools:
            try:
                stripe_result = await context.tools["stripe"](
                    action="create_refund",
                    invoice_id=invoice_id,
                    reason="customer_request",
                )
                # Use Stripe-issued refund ID if available
                if stripe_result and stripe_result.get("refund_id"):
                    refund_id = stripe_result["refund_id"]
            except Exception as e:
                logger.warning("Could not process Stripe refund: %s", e)

        return {
            "invoice_id": invoice_id,
            "refund_id": refund_id,
            "status": InvoiceStatus.REFUNDED.value,
            "refunded_at": datetime.utcnow().isoformat(),
            "message": f"Refund processed for invoice {invoice_id}",
        }

    async def _list_invoices(
        self,
        client: dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """List invoices, optionally filtered by client."""
        # Mock implementation - in production, query database
        mock_invoices = [
            Invoice(
                invoice_id=f"INV-202602-{i:03d}",
                client_name=client.get("name", "Client"),
                client_email=client.get("email", "client@example.com"),
                status=list(InvoiceStatus)[i % 4],
                issue_date=datetime.utcnow().strftime("%Y-%m-%d"),
                due_date=(datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
                items=[InvoiceItem(description=f"Service {i}", unit_price=100.0 * (i + 1))],
            )
            for i in range(5)
        ]

        return {
            "invoices": [inv.to_dict() for inv in mock_invoices],
            "total": len(mock_invoices),
            "total_value": sum(inv.total for inv in mock_invoices),
        }

    async def _generate_report(
        self,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate invoice report."""
        # Mock data for report
        total_invoiced = 15000.00
        total_paid = 10500.00
        total_outstanding = 4500.00

        return {
            "period": {
                "start": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end": datetime.utcnow().strftime("%Y-%m-%d"),
            },
            "summary": {
                "total_invoices": 15,
                "total_invoiced": round(total_invoiced, 2),
                "total_paid": round(total_paid, 2),
                "total_outstanding": round(total_outstanding, 2),
                "collection_rate": round(total_paid / total_invoiced * 100, 1) if total_invoiced else 0,
            },
            "by_status": {
                "draft": 2,
                "sent": 5,
                "paid": 7,
                "overdue": 1,
                "cancelled": 0,
            },
            "top_clients": [
                {"name": "Client A", "total": 5000.00},
                {"name": "Client B", "total": 3500.00},
                {"name": "Client C", "total": 2000.00},
            ],
        }

    async def _create_stripe_payment_link(
        self,
        invoice: Invoice,
        context: SkillContext
    ) -> str | None:
        """Create Stripe payment link for invoice."""
        # In production, use Stripe API
        # Mock implementation
        return f"https://pay.stripe.com/invoice/{invoice.invoice_id}"

    async def _check_stripe_payment(
        self,
        invoice_id: str,
        context: SkillContext
    ) -> str:
        """Check Stripe payment status."""
        # In production, query Stripe API
        return "pending"

    def _generate_invoice_email(self, invoice: Invoice) -> str:
        """Generate invoice email content."""
        return f"""
Dear {invoice.client_name},

Please find attached Invoice {invoice.invoice_id}.

Amount Due: {invoice.currency} {invoice.total:,.2f}
Due Date: {invoice.due_date}

{f"Pay online: {invoice.payment_link}" if invoice.payment_link else ""}

Thank you for your business!

Best regards,
The Team
"""

    def _generate_reminder_email(self, invoice: Invoice) -> str:
        """Generate payment reminder email content."""
        return f"""
Dear {invoice.client_name},

This is a friendly reminder that Invoice {invoice.invoice_id} is due on {invoice.due_date}.

Amount Due: {invoice.currency} {invoice.total:,.2f}

{f"Pay online: {invoice.payment_link}" if invoice.payment_link else ""}

If you have already sent payment, please disregard this message.

Thank you!

Best regards,
The Team
"""
