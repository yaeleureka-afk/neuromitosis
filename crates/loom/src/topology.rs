//! Topology — DAG validation and layer computation via Kahn's algorithm.

use neuromitosis_canvas::Canvas;
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, thiserror::Error)]
pub enum TopologyError {
    #[error("graph contains a cycle (processed {processed} of {total} nodes)")]
    CycleDetected { processed: usize, total: usize },
    #[error("empty canvas — nothing to weave")]
    EmptyCanvas,
}

/// Compute execution layers using Kahn's algorithm.
/// Returns Vec<Vec<Uuid>> where each inner Vec is a set of nodes
/// that can execute in parallel (same topological depth).
pub fn compute_layers(canvas: &Canvas) -> Result<Vec<Vec<Uuid>>, TopologyError> {
    if canvas.node_count() == 0 {
        return Err(TopologyError::EmptyCanvas);
    }

    // Build in-degree map
    let mut in_degree: HashMap<Uuid, usize> = HashMap::new();
    for id in canvas.nodes.keys() {
        in_degree.insert(*id, 0);
    }
    for yarn in &canvas.yarns {
        *in_degree.entry(yarn.to_node).or_insert(0) += 1;
    }

    // Start with zero in-degree nodes
    let mut queue: Vec<Uuid> = in_degree
        .iter()
        .filter(|(_, &deg)| deg == 0)
        .map(|(&id, _)| id)
        .collect();

    let mut layers: Vec<Vec<Uuid>> = Vec::new();
    let mut processed = 0;

    while !queue.is_empty() {
        // Current layer = all nodes in the queue
        let current_layer = queue.clone();
        processed += current_layer.len();
        layers.push(current_layer.clone());

        // Prepare next layer
        let mut next_queue = Vec::new();
        for node_id in &current_layer {
            for successor in canvas.successors(*node_id) {
                if let Some(deg) = in_degree.get_mut(&successor) {
                    *deg -= 1;
                    if *deg == 0 {
                        next_queue.push(successor);
                    }
                }
            }
        }
        queue = next_queue;
    }

    if processed != canvas.node_count() {
        return Err(TopologyError::CycleDetected {
            processed,
            total: canvas.node_count(),
        });
    }

    Ok(layers)
}

/// Validate that a canvas is a valid DAG.
pub fn validate(canvas: &Canvas) -> Result<(), TopologyError> {
    compute_layers(canvas).map(|_| ())
}

#[cfg(test)]
mod tests {
    use super::*;
    use neuromitosis_canvas::{Node, NodeType, Port};

    #[test]
    fn test_linear_topology() {
        let mut canvas = Canvas::new("linear");

        let a = Node::new("a", NodeType::Source).with_output(Port::output("out"));
        let b = Node::new("b", NodeType::Transform)
            .with_input(Port::input("in"))
            .with_output(Port::output("out"));
        let c = Node::new("c", NodeType::Action).with_input(Port::input("in"));

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

        let layers = compute_layers(&canvas).unwrap();
        assert_eq!(layers.len(), 3); // 3 sequential layers
        assert_eq!(layers[0].len(), 1); // a
        assert_eq!(layers[1].len(), 1); // b
        assert_eq!(layers[2].len(), 1); // c
    }

    #[test]
    fn test_parallel_topology() {
        let mut canvas = Canvas::new("parallel");

        let src = Node::new("src", NodeType::Source)
            .with_output(Port::output("out1"))
            .with_output(Port::output("out2"));
        let t1 = Node::new("t1", NodeType::Transform)
            .with_input(Port::input("in"))
            .with_output(Port::output("out"));
        let t2 = Node::new("t2", NodeType::Transform)
            .with_input(Port::input("in"))
            .with_output(Port::output("out"));
        let sink = Node::new("sink", NodeType::Action)
            .with_input(Port::input("in1"))
            .with_input(Port::input("in2"));

        let src_id = src.id;
        let src_out1 = src.outputs[0].id;
        let src_out2 = src.outputs[1].id;
        let t1_id = t1.id;
        let t1_in = t1.inputs[0].id;
        let t1_out = t1.outputs[0].id;
        let t2_id = t2.id;
        let t2_in = t2.inputs[0].id;
        let t2_out = t2.outputs[0].id;
        let sink_id = sink.id;
        let sink_in1 = sink.inputs[0].id;
        let sink_in2 = sink.inputs[1].id;

        canvas.add_node(src).unwrap();
        canvas.add_node(t1).unwrap();
        canvas.add_node(t2).unwrap();
        canvas.add_node(sink).unwrap();

        canvas.connect(src_id, src_out1, t1_id, t1_in).unwrap();
        canvas.connect(src_id, src_out2, t2_id, t2_in).unwrap();
        canvas.connect(t1_id, t1_out, sink_id, sink_in1).unwrap();
        canvas.connect(t2_id, t2_out, sink_id, sink_in2).unwrap();

        let layers = compute_layers(&canvas).unwrap();
        assert_eq!(layers.len(), 3); // src | t1,t2 | sink
        assert_eq!(layers[0].len(), 1); // src
        assert_eq!(layers[1].len(), 2); // t1, t2 in parallel
        assert_eq!(layers[2].len(), 1); // sink
    }
}
