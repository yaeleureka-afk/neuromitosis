# Midio Desktop — The CLI Reinvented

> The CLI was text commands → tools.
> Midio is visual nodes → MCP tools.
> Same power, spatial interface.

## Architecture

```
┌─────────────────────────────────────────────┐
│            Electron App (Midio)              │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │       React + React Flow (Canvas)      │  │
│  │  Nodes • Yarn • Timeline • Molt        │  │
│  └──────────────┬─────────────────────────┘  │
│                 │ window.midio.*              │
│  ┌──────────────▼─────────────────────────┐  │
│  │         Preload Bridge (IPC)           │  │
│  └──────────────┬─────────────────────────┘  │
│                 │ ipcRenderer.invoke()        │
├─────────────────┼────────────────────────────┤
│                 │ Main Process               │
│  ┌──────────────▼─────────────────────────┐  │
│  │       MCP Server (TypeScript)          │  │
│  │  14 tools • discoverable • typed       │  │
│  └──────────────┬─────────────────────────┘  │
│                 │ JSON-RPC over stdio         │
│  ┌──────────────▼─────────────────────────┐  │
│  │       Python Backend (child proc)      │  │
│  │  midio.bridge → Loom, Trustclaw,       │  │
│  │  Composio SDK, Memory, Molt            │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## MCP Tools Exposed

### Loom (Runtime)
- `midio/loom.weave` — Execute a swarm topology
- `midio/loom.getTopology` — Inspect the node graph

### Canvas (Visual)
- `midio/canvas.addNode` — Create a node
- `midio/canvas.connect` — Wire yarn between nodes
- `midio/canvas.removeNode` — Remove a node

### Molt (Evolution)
- `midio/molt.evaluate` — Check swarm health / drift
- `midio/molt.execute` — Trigger a molt

### Trustclaw (Agent)
- `midio/trustclaw.chat` — Talk to the agent
- `midio/trustclaw.status` — Agent state

### Memory
- `midio/memory.save` — Persist a fact
- `midio/memory.search` — Recall facts

### Skills (Composio)
- `midio/skill.execute` — Run any connected tool
- `midio/skill.list` — Discover available skills

## Why MCP?

MCP (Model Context Protocol) standardizes how AI tools are discovered
and called. By building Midio on MCP:

1. **Every node is a tool** — dragging a node onto the canvas registers
   an MCP tool. The UI and the protocol are the same thing.

2. **Trustclaw speaks the same language** — the agent calls the same
   MCP tools the UI does. No separate API.

3. **External AI can use Midio** — Claude Desktop, Cursor, or any
   MCP-compatible client can call Midio tools directly.

4. **Skills auto-discover** — connect a Composio toolkit and it
   appears as both an MCP tool and a canvas node.

## Development

```bash
# Install Python core
pip install -e .

# Install desktop dependencies
cd packages/desktop
npm install

# Run in dev mode
npm run dev
```

## The Thesis

```
1970s:  $ command --flag | pipe | pipe     (CLI)
2020s:  drag node → connect yarn → weave  (Midio)
```

Same power. Spatial interface. MCP protocol underneath.
