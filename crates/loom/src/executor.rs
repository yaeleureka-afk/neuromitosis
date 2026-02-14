//! Executor — async node execution with Tokio.

use anyhow::Result;
use serde_json::Value;
use std::collections::HashMap;
use uuid::Uuid;

/// The result of executing a single node.
#[derive(Debug, Clone)]
pub struct ExecutionResult {
    pub node_id: Uuid,
    pub output: Value,
    pub duration_ms: u64,
    pub success: bool,
    pub error: Option<String>,
}

/// Trait for node executors — the bridge between canvas nodes and actual tool calls.
#[async_trait::async_trait]
pub trait NodeExecutor: Send + Sync {
    /// Execute a node with the given inputs, return the output.
    async fn execute(
        &self,
        node_id: Uuid,
        tool_slug: Option<&str>,
        config: &Value,
        inputs: &HashMap<String, Value>,
    ) -> Result<Value>;
}

/// A no-op executor for testing — passes inputs through as outputs.
pub struct PassthroughExecutor;

#[async_trait::async_trait]
impl NodeExecutor for PassthroughExecutor {
    async fn execute(
        &self,
        _node_id: Uuid,
        _tool_slug: Option<&str>,
        _config: &Value,
        inputs: &HashMap<String, Value>,
    ) -> Result<Value> {
        Ok(serde_json::to_value(inputs)?)
    }
}
