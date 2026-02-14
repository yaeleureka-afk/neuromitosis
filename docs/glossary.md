# 💿 Neuromitosis Glossary

| Term | Definition |
|------|-----------|
| **Neuromitosis** | A learning network for AI agent skills. Named for cellular division — skills divide and propagate. |
| **💿 Disc** | A portable, self-describing container for agent skills. The `.disc` format. Like a package.json for workflows. |
| **Track** | A single skill on a disc — one node with its execution context. The atomic unit. |
| **Canvas** | The visual composition layer. Drag, connect, and compose nodes. |
| **Node** | The atomic unit of agency on the canvas. Has typed I/O, health, memory. |
| **Yarn** | A typed connection between nodes (data, signal, state, guard). |
| **Loom** | The æ runtime execution engine. Weaves nodes together in topological order. |
| **Weave** | Execute a loom — run the swarm in dependency order. |
| **Molt** | Deliberate system evolution. When drift exceeds tolerance, the system sheds its skin. |
| **Drift** | Measure of how far a node has deviated from expected behavior. |
| **Codec** | The encoding/decoding system. Burns looms into discs, rips discs into looms. |
| **Burn** | Encode a loom into a disc (serialize). |
| **Rip** | Decode a disc back into a runnable loom (deserialize). |
| **Library** | Local collection of .disc files (~/.neuromitosis/library/). Your CD shelf. |
| **llm.store** | The marketplace for agent skills. Browse, publish, install 💿 discs. |
| **Trustclaw** | The agent brain — LLM orchestration, memory, skill routing. |
| **Auth Manifest** | A disc's declaration of what connections it needs (not the keys themselves). |
| **Checksum** | SHA-256 hash for disc integrity verification. |
| **MCP** | Model Context Protocol — the transport layer for skill discovery and execution. |
| **Composio** | Execution primitive providing 500+ tool integrations with managed auth. |
| **nm** | CLI shorthand for neuromitosis commands. `nm install`, `nm burn`, `nm publish`. |
