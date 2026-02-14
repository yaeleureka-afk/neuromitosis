# 🧬 Neuromitosis Architecture

## System Overview

Neuromitosis is a learning network for AI agent skills, powered by [llm.store](https://llm.store).

```
┌──────────────────────────────────────────────────────┐
│                    llm.store                          │
│         Discovery, distribution, marketplace          │
│              mcp://llm.store/v1/skills               │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│                   Neuromitosis                        │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Canvas 🎨│→│  Loom  🧶│→│  Molt  🦎│           │
│  │  (nodes)  │  │(runtime) │  │ (evolve) │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│       ↕              ↕             ↕                  │
│  ┌──────────────────────────────────────────┐        │
│  │           Codec 💿                        │        │
│  │   Encoder (burn) ←→ Disc ←→ Decoder (rip)│        │
│  │                    ↕                      │        │
│  │              Library (shelf)              │        │
│  └──────────────────────────────────────────┘        │
│       ↕                                               │
│  ┌──────────┐  ┌──────────┐                          │
│  │Trustclaw │  │  Skills  │                          │
│  │  🧠 agent│←→│(Composio)│                          │
│  └──────────┘  └──────────┘                          │
└──────────────────────────────────────────────────────┘
                         │ MCP
┌────────────────────────▼─────────────────────────────┐
│                    Composio                           │
│            500+ integrations, OAuth handled           │
└──────────────────────────────────────────────────────┘
```

## Module Map

### Canvas (`src/canvas/`)
The visual composition layer. Nodes are the atomic unit of agency.

- **Node**: Base primitive with typed I/O buffers, health tracking, memory
- **NodeType**: Source, Transform, Action, Guard, Control
- **Yarn**: Typed connections (data, signal, state, guard)

### Loom (`src/loom/`)
The æ loom — runtime execution engine.

- Topological sort via Kahn's algorithm
- Guard node interrupt support
- Molt signal propagation
- Execution logging

### Molt (`src/molt/`)
Deliberate system evolution.

- Drift detection per node
- Threshold-based molt triggering
- Molt history tracking
- Reweave proposals

### Codec (`src/codec/`)
💿 The disc encoding/decoding system. The heart of the skill economy.

- **format.py**: `.disc` specification (Track, Disc, AuthRequirement, DiscMetadata)
- **encoder.py**: Loom → Disc (burn)
- **decoder.py**: Disc → Loom (rip/play)
- **library.py**: Local disc collection (~/.neuromitosis/library/)

### Trustclaw (`src/trustclaw/`)
🧠 The agent brain.

- LLM-agnostic orchestration (Claude, OpenAI, Ollama)
- Composio-native skill mapping
- Persistent memory (JSON, upgradeable to ChromaDB)
- Confirmation boundary for external actions

## Data Flow

### Burn (create a 💿)
```
Canvas nodes → Loom wiring → Encoder.burn() → .disc file → Library.save()
```

### Rip (load a 💿)
```
Library.load() → .disc file → Decoder.load() → Loom → weave()
```

### Share (publish a 💿)
```
Library.export() → llm.store API → MCP discovery → other users
```

### Install (get a 💿)
```
llm.store → nm install → Library.import() → Decoder.load() → Canvas
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| JSON format for .disc | Human-readable, git-friendly, debuggable |
| Composio as execution primitive | 500+ integrations without building them |
| MCP as discovery protocol | Skills announce themselves at runtime |
| Open format | Any agent framework can parse .disc files |
| Visual runtime | Canvas makes skills accessible to non-devs |
| Auth manifests (not keys) | Discs declare what they need, not credentials |
| Checksum integrity | Tamper detection built into the format |

## Planned: Monorepo Structure

```
neuromitosis/
├── packages/
│   ├── core/         # Python: canvas, loom, molt, codec, trustclaw
│   ├── desktop/      # Electron: visual canvas app
│   ├── cli/          # nm burn, rip, install, publish
│   ├── mcp-server/   # Composio-backed MCP endpoint
│   └── store/        # llm.store API + frontend
├── discs/            # First-party 💿 skill library
├── docs/
└── tests/
```
