"""
Revenue Engine
==============
Proactive revenue-generating system for $100M goal.

Features:
- Lead generation pipeline
- Client acquisition automation
- Billing automation
- Revenue forecasting
- Proactive outreach

BEAD-007: Revenue Generation System Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("archonx.revenue.engine")


class LeadStatus(str, Enum):
    """Lead status in the pipeline."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadSource(str, Enum):
    """Source of the lead."""
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_OUTREACH = "cold_outreach"
    SOCIAL_MEDIA = "social_media"
    PAID_ADS = "paid_ads"
    ORGANIC = "organic"
    API_INTEGRATION = "api_integration"
    MARKETPLACE = "marketplace"


class RevenueSource(str, Enum):
    """Revenue source categories."""
    CONSULTING = "consulting"
    SAAS = "saas"
    API_ACCESS = "api_access"
    CUSTOM_DEVELOPMENT = "custom_development"
    SUPPORT = "support"
    TRAINING = "training"
    ENTERPRISE = "enterprise"
    WHITE_LABEL = "white_label"


class ClientTier(str, Enum):
    """Client tier levels."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class Lead:
    """A sales lead."""
    lead_id: str
    company_name: str
    contact_name: str
    contact_email: str
    source: LeadSource
    status: LeadStatus = LeadStatus.NEW
    estimated_value: float = 0.0
    probability: float = 0.0  # 0.0 - 1.0
    notes: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    assigned_agent: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "source": self.source.value,
            "status": self.status.value,
            "estimated_value": self.estimated_value,
            "probability": self.probability,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_agent": self.assigned_agent,
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lead:
        return cls(
            lead_id=data["lead_id"],
            company_name=data["company_name"],
            contact_name=data["contact_name"],
            contact_email=data["contact_email"],
            source=LeadSource(data["source"]),
            status=LeadStatus(data.get("status", "new")),
            estimated_value=data.get("estimated_value", 0.0),
            probability=data.get("probability", 0.0),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            assigned_agent=data.get("assigned_agent"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )

    @property
    def weighted_value(self) -> float:
        """Calculate weighted value based on probability."""
        return self.estimated_value * self.probability


@dataclass
class Client:
    """A paying client."""
    client_id: str
    company_name: str
    contact_name: str
    contact_email: str
    tier: ClientTier = ClientTier.STARTER
    total_revenue: float = 0.0
    lifetime_value: float = 0.0
    first_transaction: Optional[float] = None
    last_transaction: Optional[float] = None
    active_subscriptions: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "tier": self.tier.value,
            "total_revenue": self.total_revenue,
            "lifetime_value": self.lifetime_value,
            "first_transaction": self.first_transaction,
            "last_transaction": self.last_transaction,
            "active_subscriptions": self.active_subscriptions,
            "projects": self.projects,
            "created_at": self.created_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Client:
        return cls(
            client_id=data["client_id"],
            company_name=data["company_name"],
            contact_name=data["contact_name"],
            contact_email=data["contact_email"],
            tier=ClientTier(data.get("tier", "starter")),
            total_revenue=data.get("total_revenue", 0.0),
            lifetime_value=data.get("lifetime_value", 0.0),
            first_transaction=data.get("first_transaction"),
            last_transaction=data.get("last_transaction"),
            active_subscriptions=data.get("active_subscriptions", []),
            projects=data.get("projects", []),
            created_at=data.get("created_at", time.time()),
            metadata=data.get("metadata", {})
        )


class LeadGenerator:
    """
    Automated lead generation pipeline.
    
    Features:
    - Multi-channel lead capture
    - Lead scoring
    - Automated qualification
    - Proactive outreach triggers
    """
    
    def __init__(self, store_path: Optional[Path] = None) -> None:
        self.store_path = store_path or Path.home() / ".archonx" / "leads.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._leads: dict[str, Lead] = {}
        self._counter = 0
        
        self._load()
    
    def _load(self) -> None:
        """Load leads from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._counter = data.get("counter", 0)
                    for lead_data in data.get("leads", []):
                        lead = Lead.from_dict(lead_data)
                        self._leads[lead.lead_id] = lead
                logger.info(f"Loaded {len(self._leads)} leads")
            except Exception as e:
                logger.warning(f"Failed to load leads: {e}")
    
    def _save(self) -> None:
        """Save leads to disk."""
        data = {
            "counter": self._counter,
            "leads": [l.to_dict() for l in self._leads.values()]
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_lead(
        self,
        company_name: str,
        contact_name: str,
        contact_email: str,
        source: LeadSource,
        estimated_value: float = 0.0,
        notes: str = "",
        tags: Optional[list[str]] = None
    ) -> Lead:
        """Create a new lead."""
        self._counter += 1
        
        lead = Lead(
            lead_id=f"lead-{self._counter:06d}",
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            source=source,
            estimated_value=estimated_value,
            notes=notes,
            tags=tags or []
        )
        
        self._leads[lead.lead_id] = lead
        self._save()
        
        logger.info(f"Created lead {lead.lead_id}: {company_name}")
        return lead

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        return self._leads.get(lead_id)

    def update_lead_status(
        self,
        lead_id: str,
        status: LeadStatus,
        probability: Optional[float] = None
    ) -> Optional[Lead]:
        """Update lead status."""
        lead = self._leads.get(lead_id)
        if not lead:
            return None
        
        lead.status = status
        lead.updated_at = time.time()
        
        if probability is not None:
            lead.probability = probability
        
        # Auto-set probability based on status
        status_probabilities = {
            LeadStatus.NEW: 0.1,
            LeadStatus.CONTACTED: 0.2,
            LeadStatus.QUALIFIED: 0.4,
            LeadStatus.PROPOSAL: 0.6,
            LeadStatus.NEGOTIATION: 0.8,
            LeadStatus.WON: 1.0,
            LeadStatus.LOST: 0.0
        }
        
        if probability is None and status in status_probabilities:
            lead.probability = status_probabilities[status]
        
        self._save()
        return lead

    def get_leads_by_status(self, status: LeadStatus) -> list[Lead]:
        """Get all leads with a specific status."""
        return [l for l in self._leads.values() if l.status == status]

    def get_pipeline_value(self) -> dict[str, float]:
        """Calculate total pipeline value."""
        total = 0.0
        weighted = 0.0
        
        for lead in self._leads.values():
            if lead.status not in [LeadStatus.WON, LeadStatus.LOST]:
                total += lead.estimated_value
                weighted += lead.weighted_value
        
        return {
            "total_pipeline": total,
            "weighted_pipeline": weighted,
            "lead_count": len([l for l in self._leads.values() if l.status not in [LeadStatus.WON, LeadStatus.LOST]])
        }

    def get_stats(self) -> dict[str, Any]:
        """Get lead statistics."""
        status_counts = {}
        for status in LeadStatus:
            status_counts[status.value] = len(self.get_leads_by_status(status))
        
        return {
            "total_leads": len(self._leads),
            "by_status": status_counts,
            "pipeline": self.get_pipeline_value()
        }


class ClientAcquisition:
    """
    Client acquisition automation.
    
    Features:
    - Lead to client conversion
    - Onboarding automation
    - Tier management
    """
    
    def __init__(
        self,
        lead_generator: LeadGenerator,
        store_path: Optional[Path] = None
    ) -> None:
        self.lead_generator = lead_generator
        self.store_path = store_path or Path.home() / ".archonx" / "clients.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._clients: dict[str, Client] = {}
        self._counter = 0
        
        self._load()
    
    def _load(self) -> None:
        """Load clients from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._counter = data.get("counter", 0)
                    for client_data in data.get("clients", []):
                        client = Client.from_dict(client_data)
                        self._clients[client.client_id] = client
                logger.info(f"Loaded {len(self._clients)} clients")
            except Exception as e:
                logger.warning(f"Failed to load clients: {e}")
    
    def _save(self) -> None:
        """Save clients to disk."""
        data = {
            "counter": self._counter,
            "clients": [c.to_dict() for c in self._clients.values()]
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def convert_lead_to_client(
        self,
        lead_id: str,
        tier: ClientTier = ClientTier.STARTER
    ) -> Optional[Client]:
        """Convert a won lead to a client."""
        lead = self.lead_generator.get_lead(lead_id)
        if not lead:
            return None
        
        self._counter += 1
        
        client = Client(
            client_id=f"client-{self._counter:06d}",
            company_name=lead.company_name,
            contact_name=lead.contact_name,
            contact_email=lead.contact_email,
            tier=tier,
            first_transaction=time.time(),
            last_transaction=time.time()
        )
        
        self._clients[client.client_id] = client
        
        # Update lead status
        self.lead_generator.update_lead_status(lead_id, LeadStatus.WON, 1.0)
        
        self._save()
        
        logger.info(f"Converted lead {lead_id} to client {client.client_id}")
        return client

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        return self._clients.get(client_id)

    def update_client_tier(self, client_id: str, tier: ClientTier) -> Optional[Client]:
        """Update a client's tier."""
        client = self._clients.get(client_id)
        if not client:
            return None
        
        client.tier = tier
        self._save()
        
        logger.info(f"Updated client {client_id} to tier {tier.value}")
        return client

    def record_transaction(
        self,
        client_id: str,
        amount: float
    ) -> Optional[Client]:
        """Record a transaction for a client."""
        client = self._clients.get(client_id)
        if not client:
            return None
        
        client.total_revenue += amount
        client.last_transaction = time.time()
        
        # Update LTV
        client.lifetime_value = client.total_revenue
        
        # Auto-upgrade tier based on revenue
        if client.total_revenue >= 100000:
            client.tier = ClientTier.ENTERPRISE
        elif client.total_revenue >= 10000:
            client.tier = ClientTier.PROFESSIONAL
        
        self._save()
        return client

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics."""
        tier_counts = {}
        for tier in ClientTier:
            tier_counts[tier.value] = len([
                c for c in self._clients.values() if c.tier == tier
            ])
        
        total_revenue = sum(c.total_revenue for c in self._clients.values())
        
        return {
            "total_clients": len(self._clients),
            "by_tier": tier_counts,
            "total_revenue": total_revenue,
            "average_revenue": total_revenue / len(self._clients) if self._clients else 0
        }


class BillingAutomation:
    """
    Automated billing system.
    
    Features:
    - Subscription management
    - Invoice generation
    - Payment tracking
    - Revenue recognition
    """
    
    def __init__(
        self,
        client_acquisition: ClientAcquisition,
        store_path: Optional[Path] = None
    ) -> None:
        self.client_acquisition = client_acquisition
        self.store_path = store_path or Path.home() / ".archonx" / "billing.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._invoices: dict[str, dict[str, Any]] = {}
        self._counter = 0
        
        # Tier pricing
        self._tier_pricing = {
            ClientTier.STARTER: 99.0,
            ClientTier.PROFESSIONAL: 499.0,
            ClientTier.ENTERPRISE: 2499.0,
            ClientTier.CUSTOM: 0.0  # Custom pricing
        }
        
        self._load()
    
    def _load(self) -> None:
        """Load billing data from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._counter = data.get("counter", 0)
                    self._subscriptions = data.get("subscriptions", {})
                    self._invoices = data.get("invoices", {})
            except Exception as e:
                logger.warning(f"Failed to load billing data: {e}")
    
    def _save(self) -> None:
        """Save billing data to disk."""
        data = {
            "counter": self._counter,
            "subscriptions": self._subscriptions,
            "invoices": self._invoices
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_subscription(
        self,
        client_id: str,
        tier: ClientTier,
        custom_price: Optional[float] = None
    ) -> dict[str, Any]:
        """Create a subscription for a client."""
        self._counter += 1
        
        price = custom_price if tier == ClientTier.CUSTOM else self._tier_pricing[tier]
        
        subscription = {
            "subscription_id": f"sub-{self._counter:06d}",
            "client_id": client_id,
            "tier": tier.value,
            "price": price,
            "billing_cycle": "monthly",
            "status": "active",
            "created_at": time.time(),
            "next_billing": time.time() + 30 * 24 * 60 * 60  # 30 days
        }
        
        self._subscriptions[subscription["subscription_id"]] = subscription
        self._save()
        
        logger.info(f"Created subscription {subscription['subscription_id']} for client {client_id}")
        return subscription

    def generate_invoice(self, client_id: str) -> dict[str, Any]:
        """Generate an invoice for a client."""
        self._counter += 1
        
        # Get client subscriptions
        client_subs = [
            s for s in self._subscriptions.values()
            if s["client_id"] == client_id and s["status"] == "active"
        ]
        
        total = sum(s["price"] for s in client_subs)
        
        invoice = {
            "invoice_id": f"inv-{self._counter:06d}",
            "client_id": client_id,
            "items": [
                {
                    "subscription_id": s["subscription_id"],
                    "tier": s["tier"],
                    "amount": s["price"]
                }
                for s in client_subs
            ],
            "total": total,
            "status": "pending",
            "created_at": time.time(),
            "due_at": time.time() + 30 * 24 * 60 * 60  # 30 days
        }
        
        self._invoices[invoice["invoice_id"]] = invoice
        self._save()
        
        logger.info(f"Generated invoice {invoice['invoice_id']} for ${total:.2f}")
        return invoice

    def record_payment(
        self,
        invoice_id: str,
        amount: float
    ) -> Optional[dict[str, Any]]:
        """Record a payment for an invoice."""
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return None
        
        invoice["status"] = "paid"
        invoice["paid_at"] = time.time()
        invoice["paid_amount"] = amount
        
        # Update client revenue
        self.client_acquisition.record_transaction(
            invoice["client_id"],
            amount
        )
        
        self._save()
        
        logger.info(f"Recorded payment of ${amount:.2f} for invoice {invoice_id}")
        return invoice

    def get_monthly_recurring_revenue(self) -> float:
        """Calculate MRR."""
        return sum(
            s["price"] for s in self._subscriptions.values()
            if s["status"] == "active"
        )

    def get_stats(self) -> dict[str, Any]:
        """Get billing statistics."""
        return {
            "active_subscriptions": len([
                s for s in self._subscriptions.values() if s["status"] == "active"
            ]),
            "mrr": self.get_monthly_recurring_revenue(),
            "arr": self.get_monthly_recurring_revenue() * 12,
            "pending_invoices": len([
                i for i in self._invoices.values() if i["status"] == "pending"
            ]),
            "total_invoiced": sum(i["total"] for i in self._invoices.values()),
            "total_collected": sum(
                i.get("paid_amount", 0)
                for i in self._invoices.values()
                if i["status"] == "paid"
            )
        }


class RevenueEngine:
    """
    Main revenue generation engine for $100M goal.
    
    Features:
    - Lead generation
    - Client acquisition
    - Billing automation
    - Revenue forecasting
    - Proactive outreach
    
    Usage:
        engine = RevenueEngine()
        
        # Create lead
        lead = engine.create_lead(
            company_name="Acme Corp",
            contact_name="John Doe",
            contact_email="john@acme.com",
            source=LeadSource.WEBSITE,
            estimated_value=50000
        )
        
        # Convert to client
        client = engine.convert_lead(lead.lead_id)
        
        # Create subscription
        sub = engine.create_subscription(client.client_id, ClientTier.PROFESSIONAL)
    """
    
    def __init__(
        self,
        store_path: Optional[Path] = None,
        kpi_dashboard: Optional[Any] = None
    ) -> None:
        """
        Initialize revenue engine.
        
        Args:
            store_path: Base path for data storage
            kpi_dashboard: KPI dashboard for revenue tracking
        """
        base_path = store_path or Path.home() / ".archonx"
        
        self.lead_generator = LeadGenerator(base_path / "leads.json")
        self.client_acquisition = ClientAcquisition(
            self.lead_generator,
            base_path / "clients.json"
        )
        self.billing = BillingAutomation(
            self.client_acquisition,
            base_path / "billing.json"
        )
        self.kpi_dashboard = kpi_dashboard
        
        # Revenue targets
        self._target = 100_000_000.0  # $100M
        self._deadline = datetime(2030, 1, 1, tzinfo=timezone.UTC)
        
        logger.info(f"Revenue Engine initialized (target: ${self._target:,.0f} by {self._deadline.strftime('%Y-%m-%d')})")

    # --- Lead Management ---

    def create_lead(
        self,
        company_name: str,
        contact_name: str,
        contact_email: str,
        source: LeadSource,
        estimated_value: float = 0.0,
        notes: str = "",
        tags: Optional[list[str]] = None
    ) -> Lead:
        """Create a new lead."""
        return self.lead_generator.create_lead(
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            source=source,
            estimated_value=estimated_value,
            notes=notes,
            tags=tags
        )

    def update_lead(
        self,
        lead_id: str,
        status: LeadStatus,
        probability: Optional[float] = None
    ) -> Optional[Lead]:
        """Update lead status."""
        return self.lead_generator.update_lead_status(lead_id, status, probability)

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        return self.lead_generator.get_lead(lead_id)

    # --- Client Management ---

    def convert_lead(
        self,
        lead_id: str,
        tier: ClientTier = ClientTier.STARTER
    ) -> Optional[Client]:
        """Convert a lead to a client."""
        client = self.client_acquisition.convert_lead_to_client(lead_id, tier)
        
        if client:
            # Create subscription
            self.billing.create_subscription(client.client_id, tier)
        
        return client

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        return self.client_acquisition.get_client(client_id)

    # --- Billing ---

    def create_subscription(
        self,
        client_id: str,
        tier: ClientTier,
        custom_price: Optional[float] = None
    ) -> dict[str, Any]:
        """Create a subscription."""
        return self.billing.create_subscription(client_id, tier, custom_price)

    def generate_invoice(self, client_id: str) -> dict[str, Any]:
        """Generate an invoice."""
        return self.billing.generate_invoice(client_id)

    def record_payment(
        self,
        invoice_id: str,
        amount: float
    ) -> Optional[dict[str, Any]]:
        """Record a payment."""
        result = self.billing.record_payment(invoice_id, amount)
        
        if result and self.kpi_dashboard:
            # Record in KPI dashboard
            self.kpi_dashboard.record_revenue(
                amount=amount,
                source="subscription",
                client_id=result["client_id"]
            )
        
        return result

    # --- Analytics ---

    def get_revenue_progress(self) -> dict[str, Any]:
        """Get progress towards $100M goal."""
        current = self.billing.get_stats()["total_collected"]
        remaining = self._target - current
        days_left = (self._deadline - datetime.now(timezone.UTC)).days
        
        return {
            "target": self._target,
            "current": current,
            "remaining": remaining,
            "progress_percentage": (current / self._target) * 100,
            "days_remaining": days_left,
            "required_daily": remaining / days_left if days_left > 0 else 0,
            "mrr": self.billing.get_monthly_recurring_revenue(),
            "arr": self.billing.get_monthly_recurring_revenue() * 12
        }

    def get_pipeline_forecast(self) -> dict[str, Any]:
        """Get revenue forecast from pipeline."""
        pipeline = self.lead_generator.get_pipeline_value()
        
        return {
            "pipeline_total": pipeline["total_pipeline"],
            "pipeline_weighted": pipeline["weighted_pipeline"],
            "lead_count": pipeline["lead_count"],
            "expected_close_rate": 0.3,  # 30% close rate assumption
            "forecasted_revenue": pipeline["weighted_pipeline"] * 0.3
        }

    def get_full_report(self) -> dict[str, Any]:
        """Get comprehensive revenue report."""
        return {
            "timestamp": datetime.now(timezone.UTC).isoformat(),
            "goal_progress": self.get_revenue_progress(),
            "pipeline": self.get_pipeline_forecast(),
            "leads": self.lead_generator.get_stats(),
            "clients": self.client_acquisition.get_stats(),
            "billing": self.billing.get_stats()
        }


# Singleton instance
_engine: Optional[RevenueEngine] = None


def get_revenue_engine() -> RevenueEngine:
    """Get the singleton RevenueEngine."""
    global _engine
    if _engine is None:
        _engine = RevenueEngine()
    return _engine
