# Architecture

## Overview

Midio is built in layers:

```
┌─────────────────────────────────────┐
│           Canvas (UI/Visual)         │
│  Nodes • Yarn • Topology • Timeline │
├─────────────────────────────────────┤
│           æ Loom (Runtime)           │
│  Execution • State • Observation    │
├─────────────────────────────────────┤
│         Molt Engine (Evolution)      │
│  Drift Detection • Rewind • Reweave │
├─────────────────────────────────────┤
│        Integrations (Skills)         │
│  Gmail • Notion • GitHub • LLMs     │
└─────────────────────────────────────┘
```

## Node Types

| Type | Role | Example |
|------|------|---------|
| **Source** | Ingests external data | Gmail fetcher, webhook listener |
| **Transform** | Processes/reshapes data | Summarizer, classifier |
| **Action** | Produces side effects | Notion writer, email sender |
| **Guard (æ)** | Enforces invariants | Drift detector, schema validator |
| **Control** | Manages flow | Router, retry loop, molt trigger |

## Yarn (Connections)

Yarn is typed:
- `data` — carries payloads between nodes
- `signal` — triggers execution (start, stop, retry)
- `state` — shares persistent context across the swarm
- `guard` — invariant assertions from æ nodes

## Execution Model

The æ loom executes nodes in **topological order** with support for:
- Parallel branches (independent subgraphs run concurrently)
- Feedback loops (guarded by cycle-depth limits)
- Molt interrupts (any node can signal a molt)

## State Management

Each node maintains:
- `input_buffer` — queued incoming data
- `output_buffer` — produced results
- `memory` — persistent state across executions
- `health` — status + drift metrics
