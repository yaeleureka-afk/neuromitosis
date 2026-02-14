# Trustclaw — The Agent Brain

Trustclaw is Midio's resident AI agent. It lives inside the loom, uses Midio's node primitives as its skeleton, and connects to external services via Composio.

## Architecture

```
┌─────────────────────────────────────────┐
│              Trustclaw Agent             │
│                                         │
│  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │ Config  │  │  Memory  │  │ Skills │ │
│  │ (who)   │  │ (recall) │  │ (can)  │ │
│  └────┬────┘  └────┬─────┘  └───┬────┘ │
│       │            │            │       │
│       └────────┬───┴────────────┘       │
│                │                        │
│         ┌──────▼──────┐                 │
│         │   Agent     │                 │
│         │ (orchestr.) │                 │
│         └──────┬──────┘                 │
│                │                        │
├────────────────┼────────────────────────┤
│                │                        │
│    ┌───────────▼───────────┐            │
│    │  LLM Backend          │            │
│    │  (Claude / Local)     │            │
│    └───────────┬───────────┘            │
│                │                        │
│    ┌───────────▼───────────┐            │
│    │  Composio ToolSet     │            │
│    │  Gmail • GitHub •     │            │
│    │  Notion • Calendar    │            │
│    └───────────────────────┘            │
└─────────────────────────────────────────┘
```

## Components

### Config (`config.py`)
Defines Trustclaw's identity, personality, connected accounts, and behavioral boundaries. The config generates the LLM system prompt fragment.

### Memory (`memory.py`)
Persistent memory across sessions. Currently JSON-backed with keyword search. Designed to be swapped for:
- **ChromaDB** — embedding-based similarity search
- **SQLite with FTS5** — full-text search
- **Any vector store** — Pinecone, Weaviate, etc.

### Skills (`skills.py`)
Registry of agent capabilities. Each skill maps to:
- A **Composio tool slug** (e.g., `GMAIL_SEND_EMAIL`) — auto-authenticated via Composio
- A **custom handler** — for internal operations like memory management
- A **confirmation flag** — external-facing actions require user approval

### Agent (`agent.py`)
The orchestrator. Takes user input → builds context (memories + skills) → calls LLM → parses tool calls → executes via Composio → returns response.

## Wiring the LLM

The agent is LLM-agnostic. To wire it:

```python
# Option 1: Anthropic Claude
from anthropic import Anthropic
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Option 2: Local model via Ollama
import requests
response = requests.post("http://localhost:11434/api/generate", json={...})

# Option 3: OpenAI-compatible
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

## Wiring Composio

```python
from composio import ComposioToolSet

toolset = ComposioToolSet(api_key=os.environ["COMPOSIO_API_KEY"])
result = toolset.execute_tool("GMAIL_SEND_EMAIL", {
    "to": "someone@example.com",
    "subject": "Hello from Trustclaw",
    "body": "Sent by an agent that lives in the loom.",
})
```

## Boundaries

Trustclaw follows strict rules:
1. **External actions require confirmation** unless `auto_send_external=True`
2. **Private data stays private** — memory is local, never sent to third parties
3. **The owner's voice is sacred** — Trustclaw never pretends to be Yael
4. **Competence over verbosity** — do the work, skip the filler

## Relationship to Midio

Trustclaw is both a **user of Midio** and a **node within it**:
- As a user: Trustclaw builds and manages swarms on the canvas
- As a node: Trustclaw can be wired into any swarm as a decision-making agent node

This is the self-referential core. The loom weaves itself.
