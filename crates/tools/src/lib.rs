//! # Tools
//!
//! Capability system — shell, files, Composio, browser, and custom tools.

use anyhow::Result;
use serde::{Deserialize, Serialize};

/// Result of executing a tool.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolResult {
    pub output: serde_json::Value,
    pub success: bool,
    pub error: Option<String>,
}

/// The Tool trait — implement for each capability.
#[async_trait::async_trait]
pub trait Tool: Send + Sync {
    /// Tool name (unique identifier).
    fn name(&self) -> &str;
    /// Human-readable description.
    fn description(&self) -> &str;
    /// JSON Schema for the tool's parameters.
    fn parameters(&self) -> serde_json::Value;
    /// Execute the tool with given arguments.
    async fn execute(&self, args: serde_json::Value) -> Result<ToolResult>;
}
