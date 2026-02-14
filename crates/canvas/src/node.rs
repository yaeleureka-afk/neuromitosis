//! Node — the atom of a Canvas.

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The four fundamental node types in Neuromitosis.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum NodeType {
    /// Data ingress — Gmail, API, file read, webhook
    Source,
    /// Data transformation — LLM call, filter, map, reduce
    Transform,
    /// Side effect — send email, create issue, write file
    Action,
    /// Approval gate — human-in-the-loop, drift check, policy
    /// Named æ (ash) — the guardian rune
    Guard,
}

/// Direction of a port on a node.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum PortDirection {
    In,
    Out,
}

/// A typed connection point on a node.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Port {
    pub id: Uuid,
    pub name: String,
    pub direction: PortDirection,
    /// Optional type hint (e.g., "string", "email[]", "json")
    pub type_hint: Option<String>,
}

impl Port {
    pub fn input(name: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            direction: PortDirection::In,
            type_hint: None,
        }
    }

    pub fn output(name: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            direction: PortDirection::Out,
            type_hint: None,
        }
    }

    pub fn with_type(mut self, t: impl Into<String>) -> Self {
        self.type_hint = Some(t.into());
        self
    }
}

/// A Node in the Canvas DAG.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    pub id: Uuid,
    pub name: String,
    pub node_type: NodeType,
    pub inputs: Vec<Port>,
    pub outputs: Vec<Port>,
    /// Arbitrary configuration (tool-specific)
    pub config: serde_json::Value,
    /// Optional tool slug (e.g., "GMAIL_FETCH_EMAILS")
    pub tool_slug: Option<String>,
}

impl Node {
    pub fn new(name: impl Into<String>, node_type: NodeType) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            node_type,
            inputs: Vec::new(),
            outputs: Vec::new(),
            config: serde_json::Value::Null,
            tool_slug: None,
        }
    }

    pub fn with_input(mut self, port: Port) -> Self {
        self.inputs.push(port);
        self
    }

    pub fn with_output(mut self, port: Port) -> Self {
        self.outputs.push(port);
        self
    }

    pub fn with_config(mut self, config: serde_json::Value) -> Self {
        self.config = config;
        self
    }

    pub fn with_tool(mut self, slug: impl Into<String>) -> Self {
        self.tool_slug = Some(slug.into());
        self
    }

    /// Find an input port by name.
    pub fn input_port(&self, name: &str) -> Option<&Port> {
        self.inputs.iter().find(|p| p.name == name)
    }

    /// Find an output port by name.
    pub fn output_port(&self, name: &str) -> Option<&Port> {
        self.outputs.iter().find(|p| p.name == name)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_node_creation() {
        let node = Node::new("gmail_fetch", NodeType::Source)
            .with_output(Port::output("emails").with_type("email[]"))
            .with_tool("GMAIL_FETCH_EMAILS");

        assert_eq!(node.name, "gmail_fetch");
        assert_eq!(node.node_type, NodeType::Source);
        assert_eq!(node.outputs.len(), 1);
        assert_eq!(node.tool_slug.as_deref(), Some("GMAIL_FETCH_EMAILS"));
    }

    #[test]
    fn test_guard_node() {
        let guard = Node::new("approval_gate", NodeType::Guard)
            .with_input(Port::input("pending"))
            .with_output(Port::output("approved"))
            .with_output(Port::output("rejected"));

        assert_eq!(guard.node_type, NodeType::Guard);
        assert_eq!(guard.inputs.len(), 1);
        assert_eq!(guard.outputs.len(), 2);
    }
}
