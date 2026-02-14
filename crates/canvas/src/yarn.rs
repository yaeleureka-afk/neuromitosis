//! Yarn — a directed edge connecting two ports.

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// A Yarn connects an output port on one node to an input port on another.
/// Data flows from `from_node.from_port` → `to_node.to_port`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Yarn {
    pub id: Uuid,
    pub from_node: Uuid,
    pub from_port: Uuid,
    pub to_node: Uuid,
    pub to_port: Uuid,
    /// Optional label for debugging/display
    pub label: Option<String>,
}

impl Yarn {
    pub fn new(from_node: Uuid, from_port: Uuid, to_node: Uuid, to_port: Uuid) -> Self {
        Self {
            id: Uuid::new_v4(),
            from_node,
            from_port,
            to_node,
            to_port,
            label: None,
        }
    }

    pub fn with_label(mut self, label: impl Into<String>) -> Self {
        self.label = Some(label.into());
        self
    }
}
