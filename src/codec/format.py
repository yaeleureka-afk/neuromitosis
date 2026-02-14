"""
midio.codec.format — The .disc file specification.

A disc is a portable, self-describing container for Midio skill graphs.
It captures everything needed to reconstruct and run a workflow:

  - Tracks: individual skills (node + wiring metadata)
  - Auth manifest: what connections are needed (not the keys)
  - Topology: how tracks wire together
  - Metadata: name, author, version, description

Format: JSON (human-readable, git-friendly, debuggable).
Future: MessagePack for compact binary distribution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import hashlib
from datetime import datetime, timezone


DISC_FORMAT_VERSION = "0.1.0"


class DiscEncoding(Enum):
    """Supported disc serialization formats."""
    JSON = "json"
    # MSGPACK = "msgpack"  # future: compact binary


@dataclass
class AuthRequirement:
    """Declares that a track needs a specific auth connection to run."""
    toolkit: str            # e.g., "gmail", "github", "slack"
    reason: str = ""        # human-readable: "Needs Gmail to fetch emails"
    scopes: List[str] = field(default_factory=list)  # optional OAuth scopes
    optional: bool = False  # can the disc degrade gracefully without this?


@dataclass
class Track:
    """
    A single skill on a disc — one node with its execution context.

    Tracks are the atomic unit. A disc is a playlist of tracks.
    Each track captures:
      - What the node does (type, config, handler)
      - Where it sits in the graph (position, connections)
      - What it needs to run (auth, dependencies)
    """
    name: str
    node_type: str          # "source", "transform", "action", "guard", "control"

    # Execution
    handler: str = ""       # composio tool slug OR custom handler path
    handler_type: str = "composio"  # "composio" | "custom" | "builtin"
    config: Dict[str, Any] = field(default_factory=dict)

    # Graph position
    position: tuple = (0, 0)
    inputs_from: List[str] = field(default_factory=list)   # track names this reads from
    outputs_to: List[str] = field(default_factory=list)     # track names this writes to
    yarn_type: str = "data"  # "data", "signal", "state", "guard"

    # Auth & deps
    auth: List[AuthRequirement] = field(default_factory=list)

    # Molt
    guard_invariant: Optional[str] = None  # if this is a guard, what does it check?
    drift_threshold: float = 0.5

    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize track to dict."""
        d = {
            "name": self.name,
            "node_type": self.node_type,
            "handler": self.handler,
            "handler_type": self.handler_type,
            "config": self.config,
            "position": list(self.position),
            "inputs_from": self.inputs_from,
            "outputs_to": self.outputs_to,
            "yarn_type": self.yarn_type,
            "auth": [
                {
                    "toolkit": a.toolkit,
                    "reason": a.reason,
                    "scopes": a.scopes,
                    "optional": a.optional,
                }
                for a in self.auth
            ],
            "description": self.description,
            "tags": self.tags,
        }
        if self.guard_invariant:
            d["guard_invariant"] = self.guard_invariant
        if self.drift_threshold != 0.5:
            d["drift_threshold"] = self.drift_threshold
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Track":
        """Deserialize track from dict."""
        auth = [
            AuthRequirement(
                toolkit=a["toolkit"],
                reason=a.get("reason", ""),
                scopes=a.get("scopes", []),
                optional=a.get("optional", False),
            )
            for a in d.get("auth", [])
        ]
        return cls(
            name=d["name"],
            node_type=d["node_type"],
            handler=d.get("handler", ""),
            handler_type=d.get("handler_type", "composio"),
            config=d.get("config", {}),
            position=tuple(d.get("position", [0, 0])),
            inputs_from=d.get("inputs_from", []),
            outputs_to=d.get("outputs_to", []),
            yarn_type=d.get("yarn_type", "data"),
            auth=auth,
            guard_invariant=d.get("guard_invariant"),
            drift_threshold=d.get("drift_threshold", 0.5),
            description=d.get("description", ""),
            tags=d.get("tags", []),
        )


@dataclass
class DiscMetadata:
    """Disc-level metadata — the album cover."""
    name: str
    version: str = "0.1.0"
    author: str = ""
    description: str = ""
    license: str = "MIT"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    repository: str = ""


@dataclass
class Disc:
    """
    💿 A portable skill library — the LLM CD.

    Contains:
      - metadata: album cover (name, author, version)
      - tracks: ordered list of skills
      - auth_manifest: all auth requirements (deduplicated)
      - topology: adjacency list derived from track wiring
      - checksum: integrity hash of the content
    """
    metadata: DiscMetadata
    tracks: List[Track] = field(default_factory=list)
    format_version: str = DISC_FORMAT_VERSION

    # — Computed properties —

    @property
    def auth_manifest(self) -> List[AuthRequirement]:
        """Deduplicated auth requirements across all tracks."""
        seen = set()
        manifest = []
        for track in self.tracks:
            for auth in track.auth:
                if auth.toolkit not in seen:
                    seen.add(auth.toolkit)
                    manifest.append(auth)
        return manifest

    @property
    def topology(self) -> Dict[str, List[str]]:
        """Adjacency list: track_name → [downstream_track_names]."""
        adj: Dict[str, List[str]] = {t.name: [] for t in self.tracks}
        for track in self.tracks:
            for target_name in track.outputs_to:
                if target_name in adj:
                    adj[track.name].append(target_name)
        return adj

    @property 
    def checksum(self) -> str:
        """SHA-256 of the disc content (excluding checksum itself)."""
        content = json.dumps(self._to_content_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # — Serialization —

    def _to_content_dict(self) -> Dict[str, Any]:
        """Internal: disc content without checksum (for hashing)."""
        return {
            "format_version": self.format_version,
            "metadata": {
                "name": self.metadata.name,
                "version": self.metadata.version,
                "author": self.metadata.author,
                "description": self.metadata.description,
                "license": self.metadata.license,
                "created_at": self.metadata.created_at,
                "tags": self.metadata.tags,
                "homepage": self.metadata.homepage,
                "repository": self.metadata.repository,
            },
            "tracks": [t.to_dict() for t in self.tracks],
        }

    def to_dict(self) -> Dict[str, Any]:
        """Full disc as dict (with checksum + computed fields)."""
        d = self._to_content_dict()
        d["checksum"] = self.checksum
        d["auth_manifest"] = [
            {"toolkit": a.toolkit, "reason": a.reason, "optional": a.optional}
            for a in self.auth_manifest
        ]
        d["topology"] = self.topology
        return d

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Disc":
        """Deserialize from dict."""
        meta_d = d.get("metadata", {})
        metadata = DiscMetadata(
            name=meta_d.get("name", "unnamed"),
            version=meta_d.get("version", "0.1.0"),
            author=meta_d.get("author", ""),
            description=meta_d.get("description", ""),
            license=meta_d.get("license", "MIT"),
            created_at=meta_d.get("created_at", ""),
            tags=meta_d.get("tags", []),
            homepage=meta_d.get("homepage", ""),
            repository=meta_d.get("repository", ""),
        )
        tracks = [Track.from_dict(t) for t in d.get("tracks", [])]
        return cls(
            metadata=metadata,
            tracks=tracks,
            format_version=d.get("format_version", DISC_FORMAT_VERSION),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Disc":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def validate(self) -> List[str]:
        """
        Validate disc integrity. Returns list of issues (empty = valid).
        """
        issues = []
        if not self.metadata.name:
            issues.append("Disc has no name")
        if not self.tracks:
            issues.append("Disc has no tracks")

        # Check track references
        track_names = {t.name for t in self.tracks}
        for track in self.tracks:
            for ref in track.inputs_from + track.outputs_to:
                if ref not in track_names:
                    issues.append(
                        f"Track '{track.name}' references unknown track '{ref}'"
                    )

        # Check for duplicate names
        if len(track_names) != len(self.tracks):
            issues.append("Disc contains duplicate track names")

        # Verify checksum if loading from external source
        return issues

    def __repr__(self):
        auth_count = len(self.auth_manifest)
        return (
            f"<Disc:'{self.metadata.name}' v{self.metadata.version} "
            f"tracks={len(self.tracks)} auth={auth_count} "
            f"checksum={self.checksum}>"
        )
