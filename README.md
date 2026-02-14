# 🧬 Midio

**Visual canvas for composing AI agent swarms.**

Midio is a node-based composition tool where you drag, connect, and orchestrate AI agents into living workflows — not pipelines, not DAGs, but *swarms* that breathe, molt, and evolve.

---

## Core Concepts

### The 4D Manifold
Every Midio canvas operates across four dimensions:

| Dimension | What it means |
|-----------|--------------|
| **Space** | The visual topology — where nodes sit, how yarn connects them |
| **Time** | Timeline replay, version history, temporal debugging |
| **Agency** | Each node has autonomous behavior — planners plan, verifiers verify, deployers deploy |
| **Invariant** | æ guard nodes — anchors that enforce constraints across the swarm |

### æ Loom
The æ loom is Midio's runtime. It weaves agent nodes together through *yarn* — typed connections that carry data, signals, and state between nodes. The loom doesn't just execute; it **observes**, tracking drift between intended and actual behavior.

### Molt
Systems evolve. When a path is failing or a topology has outgrown its design, Midio supports **Molt** — a deliberate re-evaluation, rewind, and re-weave of the swarm. Not a hotfix. A metamorphosis.

---

## Project Structure

```
midio/
├── README.md              # You are here
├── LICENSE                # MIT
├── .gitignore
├── manifesto.md           # The vision document
├── docs/
│   ├── architecture.md    # System design & topology
│   └── glossary.md        # Term definitions
├── src/
│   ├── __init__.py
│   ├── canvas/
│   │   ├── __init__.py
│   │   └── node.py        # Base node types
│   ├── loom/
│   │   ├── __init__.py
│   │   └── runtime.py     # æ loom runtime engine
│   ├── molt/
│   │   ├── __init__.py
│   │   └── evaluator.py   # Molt trigger & reweave logic
│   └── workflows/
│       ├── __init__.py
│       └── morning_ritual.py  # 8 AM ritual: Gmail → Summarizer → Planner → Notion
├── tests/
│   ├── __init__.py
│   └── test_node.py
└── pyproject.toml
```

---

## First Workflow: The 8 AM Ritual

The proving ground. Every morning at 8 AM:

1. **Cron** triggers the swarm
2. **Gmail node** fetches unread emails
3. **Summarizer node** distills them
4. **Planner node** extracts action items
5. **Notion logger node** records the plan
6. **Verifier node** checks for drift from yesterday's plan

This is Midio's "hello world" — except it actually does something useful.

---

## Philosophy

> Teach through canvas, not documentation.  
> Show the swarm, don't describe it.  
> Let the topology speak.

Midio exists because the future of AI isn't a single model — it's a **swarm of specialists** working in concert. And swarms need a loom, not a pipeline.

---

## Status

🟡 **Scaffolding** — Structure in place, building out node primitives and the æ loom runtime.

---

## License

MIT — see [LICENSE](./LICENSE)
