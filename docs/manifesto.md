# 🧬 Neuromitosis Manifesto

> Skills divide. Knowledge propagates. The network evolves.

## The Problem

AI agents are powerful but isolated. Every team builds their own integrations,
their own auth flows, their own workflows from scratch. It's like every website
building their own web server in 1995.

The skill gap isn't intelligence — it's distribution.

## The Insight

What if agent skills were **portable**? What if you could encode a workflow,
hand it to someone, and it just worked? What if there was a place to browse,
publish, and install agent capabilities the way npm works for JavaScript?

## The Solution: Neuromitosis

A learning network built on three primitives:

### 1. The Format: 💿 `.disc`

A disc is a portable container for agent skills. It captures:
- **Tracks**: Individual skills (nodes with execution context)
- **Topology**: How tracks wire together
- **Auth manifest**: What connections are needed (not the keys)
- **Checksum**: Integrity verification

The `.disc` format is to agent skills what `package.json` is to JavaScript packages.

### 2. The Protocol: MCP

The Model Context Protocol is the transport layer. Skills announce themselves
at runtime. Clients discover capabilities without downloading everything first.
New skills appear the moment they're published.

npm requires you to know what you're looking for. MCP lets skills find you.

### 3. The Marketplace: llm.store

The canonical registry for agent skills. Browse, publish, install.
`nm install email-triage` and you're running.

## The Architecture

```
Canvas (build) → Loom (execute) → Molt (evolve) → Codec (encode) → llm.store (share)
```

Each layer does one thing:
- **Canvas**: Visual node editor — drag, connect, compose
- **Loom**: Topological execution engine — runs the graph
- **Molt**: Drift detection — knows when to evolve
- **Codec**: Serialization — burns and rips .disc files
- **Trustclaw**: Agent brain — LLM orchestration and memory
- **llm.store**: The marketplace — skills become transferable

## The Philosophy

### Cells, Not Monoliths
Skills are atomic units that combine into organisms. Like biological cells,
they divide (fork), specialize (configure), and propagate (share). The network
grows through mitosis, not monolithic construction.

### Open Format, Open Protocol
The `.disc` format isn't locked to Neuromitosis. Any agent framework that reads
JSON can parse it. Any MCP client can discover skills on llm.store. We win by
being the best player, not the only player.

### The 4D Molt Framework
1. **æ Loom** — Topological execution with observable data flow
2. **Swarm-native thinking** — Multi-agent by default, not bolted on
3. **Topology-based debugging** — See what happened, where, and why
4. **Deliberate evolution** — Systems that know when to shed their skin

## The Analogy

**npm** proved that a package registry becomes infrastructure.
**Docker Hub** proved that a container registry becomes infrastructure.
**Hugging Face** proved that a model registry becomes infrastructure.

**Neuromitosis + llm.store** proves that a **skill registry** becomes infrastructure.

The pattern is always the same:
```
New paradigm → standard unit → registry → gravity well → infrastructure
```

We're building the gravity well. 💿🧬

---

*Neuromitosis — named for the process by which cells divide and propagate.
Every skill shared is a division. Every install is propagation.
The network learns by splitting.*
