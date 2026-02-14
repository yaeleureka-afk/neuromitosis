//! # Security
//!
//! Boundaries and policy enforcement — per-node, per-graph.

use serde::{Deserialize, Serialize};

/// Autonomy level for the agent.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AutonomyLevel {
    /// Read-only — can observe but not act
    ReadOnly,
    /// Supervised — external actions require approval
    Supervised,
    /// Full — autonomous execution
    Full,
}

impl Default for AutonomyLevel {
    fn default() -> Self {
        Self::Supervised
    }
}

/// Security policy configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityPolicy {
    pub autonomy: AutonomyLevel,
    pub workspace_only: bool,
    pub allowed_commands: Vec<String>,
    pub forbidden_paths: Vec<String>,
    pub require_pairing: bool,
}

impl Default for SecurityPolicy {
    fn default() -> Self {
        Self {
            autonomy: AutonomyLevel::Supervised,
            workspace_only: true,
            allowed_commands: vec![
                "git".into(), "cargo".into(), "ls".into(),
                "cat".into(), "grep".into(),
            ],
            forbidden_paths: vec![
                "/etc".into(), "/root".into(), "/proc".into(),
                "/sys".into(), "~/.ssh".into(), "~/.gnupg".into(),
                "~/.aws".into(),
            ],
            require_pairing: true,
        }
    }
}

/// Check if a command is allowed by policy.
pub fn is_command_allowed(policy: &SecurityPolicy, command: &str) -> bool {
    let base = command.split_whitespace().next().unwrap_or("");
    policy.allowed_commands.iter().any(|c| c == base)
}

/// Check if a path is forbidden by policy.
pub fn is_path_forbidden(policy: &SecurityPolicy, path: &str) -> bool {
    policy.forbidden_paths.iter().any(|fp| path.starts_with(fp))
}
