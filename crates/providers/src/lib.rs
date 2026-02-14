//! # Providers
//!
//! LLM backends — trait-based, swap with config.

use anyhow::Result;
use serde::{Deserialize, Serialize};

/// A message in a conversation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

/// A tool definition for function calling.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolDef {
    pub name: String,
    pub description: String,
    pub parameters: serde_json::Value,
}

/// Response from a provider.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Response {
    pub content: String,
    pub tool_calls: Vec<ToolCall>,
    pub model: String,
    pub usage: Option<Usage>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub name: String,
    pub arguments: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Usage {
    pub input_tokens: u64,
    pub output_tokens: u64,
}

/// The Provider trait — implement for each LLM backend.
#[async_trait::async_trait]
pub trait Provider: Send + Sync {
    /// Send messages to the LLM, optionally with tool definitions.
    async fn complete(&self, messages: &[Message], tools: &[ToolDef]) -> Result<Response>;
    /// Provider name (e.g., "anthropic", "openai", "ollama").
    fn name(&self) -> &str;
    /// Model identifier (e.g., "claude-sonnet-4-20250514").
    fn model(&self) -> &str;
}
