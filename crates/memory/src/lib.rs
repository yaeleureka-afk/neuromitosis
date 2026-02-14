//! # Memory
//!
//! Persistent memory with hybrid search — SQLite + FTS5 + vector embeddings.

use anyhow::Result;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// A memory entry.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEntry {
    pub id: Uuid,
    pub content: String,
    pub metadata: Option<serde_json::Value>,
    pub created_at: DateTime<Utc>,
    pub relevance_score: Option<f64>,
}

/// Metadata for memory storage.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Metadata {
    pub source: Option<String>,
    pub tags: Vec<String>,
}

/// The Memory trait — implement for each persistence backend.
#[async_trait::async_trait]
pub trait Memory: Send + Sync {
    /// Store a memory entry.
    async fn store(&self, content: &str, metadata: Option<Metadata>) -> Result<Uuid>;
    /// Recall memories matching a query.
    async fn recall(&self, query: &str, limit: usize) -> Result<Vec<MemoryEntry>>;
    /// Forget a specific memory.
    async fn forget(&self, id: Uuid) -> Result<()>;
    /// Count total memories.
    async fn count(&self) -> Result<usize>;
}
