//! # Molt
//!
//! Drift detection and re-evaluation.
//! Snapshots canvas state, detects divergence, triggers re-weave.

use anyhow::Result;
use chrono::{DateTime, Utc};
use neuromitosis_canvas::Canvas;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// A snapshot of a canvas execution state.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Snapshot {
    pub id: Uuid,
    pub canvas_name: String,
    pub timestamp: DateTime<Utc>,
    pub node_outputs: serde_json::Value,
    pub checksum: String,
}

/// Drift between two snapshots.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Drift {
    pub score: f64,
    pub changed_nodes: Vec<Uuid>,
    pub description: String,
}

/// Evaluate drift between expected and actual state.
pub fn evaluate(expected: &Snapshot, actual: &Snapshot) -> Drift {
    let changed = if expected.checksum != actual.checksum {
        vec![Uuid::new_v4()] // placeholder — real impl diffs node-by-node
    } else {
        vec![]
    };
    let score = if changed.is_empty() { 0.0 } else { 1.0 };
    Drift {
        score,
        changed_nodes: changed,
        description: if score > 0.0 {
            "State has drifted from expected snapshot.".into()
        } else {
            "No drift detected.".into()
        },
    }
}

/// Should we re-weave? Default threshold: drift > 0.5
pub fn should_reweave(drift: &Drift, threshold: f64) -> bool {
    drift.score > threshold
}
