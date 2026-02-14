# MCP.md — The Neuromitosis Protocol

> *"The CLI reinvented for the MCP era."*
> Every node is a tool. Every tool is a node. MCP protocol underneath.

## What Is This

Neuromitosis is a **visual swarm orchestration engine** written in Rust.
It treats AI agent workflows as **directed acyclic graphs** (DAGs) where:

- **Nodes** are capabilities (LLM calls, API actions, data transforms, approval gates)
- **Yarns** are typed connections between node ports
- **The Loom** weaves the graph — executing nodes in topological order with async parallelism
- **Molt** detects drift — when reality diverges from the plan, the graph re-evaluates
- **Codec** encodes skills as portable `.disc` files — the MP3 of agent capabilities
- **Trustclaw** is the resident agent — personality, memory, boundaries

## The MCP Connection

[Model Context Protocol](https://modelcontextprotocol.io) is the transport layer.
Every Neuromitosis tool auto-exposes as an MCP tool. The Electron frontend discovers
tools at runtime via MCP — new integrations appear as draggable canvas nodes without
code changes.

```
┌─────────────────────────────────────────────────┐
│  Electron Desktop (React + @xyflow/react)       │
│  ┌───────────────────────────────────────────┐  │
│  │  Canvas: drag nodes, connect yarns        │  │
│  │  Each node = MCP tool call                │  │
│  └───────────────┬───────────────────────────┘  │
│                  │ WebMCP (WebSocket)            │
│  ┌───────────────▼───────────────────────────┐  │
│  │  MCP Server (Rust, in-process)            │  │
│  │  ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐ │  │
│  │  │ Canvas  │ │ Loom │ │ Molt │ │Codec │ │  │
│  │  └─────────┘ └──────┘ └──────┘ └──────┘ │  │
│  │  ┌──────────┐ ┌────────┐ ┌────────────┐ │  │
│  │  │Trustclaw │ │Memory  │ │ Composio   │ │  │
│  │  └──────────┘ └────────┘ └────────────┘ │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Architecture: Everything Is a Trait

Inspired by ZeroClaw's "swap anything with config" philosophy, but graph-first:

| Subsystem    | Trait            | Purpose                                      |
|-------------|------------------|----------------------------------------------|
| **Canvas**  | `Node`, `Yarn`   | Graph primitives — the atoms                 |
| **Loom**    | `Runtime`        | Topological execution — the scheduler        |
| **Molt**    | `Evaluator`      | Drift detection — the immune system          |
| **Codec**   | `Encoder/Decoder`| Skill portability — the file format          |
| **Providers** | `Provider`     | LLM backends — swap with config              |
| **Memory**  | `Memory`         | Persistence — SQLite+FTS5+vectors            |
| **Tools**   | `Tool`           | Capabilities — shell, files, Composio, etc.  |
| **Channels** | `Channel`       | I/O — CLI, Telegram, Discord, Slack, webhook |
| **Security** | `SecurityPolicy`| Boundaries — per-node, per-graph             |
| **MCP**     | `McpTransport`   | Protocol — WebSocket, stdio                  |
| **Store**   | `Registry`       | llm.store — publish/install .disc files      |
| **Trustclaw** | Agent loop     | Personality + memory + tools + boundaries    |

## The Codec: LLM CDs 💿

Skills are encoded as `.disc` files — portable, cross-framework, shareable.

```
Disc {
    metadata: { name, version, author, description }
    tracks: [
        Track {
            nodes: [...],      // The graph fragment
            yarns: [...],      // Connections
            auth: [...],       // Required OAuth scopes
            topology: [...]    // Execution order hint
        }
    ]
    checksum: sha256
}
```

- **Burn**: Canvas → `.disc` (encode a workflow as a skill)
- **Rip**: `.disc` → Canvas (decode a skill into a runnable graph)
- **Play**: Load + execute in one step

The `.disc` format is JSON-based, not Neuromitosis-exclusive.
Any agent framework could parse it. But it plays best here.

## llm.store — The Registry

`llm.store` is the npm of agent skills.

```bash
neuromitosis publish morning-ritual.disc    # Push to registry
neuromitosis install email-triage           # Pull from registry
neuromitosis search "github workflow"       # Discover skills
```

**Phasing:**
1. Burn real discs first (you need records before opening a store)
2. CLI: `neuromitosis publish` / `neuromitosis install`
3. MCP endpoint: `mcp://llm.store/v1/skills`
4. Pretty storefront last

## The Platform Equation

```
.disc format    = package.json     (what)
MCP             = install protocol (how)
Canvas          = runtime          (where)
llm.store       = npm registry     (from where)
Loom            = node runtime     (execution)
Trustclaw       = npx              (agent that runs it)
```

## Project Structure

```
neuromitosis/
├── Cargo.toml              # Workspace
├── MCP.md                  # You are here
├── crates/
│   ├── canvas/             # Graph primitives
│   ├── loom/               # Topological executor
│   ├── molt/               # Drift detection
│   ├── codec/              # .disc format
│   ├── providers/          # LLM backends
│   ├── memory/             # SQLite + FTS5 + vectors
│   ├── tools/              # Shell, files, Composio
│   ├── channels/           # CLI, Telegram, Discord
│   ├── security/           # Boundaries & policy
│   ├── mcp/                # MCP server
│   ├── store/              # llm.store client
│   └── trustclaw/          # Agent personality
├── src/main.rs             # CLI entry
├── packages/desktop/       # Electron frontend (preserved)
└── docs/
```

## Building

```bash
cargo build --release       # ~3-5MB binary
cargo test                  # Run all crate tests
cargo run -- agent          # Interactive chat
cargo run -- weave          # Execute a canvas
cargo run -- burn skill.disc # Encode a skill
cargo run -- status         # System status
```

## Philosophy

1. **Graph-first**: Everything is a node in a DAG. Not a chat loop — a topology.
2. **Trait-everything**: Swap providers, memory, channels, tools via config. Zero code changes.
3. **MCP-native**: Tools discover themselves at runtime. The canvas is the IDE.
4. **Portable skills**: `.disc` files work anywhere. Neuromitosis is the best player, not the only one.
5. **Security by default**: Per-node boundaries, workspace scoping, encrypted secrets.
6. **Single binary**: `cargo install neuromitosis` — done. No Python, no Node, no Docker.

## Prior Art & Inspiration

- **ZeroClaw** — trait-based Rust agent architecture (provider/memory/tool/channel abstraction)
- **FFmpeg** — encode/decode/transcode paradigm (→ Codec module)
- **npm** — package registry model (→ llm.store)
- **React Flow** — node-based visual programming (→ Canvas frontend)
- **MCP** — Model Context Protocol (→ transport layer)

---

*Built with 🦀 by Yael. Powered by Composio.*
*The CLI reinvented for the MCP era.*
