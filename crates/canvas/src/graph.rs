//! Canvas — the DAG container.

use crate::node::Node;
use crate::yarn::Yarn;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use uuid::Uuid;

/// Errors that can occur when modifying a Canvas.
#[derive(Debug, thiserror::Error)]
pub enum CanvasError {
    #[error("node {0} not found")]
    NodeNotFound(Uuid),
    #[error("port {0} not found on node {1}")]
    PortNotFound(Uuid, Uuid),
    #[error("adding yarn would create a cycle")]
    CycleDetected,
    #[error("duplicate node id {0}")]
    DuplicateNode(Uuid),
}

/// A Canvas is a directed acyclic graph of Nodes connected by Yarns.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Canvas {
    pub nodes: HashMap<Uuid, Node>,
    pub yarns: Vec<Yarn>,
    pub name: String,
    pub description: Option<String>,
}

impl Canvas {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            nodes: HashMap::new(),
            yarns: Vec::new(),
            name: name.into(),
            description: None,
        }
    }

    /// Add a node to the canvas.
    pub fn add_node(&mut self, node: Node) -> Result<Uuid, CanvasError> {
        let id = node.id;
        if self.nodes.contains_key(&id) {
            return Err(CanvasError::DuplicateNode(id));
        }
        self.nodes.insert(id, node);
        Ok(id)
    }

    /// Connect two nodes via their ports.
    pub fn connect(
        &mut self,
        from_node: Uuid,
        from_port: Uuid,
        to_node: Uuid,
        to_port: Uuid,
    ) -> Result<Uuid, CanvasError> {
        // Validate nodes exist
        if !self.nodes.contains_key(&from_node) {
            return Err(CanvasError::NodeNotFound(from_node));
        }
        if !self.nodes.contains_key(&to_node) {
            return Err(CanvasError::NodeNotFound(to_node));
        }

        let yarn = Yarn::new(from_node, from_port, to_node, to_port);
        let id = yarn.id;

        // Check for cycles before adding
        if self.would_create_cycle(from_node, to_node) {
            return Err(CanvasError::CycleDetected);
        }

        self.yarns.push(yarn);
        Ok(id)
    }

    /// Get all nodes with no incoming yarns (entry points).
    pub fn sources(&self) -> Vec<&Node> {
        let has_incoming: HashSet<Uuid> = self.yarns.iter().map(|y| y.to_node).collect();
        self.nodes
            .values()
            .filter(|n| !has_incoming.contains(&n.id))
            .collect()
    }

    /// Get all nodes with no outgoing yarns (exit points).
    pub fn sinks(&self) -> Vec<&Node> {
        let has_outgoing: HashSet<Uuid> = self.yarns.iter().map(|y| y.from_node).collect();
        self.nodes
            .values()
            .filter(|n| !has_outgoing.contains(&n.id))
            .collect()
    }

    /// Get predecessors of a node (nodes that feed into it).
    pub fn predecessors(&self, node_id: Uuid) -> Vec<Uuid> {
        self.yarns
            .iter()
            .filter(|y| y.to_node == node_id)
            .map(|y| y.from_node)
            .collect()
    }

    /// Get successors of a node (nodes it feeds into).
    pub fn successors(&self, node_id: Uuid) -> Vec<Uuid> {
        self.yarns
            .iter()
            .filter(|y| y.from_node == node_id)
            .map(|y| y.to_node)
            .collect()
    }

    /// Check if adding an edge from → to would create a cycle.
    fn would_create_cycle(&self, from: Uuid, to: Uuid) -> bool {
        if from == to {
            return true;
        }
        // BFS from `to` to see if we can reach `from`
        let mut visited = HashSet::new();
        let mut queue = vec![to];
        while let Some(current) = queue.pop() {
            if current == from {
                return true; // cycle!
            }
            if visited.insert(current) {
                for successor in self.successors(current) {
                    queue.push(successor);
                }
            }
        }
        false
    }

    /// Number of nodes in the canvas.
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    /// Number of yarns (edges) in the canvas.
    pub fn yarn_count(&self) -> usize {
        self.yarns.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::node::{NodeType, Port};

    fn make_test_canvas() -> Canvas {
        let mut canvas = Canvas::new("test");

        let source = Node::new("source", NodeType::Source)
            .with_output(Port::output("out"));
        let transform = Node::new("transform", NodeType::Transform)
            .with_input(Port::input("in"))
            .with_output(Port::output("out"));
        let action = Node::new("action", NodeType::Action)
            .with_input(Port::input("in"));

        let s_id = source.id;
        let s_out = source.outputs[0].id;
        let t_id = transform.id;
        let t_in = transform.inputs[0].id;
        let t_out = transform.outputs[0].id;
        let a_id = action.id;
        let a_in = action.inputs[0].id;

        canvas.add_node(source).unwrap();
        canvas.add_node(transform).unwrap();
        canvas.add_node(action).unwrap();
        canvas.connect(s_id, s_out, t_id, t_in).unwrap();
        canvas.connect(t_id, t_out, a_id, a_in).unwrap();

        canvas
    }

    #[test]
    fn test_canvas_structure() {
        let canvas = make_test_canvas();
        assert_eq!(canvas.node_count(), 3);
        assert_eq!(canvas.yarn_count(), 2);
        assert_eq!(canvas.sources().len(), 1);
        assert_eq!(canvas.sinks().len(), 1);
    }

    #[test]
    fn test_cycle_detection() {
        let mut canvas = Canvas::new("cycle_test");
        let a = Node::new("a", NodeType::Source).with_output(Port::output("out"));
        let b = Node::new("b", NodeType::Transform)
            .with_input(Port::input("in"))
            .with_output(Port::output("out"));

        let a_id = a.id;
        let a_out = a.outputs[0].id;
        let b_id = b.id;
        let b_in = b.inputs[0].id;
        let b_out = b.outputs[0].id;

        canvas.add_node(a).unwrap();
        canvas.add_node(b).unwrap();
        canvas.connect(a_id, a_out, b_id, b_in).unwrap();

        // This should fail — cycle: b → a, but a → b already exists
        let result = canvas.connect(b_id, b_out, a_id, a_out);
        assert!(result.is_err());
    }
}
