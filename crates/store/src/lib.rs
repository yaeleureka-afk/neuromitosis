//! # Store
//!
//! llm.store client — publish, install, and search .disc files.

use anyhow::Result;
use neuromitosis_codec::Disc;
use serde::{Deserialize, Serialize};

/// Registry entry returned by search.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegistryEntry {
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub author: Option<String>,
    pub downloads: u64,
}

/// Store client configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StoreConfig {
    pub registry_url: String,
    pub api_key: Option<String>,
}

impl Default for StoreConfig {
    fn default() -> Self {
        Self {
            registry_url: "https://llm.store/api/v1".to_string(),
            api_key: None,
        }
    }
}

// TODO: Phase 6 — implement publish/install/search against llm.store API
// pub async fn publish(config: &StoreConfig, disc: &Disc) -> Result<()>
// pub async fn install(config: &StoreConfig, name: &str) -> Result<Disc>
// pub async fn search(config: &StoreConfig, query: &str) -> Result<Vec<RegistryEntry>>
