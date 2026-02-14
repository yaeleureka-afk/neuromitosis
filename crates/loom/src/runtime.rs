//! Runtime — the Loom. Weaves a Canvas into execution.

use crate::executor::{ExecutionResult, NodeExecutor};
use crate::topology;
use anyhow::Result;
use neuromitosis_canvas::Canvas;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Instant;
use uuid::Uuid;

/// Output produced by a single node after execution.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeOutput {
    pub node_id: Uuid,
    pub node_name: String,
    pub output: Value,
    pub duration_ms: u64,
}

/// The result of weaving an entire Canvas.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeaveResult {
    pub canvas_name: String,
    pub layers: Vec<Vec<Uuid>>,
    pub outputs: HashMap<Uuid, NodeOutput>,
    pub total_duration_ms: u64,
    pub success: bool,
    pub errors: Vec<String>,
}

/// The Loom — weaves a Canvas DAG into execution.
pub struct Loom {
    executor: Arc<dyn NodeExecutor>,
}

impl Loom {
    pub fn new(executor: Arc<dyn NodeExecutor>) -> Self {
        Self { executor }
    }

    /// Compute the topology (execution layers) of a canvas.
    pub fn topology(&self, canvas: &Canvas) -> Result<Vec<Vec<Uuid>>> {
        Ok(topology::compute_layers(canvas)?)
    }

    /// Weave a canvas — execute all nodes in topological order.
    /// Nodes in the same layer execute in parallel via Tokio.
    pub async fn weave(&self, canvas: &Canvas) -> Result<WeaveResult> {
        let start = Instant::now();
        let layers = topology::compute_layers(canvas)?;

        let mut outputs: HashMap<Uuid, NodeOutput> = HashMap::new();
        let mut errors: Vec<String> = Vec::new();

        for layer in &layers {
            // Execute all nodes in this layer in parallel
            let mut handles = Vec::new();

            for &node_id in layer {
                let node = canvas.nodes.get(&node_id).unwrap().clone();
                let executor = self.executor.clone();

                // Gather inputs from predecessor outputs
                let mut inputs: HashMap<String, Value> = HashMap::new();
                for yarn in &canvas.yarns {
                    if yarn.to_node == node_id {
                        if let Some(prev_output) = outputs.get(&yarn.from_node) {
                            let key = node
                                .inputs
                                .iter()
                                .find(|p| p.id == yarn.to_port)
                                .map(|p| p.name.clone())
                                .unwrap_or_else(|| "input".to_string());
                            inputs.insert(key, prev_output.output.clone());
                        }
                    }
                }

                handles.push(tokio::spawn(async move {
                    let node_start = Instant::now();
                    let result = executor
                        .execute(
                            node.id,
                            node.tool_slug.as_deref(),
                            &node.config,
                            &inputs,
                        )
                        .await;

                    let duration = node_start.elapsed().as_millis() as u64;

                    match result {
                        Ok(output) => ExecutionResult {
                            node_id: node.id,
                            output,
                            duration_ms: duration,
                            success: true,
                            error: None,
                        },
                        Err(e) => ExecutionResult {
                            node_id: node.id,
                            output: Value::Null,
                            duration_ms: duration,
                            success: false,
                            error: Some(e.to_string()),
                        },
                    }
                }));
            }

            // Await all parallel tasks in this layer
            for handle in handles {
                let result = handle.await?;
                let node_name = canvas
                    .nodes
                    .get(&result.node_id)
                    .map(|n| n.name.clone())
                    .unwrap_or_default();

                if !result.success {
                    if let Some(ref err) = result.error {
                        errors.push(format!("{}: {}", node_name, err));
                    }
                }

                outputs.insert(
                    result.node_id,
                    NodeOutput {
                        node_id: result.node_id,
                        node_name,
                        output: result.output,
                        duration_ms: result.duration_ms,
                    },
                );
            }
        }

        let total = start.elapsed().as_millis() as u64;

        Ok(WeaveResult {
            canvas_name: canvas.name.clone(),
            layers: layers.clone(),
            outputs,
            total_duration_ms: total,
            success: errors.is_empty(),
            errors,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::executor::PassthroughExecutor;
    use neuromitosis_canvas::{Node, NodeType, Port};

    #[tokio::test]
    async fn test_weave_linear() {
        let mut canvas = Canvas::new("test_weave");
        let a = Node::new("source", NodeType::Source)
            .with_output(Port::output("data"));
        let b = Node::new("transform", NodeType::Transform)
            .with_input(Port::input("data"))
            .with_output(Port::output("result"));
        let c = Node::new("action", NodeType::Action)
            .with_input(Port::input("result"));

        let a_id = a.id;
        let a_out = a.outputs[0].id;
        let b_id = b.id;
        let b_in = b.inputs[0].id;
        let b_out = b.outputs[0].id;
        let c_id = c.id;
        let c_in = c.inputs[0].id;

        canvas.add_node(a).unwrap();
        canvas.add_node(b).unwrap();
        canvas.add_node(c).unwrap();
        canvas.connect(a_id, a_out, b_id, b_in).unwrap();
        canvas.connect(b_id, b_out, c_id, c_in).unwrap();

        let loom = Loom::new(Arc::new(PassthroughExecutor));
        let result = loom.weave(&canvas).await.unwrap();

        assert!(result.success);
        assert_eq!(result.layers.len(), 3);
        assert_eq!(result.outputs.len(), 3);
    }
}
