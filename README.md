# 🧬💿 Neuromitosis

**A learning network powered by [llm.store](https://llm.store)**

> Skills divide. Knowledge propagates. The network evolves.

Neuromitosis is an open skill economy for AI agents. Build workflows on a visual canvas, encode them as portable 💿 **discs**, and share them through [llm.store](https://llm.store) — the npm of agent skills.

---

## 💿 What's a Disc?

A disc is a portable, self-describing container for AI agent skills. Think of it as a package.json for agent workflows:

```json
{
  "metadata": {"name": "email-triage", "version": "1.0.0", "author": "yael"},
  "tracks": [
    {"name": "fetch_emails", "handler": "GMAIL_FETCH_EMAILS", "outputs_to": ["summarize"]},
    {"name": "summarize", "node_type": "transform", "outputs_to": ["notify"]},
    {"name": "notify", "handler": "SLACK_SEND_MESSAGE"}
  ],
  "auth_manifest": [{"toolkit": "gmail"}, {"toolkit": "slack"}],
  "checksum": "a1b2c3d4e5f6g7h8"
}
```

Burn a workflow → share the `.disc` → anyone can load and run it.

## Architecture

```
┌─────────────────────────────────────┐
│           llm.store                 │  ← Discovery & distribution
│   Browse, publish, install 💿       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Neuromitosis                │  ← Composition & visualization
│   Canvas + Loom + Molt + Codec      │
│   Wire skills visually              │
└──────────────┬──────────────────────┘
               │ MCP
┌──────────────▼──────────────────────┐
│          Composio                   │  ← Execution & auth
│   500+ integrations via MCP         │
└─────────────────────────────────────┘
```

## Core Modules

| Module | What | Path |
|--------|------|------|
| **Canvas** 🎨 | Node primitives — the atoms of agency | `src/canvas/` |
| **Loom** 🧶 | Runtime execution engine (topological sort, Kahn's algorithm) | `src/loom/` |
| **Molt** 🦎 | Drift detection and deliberate system evolution | `src/molt/` |
| **Codec** 💿 | Encode/decode/share skill libraries as `.disc` files | `src/codec/` |
| **Trustclaw** 🧠 | Agent brain — LLM orchestration, memory, skill routing | `src/trustclaw/` |

## Quick Start

```bash
# Clone
git clone https://github.com/yaeleureka-afk/neuromitosis.git
cd neuromitosis

# Install
pip install -e .

# Burn your first disc
python -c "
from src.canvas.node import Node, NodeType
from src.loom.runtime import Loom
from src.codec import Encoder

loom = Loom(name='hello')
n1 = Node(name='fetch', node_type=NodeType.SOURCE)
n2 = Node(name='process', node_type=NodeType.TRANSFORM)
n1.connect(n2)
loom.add_node(n1)
loom.add_node(n2)

disc = Encoder.burn(loom, name='hello_world', author='you')
print(disc.to_json())
"
```

## The Vision

**npm** standardized JavaScript packages. **Docker Hub** standardized containers. **Hugging Face** standardized models.

**Neuromitosis + llm.store** standardizes **AI agent skills**.

The `.disc` format is the unit. MCP is the protocol. The canvas is the runtime. [llm.store](https://llm.store) is the marketplace.

Skills that find you. Not the other way around.

## Stack

- **Format**: `.disc` (JSON, self-describing, checksummed)
- **Protocol**: [MCP](https://modelcontextprotocol.io) (Model Context Protocol)
- **Runtime**: Python 3.10+ (canvas, loom, codec, trustclaw)
- **Execution**: [Composio](https://composio.dev) (500+ tool integrations, OAuth handled)
- **Desktop**: Electron + React + React Flow (planned)
- **Registry**: [llm.store](https://llm.store)

## Status

🧬 **Pre-alpha** — Core primitives built, codec functional, learning network forming.

## License

[MIT](LICENSE) — Skills want to be free.

---

*Built with 🧠 by [Yael](https://github.com/yaeleureka-afk) and [Trustclaw](https://composio.dev)*
