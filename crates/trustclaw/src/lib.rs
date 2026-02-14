//! # Trustclaw 🧠
//!
//! The resident agent — personality, memory, tools, boundaries.
//! Trustclaw is both a user of the Loom AND a node that can be
//! wired into any swarm.

use anyhow::Result;
use serde::{Deserialize, Serialize};
use toml;

/// Trustclaw configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrustclawConfig {
    pub name: String,
    pub personality: String,
    pub writing_style: String,
    pub default_provider: String,
    pub default_model: String,
    pub autonomy: String,
}

impl Default for TrustclawConfig {
    fn default() -> Self {
        Self {
            name: "Trustclaw".into(),
            personality: "sassy & bold".into(),
            writing_style: "Professional".into(),
            default_provider: "anthropic".into(),
            default_model: "claude-sonnet-4-20250514".into(),
            autonomy: "supervised".into(),
        }
    }
}

/// Load config from TOML file.
pub fn load_config(path: &str) -> Result<TrustclawConfig> {
    let content = std::fs::read_to_string(path)?;
    let config: TrustclawConfig = toml::from_str(&content)?;
    Ok(config)
}

// TODO: Phase 4 — full agent loop:
// pub struct Trustclaw { config, provider, memory, tools, security }
// pub async fn chat(&self, message: &str) -> Result<String>
// pub async fn heartbeat(&self) -> Result<()>
