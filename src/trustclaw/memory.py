"""
midio.trustclaw.memory — Persistent memory for the agent.

Simple local implementation. Can be swapped for ChromaDB,
SQLite with FTS, or any vector store.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Memory:
    """A single memory entry."""
    id: str = ""
    content: str = ""
    created_at: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    """
    Local JSON-backed memory store.

    Supports save, search (keyword-based), and list.
    For production, swap this with a vector DB backend.
    """

    def __init__(self, path: str = "./data/trustclaw_memory.json"):
        self.path = path
        self.memories: List[Memory] = []
        self._load()

    def _load(self) -> None:
        """Load memories from disk."""
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                raw = json.load(f)
            self.memories = [
                Memory(**m) for m in raw
            ]

    def _save(self) -> None:
        """Persist memories to disk."""
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(
                [{"id": m.id, "content": m.content, "created_at": m.created_at,
                  "tags": m.tags, "metadata": m.metadata}
                 for m in self.memories],
                f, indent=2,
            )

    def save(self, content: str, tags: Optional[List[str]] = None,
             metadata: Optional[Dict[str, Any]] = None) -> Memory:
        """Save a new memory."""
        import uuid
        mem = Memory(
            id=str(uuid.uuid4()),
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
            tags=tags or [],
            metadata=metadata or {},
        )
        self.memories.append(mem)
        self._save()
        return mem

    def search(self, query: str, max_results: int = 5) -> List[Memory]:
        """
        Simple keyword search across memory contents.
        For production, use embedding similarity.
        """
        query_lower = query.lower()
        scored = []
        for mem in self.memories:
            content_lower = mem.content.lower()
            # Simple relevance: count query term occurrences
            score = sum(
                1 for word in query_lower.split()
                if word in content_lower
            )
            if score > 0:
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:max_results]]

    def list_all(self) -> List[Memory]:
        return list(self.memories)

    def clear(self) -> None:
        self.memories = []
        self._save()

    def __len__(self):
        return len(self.memories)

    def __repr__(self):
        return f"<MemoryStore entries={len(self.memories)} path='{self.path}'>"
