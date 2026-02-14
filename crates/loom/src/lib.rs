//! # Loom
//!
//! The topological execution engine for Neuromitosis.
//! Takes a Canvas (DAG) and weaves it — executing nodes in parallel layers
//! determined by Kahn's algorithm.

pub mod topology;
pub mod runtime;
pub mod executor;

pub use runtime::{Loom, WeaveResult, NodeOutput};
pub use topology::TopologyError;
