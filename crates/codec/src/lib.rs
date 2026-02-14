//! # Codec
//!
//! Portable skill encoding — the .disc format (LLM CDs). 💿
//! Burn: Canvas → Disc. Rip: Disc → Canvas. Play: Load + execute.

use anyhow::Result;
use chrono::{DateTime, Utc};
use neuromitosis_canvas::{Canvas, Node, Yarn};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use uuid::Uuid;

pub const FORMAT_VERSION: &str = "0.1.0";

/// A Track is a single skill — a graph fragment.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Track {
    pub name: String,
    pub description: Option<String>,
    pub nodes: Vec<Node>,
    pub yarns: Vec<Yarn>,
    pub auth_requirements: Vec<AuthRequirement>,
}

/// An auth requirement for a track (e.g., "gmail: read" scope).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthRequirement {
    pub service: String,
    pub scopes: Vec<String>,
}

/// Disc metadata.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscMetadata {
    pub name: String,
    pub version: String,
    pub author: Option<String>,
    pub description: Option<String>,
    pub created_at: DateTime<Utc>,
    pub format_version: String,
}

/// A Disc is a collection of tracks — a portable skill package. 💿
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Disc {
    pub metadata: DiscMetadata,
    pub tracks: Vec<Track>,
    pub checksum: String,
}

/// Burn: Canvas → Disc
pub fn burn(canvas: &Canvas, name: &str, version: &str) -> Result<Disc> {
    let track = Track {
        name: canvas.name.clone(),
        description: canvas.description.clone(),
        nodes: canvas.nodes.values().cloned().collect(),
        yarns: canvas.yarns.clone(),
        auth_requirements: vec![], // TODO: extract from node tool_slugs
    };

    let metadata = DiscMetadata {
        name: name.to_string(),
        version: version.to_string(),
        author: None,
        description: canvas.description.clone(),
        created_at: Utc::now(),
        format_version: FORMAT_VERSION.to_string(),
    };

    let mut disc = Disc {
        metadata,
        tracks: vec![track],
        checksum: String::new(),
    };

    // Compute checksum over serialized tracks
    let tracks_json = serde_json::to_string(&disc.tracks)?;
    let mut hasher = Sha256::new();
    hasher.update(tracks_json.as_bytes());
    disc.checksum = format!("{:x}", hasher.finalize());

    Ok(disc)
}

/// Rip: Disc → Canvas (first track)
pub fn rip(disc: &Disc) -> Result<Canvas> {
    let track = disc
        .tracks
        .first()
        .ok_or_else(|| anyhow::anyhow!("disc has no tracks"))?;

    let mut canvas = Canvas::new(&track.name);
    for node in &track.nodes {
        canvas.nodes.insert(node.id, node.clone());
    }
    canvas.yarns = track.yarns.clone();

    Ok(canvas)
}

#[cfg(test)]
mod tests {
    use super::*;
    use neuromitosis_canvas::{Node, NodeType, Port};

    #[test]
    fn test_burn_and_rip() {
        let mut canvas = Canvas::new("test_skill");
        let a = Node::new("src", NodeType::Source).with_output(Port::output("out"));
        let b = Node::new("act", NodeType::Action).with_input(Port::input("in"));
        let a_id = a.id;
        let a_out = a.outputs[0].id;
        let b_id = b.id;
        let b_in = b.inputs[0].id;
        canvas.add_node(a).unwrap();
        canvas.add_node(b).unwrap();
        canvas.connect(a_id, a_out, b_id, b_in).unwrap();

        let disc = burn(&canvas, "test", "0.1.0").unwrap();
        assert_eq!(disc.metadata.name, "test");
        assert!(!disc.checksum.is_empty());

        let restored = rip(&disc).unwrap();
        assert_eq!(restored.node_count(), 2);
        assert_eq!(restored.yarn_count(), 1);
    }
}
