# 💿 Midio Codec — LLM CDs

> *"The CLI reinvented for the MCP era."*

The codec is Midio\'s serialization layer. It captures node graphs, loom topologies, molt invariants, and skill requirements into portable **disc** files that can be shared, versioned, and loaded into any Midio runtime.

## Concepts

| Concept | Analogy | What it does |
|---------|---------|--------------|
| **Track** | Audio track | A single skill — one node with its execution context |
| **Disc** | CD / Album | A collection of tracks bundled with metadata and wiring |
| **Encoder** | CD Burner | Serializes a live Loom into a portable Disc |
| **Decoder** | CD Player | Hydrates a Disc back into a runnable Loom |
| **Library** | CD Shelf | Local collection of saved .disc files |
| **Auth Manifest** | Liner notes | What connections the disc needs (not the keys) |
| **Checksum** | Anti-piracy seal | SHA-256 hash for integrity verification |

## The .disc Format

A `.disc` file is JSON (human-readable, git-friendly):

```json
{
  "format_version": "0.1.0",
  "metadata": {
    "name": "morning_ritual",
    "version": "1.0.0",
    "author": "yael",
    "description": "Daily email triage → summary → plan",
    "license": "MIT",
    "tags": ["email", "productivity", "daily"]
  },
  "tracks": [
    {
      "name": "fetch_emails",
      "node_type": "source",
      "handler": "GMAIL_FETCH_EMAILS",
      "handler_type": "composio",
      "outputs_to": ["summarize"],
      "auth": [{"toolkit": "gmail", "reason": "Fetch unread emails"}]
    },
    {
      "name": "summarize",
      "node_type": "transform",
      "handler": "",
      "handler_type": "builtin",
      "inputs_from": ["fetch_emails"],
      "outputs_to": ["plan"]
    },
    {
      "name": "plan",
      "node_type": "action",
      "handler": "NOTION_CREATE_PAGE",
      "handler_type": "composio",
      "inputs_from": ["summarize"],
      "auth": [{"toolkit": "notion", "reason": "Create daily plan page"}]
    }
  ],
  "auth_manifest": [
    {"toolkit": "gmail", "optional": false},
    {"toolkit": "notion", "optional": false}
  ],
  "topology": {
    "fetch_emails": ["summarize"],
    "summarize": ["plan"],
    "plan": []
  },
  "checksum": "a1b2c3d4e5f6g7h8"
}
```

## Usage

### Burn (encode a Loom → Disc)

```python
from midio.loom.runtime import Loom
from midio.codec import Encoder

loom = build_morning_ritual()
disc = Encoder.burn(
    loom,
    name="morning_ritual",
    author="yael",
    description="Daily email triage → summary → plan",
    skill_map={
        fetch_node.id: {"tool_slug": "GMAIL_FETCH_EMAILS", "handler_type": "composio"},
        plan_node.id: {"tool_slug": "NOTION_CREATE_PAGE", "handler_type": "composio"},
    }
)

# Save to file
with open("morning_ritual.disc", "w") as f:
    f.write(disc.to_json())
```

### Rip (load a Disc → Loom)

```python
from midio.codec import Decoder, Disc

disc = Disc.from_json(open("morning_ritual.disc").read())

# Preview before loading
print(Decoder.preview(disc))

# Check auth requirements
auth_status = Decoder.check_auth(disc)
print(auth_status)  # {"gmail": False, "notion": False}

# Load and run
loom = Decoder.load(disc)
results = loom.weave()
```

### Library (manage your disc collection)

```python
from midio.codec import Library

lib = Library()  # ~/.midio/library/

# Save
lib.save(disc)

# List
print(lib.list())  # ["morning_ritual"]

# Load
loaded = lib.load("morning_ritual")

# Share
lib.export_disc("morning_ritual", "/tmp/morning_ritual.disc")

# Import someone else\'s disc
lib.import_disc("/downloads/cool_workflow.disc")
```

## Integration with Midio

The codec connects to every layer of the system:

```
Canvas (nodes) ←→ Encoder ←→ Disc ←→ Decoder ←→ Loom (runtime)
                                ↕
                            Library (storage)
                                ↕
                         MCP (discovery)
```

- **Canvas**: Nodes are the raw material. The encoder reads them.
- **Loom**: The runtime. The decoder produces runnable Looms.
- **Molt**: Guard invariants are preserved in tracks.
- **Trustclaw**: Skills map to track handlers.
- **MCP**: Discs can be discovered and loaded via MCP tool listing.

## Future

- **MessagePack encoding**: Compact binary format for distribution
- **Disc signing**: Cryptographic signatures for trust
- **Registry**: `midio install morning_ritual` from a central index
- **Versioned migration**: Upgrade discs between format versions
- **Dependency resolution**: Discs that require other discs
