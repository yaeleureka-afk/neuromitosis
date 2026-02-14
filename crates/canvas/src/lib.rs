//! # Canvas
//!
//! Graph primitives for Neuromitosis.
//! A Canvas is a directed acyclic graph of Nodes connected by Yarns.
//! Each Node has typed Ports (input/output). The Loom weaves the Canvas.

pub mod node;
pub mod yarn;
pub mod graph;

pub use node::{Node, NodeType, Port, PortDirection};
pub use yarn::Yarn;
pub use graph::Canvas;
