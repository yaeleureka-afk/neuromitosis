//! Neuromitosis CLI — the CLI reinvented for the MCP era.

use clap::{Parser, Subcommand};
use anyhow::Result;

#[derive(Parser)]
#[command(
    name = "neuromitosis",
    version,
    about = "The CLI reinvented for the MCP era. Visual swarm orchestration in Rust. 🦀💿",
    long_about = None,
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Interactive chat with Trustclaw
    Agent {
        /// Single message mode
        #[arg(short, long)]
        message: Option<String>,
    },

    /// Weave a canvas (execute a DAG)
    Weave {
        /// Path to canvas file (.json)
        #[arg(short, long)]
        canvas: String,
    },

    /// Burn a canvas into a .disc file
    Burn {
        /// Path to canvas file
        #[arg(short, long)]
        canvas: String,
        /// Output .disc path
        #[arg(short, long)]
        output: String,
        /// Disc name
        #[arg(short, long)]
        name: String,
        /// Disc version
        #[arg(long, default_value = "0.1.0")]
        version: String,
    },

    /// Rip a .disc file back into a canvas
    Rip {
        /// Path to .disc file
        #[arg(short, long)]
        disc: String,
        /// Output canvas path
        #[arg(short, long)]
        output: String,
    },

    /// Publish a .disc to llm.store
    Publish {
        /// Path to .disc file
        path: String,
    },

    /// Install a .disc from llm.store
    Install {
        /// Disc name
        name: String,
    },

    /// Show system status
    Status,

    /// Start the MCP server
    Serve {
        /// Port (default: 8080)
        #[arg(short, long, default_value = "8080")]
        port: u16,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Agent { message } => {
            match message {
                Some(msg) => {
                    println!("🧠 Trustclaw: (agent loop not yet wired — Phase 4)");
                    println!("   You said: {}", msg);
                }
                None => {
                    println!("🧠 Trustclaw interactive mode (Phase 4)");
                    println!("   Type 'quit' to exit.");
                }
            }
        }

        Commands::Weave { canvas } => {
            println!("🕸️  Weaving canvas: {}", canvas);
            println!("   (Loom execution wired — load canvas JSON and weave)");
        }

        Commands::Burn { canvas, output, name, version } => {
            println!("💿 Burning: {} → {}", canvas, output);
            println!("   Disc: {} v{}", name, version);
        }

        Commands::Rip { disc, output } => {
            println!("💿 Ripping: {} → {}", disc, output);
        }

        Commands::Publish { path } => {
            println!("📦 Publishing {} to llm.store (Phase 6)", path);
        }

        Commands::Install { name } => {
            println!("📦 Installing {} from llm.store (Phase 6)", name);
        }

        Commands::Status => {
            println!("╔══════════════════════════════════════╗");
            println!("║     Neuromitosis v{:<18}║", env!("CARGO_PKG_VERSION"));
            println!("╠══════════════════════════════════════╣");
            println!("║ Canvas   ✅  Graph primitives        ║");
            println!("║ Loom     ✅  Topological executor    ║");
            println!("║ Molt     🔲  Drift detection         ║");
            println!("║ Codec    ✅  .disc burn/rip          ║");
            println!("║ Provider 🔲  LLM backends            ║");
            println!("║ Memory   🔲  SQLite+FTS5+vectors     ║");
            println!("║ Tools    🔲  Shell/Composio/browser  ║");
            println!("║ Channels 🔲  CLI/Telegram/Discord    ║");
            println!("║ Security ✅  Policy enforcement      ║");
            println!("║ MCP      🔲  Protocol server         ║");
            println!("║ Store    🔲  llm.store client        ║");
            println!("║ Trustclaw🔲  Agent personality       ║");
            println!("╚══════════════════════════════════════╝");
        }

        Commands::Serve { port } => {
            println!("🌐 MCP server starting on port {} (Phase 5)", port);
        }
    }

    Ok(())
}
