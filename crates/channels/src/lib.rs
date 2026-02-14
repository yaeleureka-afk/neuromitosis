//! # Channels
//!
//! I/O channels — CLI, Telegram, Discord, Slack, webhook.

use anyhow::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InboundMessage {
    pub content: String,
    pub sender: String,
    pub channel_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutboundMessage {
    pub content: String,
    pub channel_id: String,
}

/// The Channel trait — implement for each messaging platform.
#[async_trait::async_trait]
pub trait Channel: Send + Sync {
    /// Channel name (e.g., "cli", "telegram", "discord").
    fn name(&self) -> &str;
    /// Receive the next inbound message.
    async fn recv(&self) -> Result<InboundMessage>;
    /// Send an outbound message.
    async fn send(&self, msg: OutboundMessage) -> Result<()>;
}
