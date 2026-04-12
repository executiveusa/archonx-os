/// Token Meter — lock-free billing engine.
/// Replaces: archonx/billing/token_meter.py
///
/// Hot path — must be lock-free.
/// Uses DashMap<UserId, AtomicI64> for balances.
/// Replaces Python defaultdict(int) + list with atomic operations.
use std::sync::atomic::{AtomicI64, AtomicU64, Ordering};
use std::sync::Arc;

use chrono::Utc;
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use tracing::{info, warn};

// ---------------------------------------------------------------------------
// TokenTransaction
// ---------------------------------------------------------------------------

/// A single token transaction.
/// Replaces Python: @dataclass class TokenTransaction
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenTransaction {
    pub id: String,
    pub user_id: String,
    /// Positive = charge (tokens spent), negative = credit (tokens added).
    /// Note: Python has opposite sign convention for credit (amount = -credit_amount).
    /// We use: charge = +amount, credit = -amount to match Python behavior exactly.
    pub amount: i64,
    pub source: String,
    pub description: String,
    pub timestamp_ms: i64, // replaces Python time.time()
    pub metadata: serde_json::Value,
}

/// Token source categories.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TokenSource {
    Theater,
    Skill,
    Api,
    ComputerUse,
    Purchase,
    Refund,
    Custom(String),
}

impl std::fmt::Display for TokenSource {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TokenSource::Custom(s) => write!(f, "{}", s),
            _ => write!(f, "{:?}", self),
        }
    }
}

// ---------------------------------------------------------------------------
// TokenMeter
// ---------------------------------------------------------------------------

/// Central billing engine for token-based usage tracking.
///
/// All billable actions go through the meter. Uses:
/// - DashMap<String, Arc<AtomicI64>> for lock-free per-user balance reads
/// - tokio::sync::Mutex<Vec<TokenTransaction>> for transaction history append
///
/// Replaces Python: class TokenMeter with defaultdict + list
pub struct TokenMeter {
    /// Per-user token balances — lock-free atomic reads/writes.
    balances: DashMap<String, Arc<AtomicI64>>,
    /// Transaction history — append-only, protected by async mutex.
    transactions: Arc<tokio::sync::Mutex<Vec<TokenTransaction>>>,
    /// Global monotonic transaction counter.
    counter: Arc<AtomicU64>,
}

impl Default for TokenMeter {
    fn default() -> Self {
        Self::new()
    }
}

impl TokenMeter {
    pub fn new() -> Self {
        Self {
            balances: DashMap::new(),
            transactions: Arc::new(tokio::sync::Mutex::new(Vec::new())),
            counter: Arc::new(AtomicU64::new(0)),
        }
    }

    // ------------------------------------------------------------------
    // Credit — add tokens to user balance
    // ------------------------------------------------------------------

    /// Add tokens to a user's balance.
    /// Replaces Python: def credit(self, user_id, amount, source, description)
    pub async fn credit(
        &self,
        user_id: &str,
        amount: i64,
        source: &str,
        description: &str,
    ) -> TokenTransaction {
        // Atomic increment of balance
        let entry = self
            .balances
            .entry(user_id.to_string())
            .or_insert_with(|| Arc::new(AtomicI64::new(0)));
        entry.fetch_add(amount, Ordering::Relaxed);

        let id = self.counter.fetch_add(1, Ordering::Relaxed) + 1;
        let txn = TokenTransaction {
            id: format!("txn-{:06}", id),
            user_id: user_id.to_string(),
            amount: -amount, // negative = credit (tokens added) — matches Python convention
            source: source.to_string(),
            description: if description.is_empty() {
                format!("Credit {} tokens", amount)
            } else {
                description.to_string()
            },
            timestamp_ms: Utc::now().timestamp_millis(),
            metadata: serde_json::Value::Null,
        };

        self.transactions.lock().await.push(txn.clone());
        info!("Token credit: {} +{} ({})", user_id, amount, source);
        txn
    }

    // ------------------------------------------------------------------
    // Charge — deduct tokens from user balance
    // ------------------------------------------------------------------

    /// Charge tokens from a user's balance.
    /// Returns None if insufficient balance.
    /// Replaces Python: def charge(self, user_id, amount, source, description)
    pub async fn charge(
        &self,
        user_id: &str,
        amount: i64,
        source: &str,
        description: &str,
    ) -> Option<TokenTransaction> {
        let entry = self
            .balances
            .entry(user_id.to_string())
            .or_insert_with(|| Arc::new(AtomicI64::new(0)));

        // Atomic compare-and-swap loop — ensures no overdraft even under concurrency
        loop {
            let current = entry.load(Ordering::Relaxed);
            if current < amount {
                warn!(
                    "Token charge failed: {} has {}, needs {}",
                    user_id, current, amount
                );
                return None;
            }
            // Try to atomically subtract
            match entry.compare_exchange(
                current,
                current - amount,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(_) => continue, // CAS failed — retry
            }
        }

        let id = self.counter.fetch_add(1, Ordering::Relaxed) + 1;
        let txn = TokenTransaction {
            id: format!("txn-{:06}", id),
            user_id: user_id.to_string(),
            amount, // positive = charge
            source: source.to_string(),
            description: if description.is_empty() {
                format!("Charge {} tokens for {}", amount, source)
            } else {
                description.to_string()
            },
            timestamp_ms: Utc::now().timestamp_millis(),
            metadata: serde_json::Value::Null,
        };

        self.transactions.lock().await.push(txn.clone());
        info!("Token charge: {} -{} ({})", user_id, amount, source);
        Some(txn)
    }

    // ------------------------------------------------------------------
    // Queries
    // ------------------------------------------------------------------

    /// Get current token balance for a user.
    /// Replaces Python: def balance(self, user_id)
    pub fn balance(&self, user_id: &str) -> i64 {
        self.balances
            .get(user_id)
            .map(|v| v.load(Ordering::Relaxed))
            .unwrap_or(0)
    }

    /// Get transaction history for a user.
    /// Replaces Python: def history(self, user_id, limit=50)
    pub async fn history(&self, user_id: &str, limit: usize) -> Vec<TokenTransaction> {
        let txns = self.transactions.lock().await;
        let user_txns: Vec<TokenTransaction> = txns
            .iter()
            .filter(|t| t.user_id == user_id)
            .cloned()
            .collect();
        let len = user_txns.len();
        user_txns[len.saturating_sub(limit)..].to_vec()
    }

    // ------------------------------------------------------------------
    // Stats
    // ------------------------------------------------------------------

    /// Get billing statistics.
    /// Replaces Python: @property def stats(self)
    pub async fn stats(&self) -> serde_json::Value {
        let txns = self.transactions.lock().await;
        let total_charged: i64 = txns.iter().filter(|t| t.amount > 0).map(|t| t.amount).sum();
        let total_credited: i64 = txns.iter().filter(|t| t.amount < 0).map(|t| -t.amount).sum();

        let active_balances: serde_json::Map<String, serde_json::Value> = self
            .balances
            .iter()
            .filter(|e| e.value().load(Ordering::Relaxed) > 0)
            .map(|e| {
                (
                    e.key().clone(),
                    serde_json::Value::Number(
                        serde_json::Number::from(e.value().load(Ordering::Relaxed)),
                    ),
                )
            })
            .collect();

        serde_json::json!({
            "total_users": self.balances.len(),
            "total_charged": total_charged,
            "total_credited": total_credited,
            "total_transactions": txns.len(),
            "active_balances": active_balances,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn credit_increases_balance() {
        let m = TokenMeter::new();
        let txn = m.credit("user-01", 1000, "purchase", "Welcome tokens").await;
        assert_eq!(m.balance("user-01"), 1000);
        assert_eq!(txn.amount, -1000); // credit = negative (matches Python)
    }

    #[tokio::test]
    async fn charge_decreases_balance() {
        let m = TokenMeter::new();
        m.credit("user-01", 500, "purchase", "").await;
        let txn = m.charge("user-01", 100, "skill", "Used skill X").await;
        assert!(txn.is_some());
        assert_eq!(txn.unwrap().amount, 100); // charge = positive
        assert_eq!(m.balance("user-01"), 400);
    }

    #[tokio::test]
    async fn charge_fails_with_insufficient_balance() {
        let m = TokenMeter::new();
        m.credit("user-02", 50, "purchase", "").await;
        let txn = m.charge("user-02", 100, "theater", "").await;
        assert!(txn.is_none());
        assert_eq!(m.balance("user-02"), 50); // balance unchanged
    }

    #[tokio::test]
    async fn charge_exact_balance_succeeds() {
        let m = TokenMeter::new();
        m.credit("user-03", 100, "purchase", "").await;
        let txn = m.charge("user-03", 100, "api", "").await;
        assert!(txn.is_some());
        assert_eq!(m.balance("user-03"), 0);
    }

    #[tokio::test]
    async fn history_returns_user_transactions() {
        let m = TokenMeter::new();
        m.credit("user-04", 200, "purchase", "").await;
        m.charge("user-04", 50, "skill", "").await;
        m.charge("user-04", 30, "api", "").await;
        let hist = m.history("user-04", 50).await;
        assert_eq!(hist.len(), 3);
    }

    #[tokio::test]
    async fn stats_shows_correct_totals() {
        let m = TokenMeter::new();
        m.credit("u1", 1000, "purchase", "").await;
        m.charge("u1", 200, "skill", "").await;
        m.charge("u1", 100, "api", "").await;
        let s = m.stats().await;
        assert_eq!(s["total_charged"].as_i64().unwrap(), 300);
        assert_eq!(s["total_credited"].as_i64().unwrap(), 1000);
    }

    #[tokio::test]
    async fn concurrent_charges_no_overdraft() {
        use std::sync::Arc;
        let m = Arc::new(TokenMeter::new());
        m.credit("user-concurrent", 100, "purchase", "").await;

        // Spawn 10 concurrent charge attempts of 20 each (total 200 > balance 100)
        let mut handles = Vec::new();
        for _ in 0..10 {
            let m2 = m.clone();
            handles.push(tokio::spawn(async move {
                m2.charge("user-concurrent", 20, "api", "").await
            }));
        }
        let results: Vec<_> = futures::future::join_all(handles).await;
        let successes = results.iter().filter(|r| r.as_ref().unwrap().is_some()).count();
        // At most 5 should succeed (100 / 20 = 5 max)
        assert!(successes <= 5, "Got {} successes, expected <= 5", successes);
        assert!(m.balance("user-concurrent") >= 0, "Balance went negative!");
    }
}
