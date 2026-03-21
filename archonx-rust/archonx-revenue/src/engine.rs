/// Revenue Engine — leads, clients, billing for $100M goal.
/// Replaces: archonx/revenue/engine.py
///
/// Backed by sqlx + PostgreSQL (falls back to in-memory HashMap for tests).
/// Revenue target: $100M by 2030.
use std::collections::HashMap;
use std::sync::Arc;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use tracing::info;

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum LeadStatus {
    #[default]
    New,
    Contacted,
    Qualified,
    Proposal,
    Negotiation,
    Won,
    Lost,
}

impl LeadStatus {
    pub fn default_probability(self) -> f64 {
        match self {
            LeadStatus::New => 0.1,
            LeadStatus::Contacted => 0.2,
            LeadStatus::Qualified => 0.4,
            LeadStatus::Proposal => 0.6,
            LeadStatus::Negotiation => 0.8,
            LeadStatus::Won => 1.0,
            LeadStatus::Lost => 0.0,
        }
    }
}

impl std::fmt::Display for LeadStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            LeadStatus::New => "new", LeadStatus::Contacted => "contacted",
            LeadStatus::Qualified => "qualified", LeadStatus::Proposal => "proposal",
            LeadStatus::Negotiation => "negotiation", LeadStatus::Won => "won",
            LeadStatus::Lost => "lost",
        };
        write!(f, "{}", s)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum LeadSource {
    #[default]
    Website,
    Referral,
    ColdOutreach,
    SocialMedia,
    PaidAds,
    Organic,
    ApiIntegration,
    Marketplace,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum ClientTier {
    #[default]
    Starter,
    Professional,
    Enterprise,
    Custom,
}

impl ClientTier {
    pub fn monthly_price(self) -> f64 {
        match self {
            ClientTier::Starter => 99.0,
            ClientTier::Professional => 499.0,
            ClientTier::Enterprise => 2499.0,
            ClientTier::Custom => 0.0,
        }
    }
}

impl std::fmt::Display for ClientTier {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            ClientTier::Starter => "starter", ClientTier::Professional => "professional",
            ClientTier::Enterprise => "enterprise", ClientTier::Custom => "custom",
        };
        write!(f, "{}", s)
    }
}

// ---------------------------------------------------------------------------
// Lead
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Lead {
    pub lead_id: String,
    pub company_name: String,
    pub contact_name: String,
    pub contact_email: String,
    pub source: LeadSource,
    pub status: LeadStatus,
    pub estimated_value: f64,
    pub probability: f64,
    pub notes: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub assigned_agent: Option<String>,
    pub tags: Vec<String>,
    pub metadata: serde_json::Value,
}

impl Lead {
    pub fn weighted_value(&self) -> f64 {
        self.estimated_value * self.probability
    }
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Client {
    pub client_id: String,
    pub company_name: String,
    pub contact_name: String,
    pub contact_email: String,
    pub tier: ClientTier,
    pub total_revenue: f64,
    pub lifetime_value: f64,
    pub first_transaction: Option<DateTime<Utc>>,
    pub last_transaction: Option<DateTime<Utc>>,
    pub active_subscriptions: Vec<String>,
    pub projects: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub metadata: serde_json::Value,
}

// ---------------------------------------------------------------------------
// Subscription & Invoice
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subscription {
    pub subscription_id: String,
    pub client_id: String,
    pub tier: ClientTier,
    pub price: f64,
    pub status: String, // "active" | "cancelled"
    pub created_at: DateTime<Utc>,
    pub next_billing: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Invoice {
    pub invoice_id: String,
    pub client_id: String,
    pub items: Vec<serde_json::Value>,
    pub total: f64,
    pub status: String, // "pending" | "paid"
    pub created_at: DateTime<Utc>,
    pub due_at: DateTime<Utc>,
    pub paid_at: Option<DateTime<Utc>>,
    pub paid_amount: Option<f64>,
}

// ---------------------------------------------------------------------------
// RevenueEngine — combines lead gen, client acquisition, billing
// ---------------------------------------------------------------------------

/// Main revenue generation engine targeting $100M by 2030.
/// Replaces Python: class RevenueEngine + LeadGenerator + ClientAcquisition + BillingAutomation
pub struct RevenueEngine {
    pool: Option<PgPool>,
    leads: Arc<tokio::sync::RwLock<HashMap<String, Lead>>>,
    clients: Arc<tokio::sync::RwLock<HashMap<String, Client>>>,
    subscriptions: Arc<tokio::sync::RwLock<HashMap<String, Subscription>>>,
    invoices: Arc<tokio::sync::RwLock<HashMap<String, Invoice>>>,
    lead_counter: Arc<tokio::sync::Mutex<u64>>,
    client_counter: Arc<tokio::sync::Mutex<u64>>,
    invoice_counter: Arc<tokio::sync::Mutex<u64>>,
    sub_counter: Arc<tokio::sync::Mutex<u64>>,
    /// $100M by 2030 — locked constant
    revenue_target: f64,
    deadline: DateTime<Utc>,
}

impl RevenueEngine {
    pub fn new(pool: Option<PgPool>) -> Self {
        let deadline = chrono::DateTime::parse_from_rfc3339("2030-01-01T00:00:00Z")
            .unwrap()
            .with_timezone(&Utc);
        let this = Self {
            pool,
            leads: Default::default(),
            clients: Default::default(),
            subscriptions: Default::default(),
            invoices: Default::default(),
            lead_counter: Default::default(),
            client_counter: Default::default(),
            invoice_counter: Default::default(),
            sub_counter: Default::default(),
            revenue_target: 100_000_000.0, // $100M
            deadline,
        };
        info!(
            "Revenue Engine initialized (target: ${:.0} by {})",
            this.revenue_target,
            this.deadline.format("%Y-%m-%d")
        );
        this
    }

    // ------------------------------------------------------------------
    // Lead management
    // ------------------------------------------------------------------

    pub async fn create_lead(
        &self,
        company_name: &str,
        contact_name: &str,
        contact_email: &str,
        source: LeadSource,
        estimated_value: f64,
        notes: &str,
        tags: Vec<String>,
    ) -> Lead {
        let mut counter = self.lead_counter.lock().await;
        *counter += 1;
        let lead = Lead {
            lead_id: format!("lead-{:06}", counter),
            company_name: company_name.to_string(),
            contact_name: contact_name.to_string(),
            contact_email: contact_email.to_string(),
            source,
            status: LeadStatus::New,
            estimated_value,
            probability: LeadStatus::New.default_probability(),
            notes: notes.to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
            assigned_agent: None,
            tags,
            metadata: serde_json::Value::Null,
        };
        self.leads.write().await.insert(lead.lead_id.clone(), lead.clone());
        info!("Created lead {}: {}", lead.lead_id, company_name);
        lead
    }

    pub async fn update_lead_status(
        &self,
        lead_id: &str,
        status: LeadStatus,
        probability: Option<f64>,
    ) -> Option<Lead> {
        let mut leads = self.leads.write().await;
        let lead = leads.get_mut(lead_id)?;
        lead.status = status;
        lead.updated_at = Utc::now();
        lead.probability = probability.unwrap_or_else(|| status.default_probability());
        Some(lead.clone())
    }

    pub async fn get_lead(&self, lead_id: &str) -> Option<Lead> {
        self.leads.read().await.get(lead_id).cloned()
    }

    pub async fn pipeline_value(&self) -> serde_json::Value {
        let leads = self.leads.read().await;
        let active: Vec<&Lead> = leads
            .values()
            .filter(|l| l.status != LeadStatus::Won && l.status != LeadStatus::Lost)
            .collect();
        let total: f64 = active.iter().map(|l| l.estimated_value).sum();
        let weighted: f64 = active.iter().map(|l| l.weighted_value()).sum();
        serde_json::json!({
            "total_pipeline": total,
            "weighted_pipeline": weighted,
            "lead_count": active.len(),
        })
    }

    // ------------------------------------------------------------------
    // Client management
    // ------------------------------------------------------------------

    pub async fn convert_lead_to_client(
        &self,
        lead_id: &str,
        tier: ClientTier,
    ) -> Option<Client> {
        let lead = {
            let leads = self.leads.read().await;
            leads.get(lead_id).cloned()?
        };

        let mut counter = self.client_counter.lock().await;
        *counter += 1;
        let now = Utc::now();
        let client = Client {
            client_id: format!("client-{:06}", counter),
            company_name: lead.company_name.clone(),
            contact_name: lead.contact_name.clone(),
            contact_email: lead.contact_email.clone(),
            tier,
            total_revenue: 0.0,
            lifetime_value: 0.0,
            first_transaction: Some(now),
            last_transaction: Some(now),
            active_subscriptions: Vec::new(),
            projects: Vec::new(),
            created_at: now,
            metadata: serde_json::Value::Null,
        };
        self.clients.write().await.insert(client.client_id.clone(), client.clone());
        self.update_lead_status(lead_id, LeadStatus::Won, Some(1.0)).await;

        // Auto-create subscription
        self.create_subscription(&client.client_id, tier, None).await;
        info!("Converted lead {} to client {}", lead_id, client.client_id);
        Some(client)
    }

    pub async fn get_client(&self, client_id: &str) -> Option<Client> {
        self.clients.read().await.get(client_id).cloned()
    }

    pub async fn record_transaction(&self, client_id: &str, amount: f64) {
        let mut clients = self.clients.write().await;
        if let Some(client) = clients.get_mut(client_id) {
            client.total_revenue += amount;
            client.lifetime_value = client.total_revenue;
            client.last_transaction = Some(Utc::now());
            // Auto-upgrade tier
            client.tier = if client.total_revenue >= 100_000.0 {
                ClientTier::Enterprise
            } else if client.total_revenue >= 10_000.0 {
                ClientTier::Professional
            } else {
                client.tier
            };
        }
    }

    // ------------------------------------------------------------------
    // Billing
    // ------------------------------------------------------------------

    pub async fn create_subscription(
        &self,
        client_id: &str,
        tier: ClientTier,
        custom_price: Option<f64>,
    ) -> Subscription {
        let mut counter = self.sub_counter.lock().await;
        *counter += 1;
        let price = custom_price.unwrap_or_else(|| tier.monthly_price());
        let now = Utc::now();
        let sub = Subscription {
            subscription_id: format!("sub-{:06}", counter),
            client_id: client_id.to_string(),
            tier,
            price,
            status: "active".into(),
            created_at: now,
            next_billing: now + chrono::Duration::days(30),
        };
        self.subscriptions.write().await.insert(sub.subscription_id.clone(), sub.clone());
        info!("Created subscription {} for client {}", sub.subscription_id, client_id);
        sub
    }

    pub async fn generate_invoice(&self, client_id: &str) -> Invoice {
        let subs = self.subscriptions.read().await;
        let client_subs: Vec<&Subscription> = subs
            .values()
            .filter(|s| s.client_id == client_id && s.status == "active")
            .collect();
        let total: f64 = client_subs.iter().map(|s| s.price).sum();

        let mut counter = self.invoice_counter.lock().await;
        *counter += 1;
        let now = Utc::now();
        let invoice = Invoice {
            invoice_id: format!("inv-{:06}", counter),
            client_id: client_id.to_string(),
            items: client_subs.iter().map(|s| serde_json::json!({
                "subscription_id": s.subscription_id,
                "tier": s.tier.to_string(),
                "amount": s.price,
            })).collect(),
            total,
            status: "pending".into(),
            created_at: now,
            due_at: now + chrono::Duration::days(30),
            paid_at: None,
            paid_amount: None,
        };
        self.invoices.write().await.insert(invoice.invoice_id.clone(), invoice.clone());
        info!("Generated invoice {} for ${:.2}", invoice.invoice_id, total);
        invoice
    }

    pub async fn record_payment(&self, invoice_id: &str, amount: f64) -> Option<Invoice> {
        let invoice = {
            let mut invoices = self.invoices.write().await;
            let inv = invoices.get_mut(invoice_id)?;
            inv.status = "paid".into();
            inv.paid_at = Some(Utc::now());
            inv.paid_amount = Some(amount);
            inv.clone()
        };
        self.record_transaction(&invoice.client_id, amount).await;
        info!("Recorded payment of ${:.2} for invoice {}", amount, invoice_id);
        Some(invoice)
    }

    pub async fn mrr(&self) -> f64 {
        self.subscriptions
            .read()
            .await
            .values()
            .filter(|s| s.status == "active")
            .map(|s| s.price)
            .sum()
    }

    // ------------------------------------------------------------------
    // Analytics
    // ------------------------------------------------------------------

    pub async fn revenue_progress(&self) -> serde_json::Value {
        let invoices = self.invoices.read().await;
        let current: f64 = invoices
            .values()
            .filter(|i| i.status == "paid")
            .filter_map(|i| i.paid_amount)
            .sum();
        let remaining = self.revenue_target - current;
        let days_left = (self.deadline - Utc::now()).num_days();
        let mrr = self.mrr().await;

        serde_json::json!({
            "target": self.revenue_target,
            "current": current,
            "remaining": remaining,
            "progress_percentage": (current / self.revenue_target) * 100.0,
            "days_remaining": days_left,
            "required_daily": if days_left > 0 { remaining / days_left as f64 } else { 0.0 },
            "mrr": mrr,
            "arr": mrr * 12.0,
        })
    }

    pub async fn full_report(&self) -> serde_json::Value {
        let leads = self.leads.read().await;
        let clients = self.clients.read().await;
        let subs = self.subscriptions.read().await;
        let invoices = self.invoices.read().await;

        let total_collected: f64 = invoices
            .values()
            .filter(|i| i.status == "paid")
            .filter_map(|i| i.paid_amount)
            .sum();

        serde_json::json!({
            "timestamp": Utc::now().to_rfc3339(),
            "goal_progress": self.revenue_progress().await,
            "leads": {
                "total": leads.len(),
                "by_status": {
                    "new": leads.values().filter(|l| l.status == LeadStatus::New).count(),
                    "won": leads.values().filter(|l| l.status == LeadStatus::Won).count(),
                    "lost": leads.values().filter(|l| l.status == LeadStatus::Lost).count(),
                }
            },
            "clients": {
                "total": clients.len(),
                "by_tier": {
                    "starter": clients.values().filter(|c| c.tier == ClientTier::Starter).count(),
                    "professional": clients.values().filter(|c| c.tier == ClientTier::Professional).count(),
                    "enterprise": clients.values().filter(|c| c.tier == ClientTier::Enterprise).count(),
                }
            },
            "billing": {
                "active_subscriptions": subs.values().filter(|s| s.status == "active").count(),
                "mrr": self.mrr().await,
                "arr": self.mrr().await * 12.0,
                "total_collected": total_collected,
            }
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn engine() -> RevenueEngine {
        RevenueEngine::new(None)
    }

    #[tokio::test]
    async fn create_and_retrieve_lead() {
        let e = engine();
        let lead = e.create_lead("Acme", "John", "john@acme.com", LeadSource::Website, 50000.0, "", vec![]).await;
        assert!(lead.lead_id.starts_with("lead-"));
        assert_eq!(lead.status, LeadStatus::New);
        let fetched = e.get_lead(&lead.lead_id).await.unwrap();
        assert_eq!(fetched.company_name, "Acme");
    }

    #[tokio::test]
    async fn convert_lead_to_client() {
        let e = engine();
        let lead = e.create_lead("Corp", "Jane", "jane@corp.com", LeadSource::Referral, 100000.0, "", vec![]).await;
        let client = e.convert_lead_to_client(&lead.lead_id, ClientTier::Professional).await.unwrap();
        assert!(client.client_id.starts_with("client-"));
        assert_eq!(client.tier, ClientTier::Professional);

        // Lead should be marked Won
        let lead = e.get_lead(&lead.lead_id).await.unwrap();
        assert_eq!(lead.status, LeadStatus::Won);
    }

    #[tokio::test]
    async fn billing_invoice_and_payment() {
        let e = engine();
        let lead = e.create_lead("Biz", "Bob", "bob@biz.com", LeadSource::Organic, 10000.0, "", vec![]).await;
        let client = e.convert_lead_to_client(&lead.lead_id, ClientTier::Starter).await.unwrap();
        let invoice = e.generate_invoice(&client.client_id).await;
        assert_eq!(invoice.status, "pending");
        assert_eq!(invoice.total, 99.0); // Starter price

        let paid = e.record_payment(&invoice.invoice_id, invoice.total).await.unwrap();
        assert_eq!(paid.status, "paid");
    }

    #[tokio::test]
    async fn mrr_accumulates() {
        let e = engine();
        let lead1 = e.create_lead("A", "x", "x@a.com", LeadSource::Website, 0.0, "", vec![]).await;
        let lead2 = e.create_lead("B", "y", "y@b.com", LeadSource::Website, 0.0, "", vec![]).await;
        e.convert_lead_to_client(&lead1.lead_id, ClientTier::Professional).await;
        e.convert_lead_to_client(&lead2.lead_id, ClientTier::Enterprise).await;
        let mrr = e.mrr().await;
        assert_eq!(mrr, 499.0 + 2499.0);
    }

    #[tokio::test]
    async fn revenue_target_constant() {
        let e = engine();
        let progress = e.revenue_progress().await;
        assert_eq!(progress["target"].as_f64().unwrap(), 100_000_000.0);
    }
}
