<p align="center">
  <strong>💿 Neuromitosis</strong>
</p>

<h1 align="center">Neuromitosis 🦀💿</h1>

<p align="center">
  <strong>The CLI reinvented for the MCP era.</strong><br>
  Visual swarm orchestration in Rust. Skills divide. Knowledge propagates. The network evolves.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="https://llm.store"><img src="https://img.shields.io/badge/registry-llm.store-purple.svg" alt="llm.store" /></a>
</p>

## What Is This

Neuromitosis is a **Rust-native AI agent orchestration engine** built on three ideas:

1. **Everything is a graph** — workflows are DAGs of typed nodes, not chat loops
2. **Everything is a trait** — swap LLM providers, memory, tools, channels via config
3. **Everything is MCP** — tools discover themselves at runtime via [Model Context Protocol](https://modelcontextprotocol.io)

Read [MCP.md](MCP.md) for the full architecture vision.

## Quick Start

```bash
git clone https://github.com/yaeleureka-afk/neuromitosis.git
cd neuromitosis
cargo build --release
cargo run -- status
```

## Architecture

```
12 crates, 1 binary, 0 compromises

Canvas  → Loom   → Molt      (graph → execute → evaluate)
Codec   → Store               (encode → distribute)
Providers → Memory → Tools    (think → remember → act)
Channels → Security → MCP     (communicate → protect → discover)
Trustclaw                      (the resident agent)
```

| Crate | Purpose | Status |
|-------|---------|--------|
| `canvas` | Node graph primitives (Node, Yarn, Port, Canvas) | ✅ |
| `loom` | Topological executor (Kahn's algorithm, async parallel) | ✅ |
| `molt` | Drift detection & re-evaluation | 🔲 |
| `codec` | .disc format — burn/rip portable skills 💿 | ✅ |
| `providers` | LLM backends (Anthropic, OpenAI, Ollama, OpenRouter) | 🔲 |
| `memory` | SQLite + FTS5 + vector embeddings | 🔲 |
| `tools` | Shell, files, Composio (500+ integrations), browser | 🔲 |
| `channels` | CLI, Telegram, Discord, Slack, webhook | 🔲 |
| `security` | Per-node boundaries, workspace scoping, encrypted secrets | ✅ |
| `mcp` | MCP server for Electron frontend | 🔲 |
| `store` | llm.store client — publish/install/search | 🔲 |
| `trustclaw` | Agent personality layer 🧠 | 🔲 |

## CLI

```bash
neuromitosis agent              # Interactive chat with Trustclaw
neuromitosis agent -m "Hello"   # Single message
neuromitosis weave -c flow.json # Execute a canvas DAG
neuromitosis burn -c flow.json -o skill.disc -n "my-skill"  # Encode
neuromitosis rip -d skill.disc -o flow.json                 # Decode
neuromitosis publish skill.disc # Push to llm.store
neuromitosis install email-triage # Pull from llm.store
neuromitosis status             # System status
neuromitosis serve              # Start MCP server
```

## The .disc Format 💿

Skills encoded as portable files — the MP3 of agent capabilities.

```bash
neuromitosis burn -c morning-ritual.json -o morning.disc -n "morning-ritual"
neuromitosis rip -d morning.disc -o restored.json
```

See [MCP.md](MCP.md) for the full Codec spec.

## llm.store

The npm of agent skills. Coming soon at [llm.store](https://llm.store).

## License

MIT — see [LICENSE](LICENSE)

---

*Built with 🦀 by Yael. Powered by [Composio](https://composio.dev).*
