//! # MCP
//!
//! Model Context Protocol server — tool discovery for the Electron frontend.
//! Every Tool auto-exposes as an MCP tool.

use anyhow::Result;
use serde::{Deserialize, Serialize};

/// An MCP tool listing entry.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpToolEntry {
    pub name: String,
    pub description: String,
    pub input_schema: serde_json::Value,
}

/// MCP request types.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "method")]
pub enum McpRequest {
    #[serde(rename = "tools/list")]
    ListTools,
    #[serde(rename = "tools/call")]
    CallTool {
        params: McpCallParams,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpCallParams {
    pub name: String,
    pub arguments: serde_json::Value,
}

/// MCP transport trait — WebSocket, stdio, etc.
#[async_trait::async_trait]
pub trait McpTransport: Send + Sync {
    async fn recv(&self) -> Result<String>;
    async fn send(&self, msg: &str) -> Result<()>;
}

// TODO: Phase 5 — full MCP JSON-RPC server implementation
