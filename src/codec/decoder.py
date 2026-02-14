"""
midio.codec.decoder — Load a disc into a runnable Loom.

The decoder reads a Disc (from JSON or dict) and hydrates it into
live Node objects wired into a Loom. This is the "rip" / "play" operation.

Usage:
    from midio.codec import Decoder

    disc = Disc.from_json(open("morning_ritual.disc").read())
    loom = Decoder.load(disc)
    results = loom.weave()  # run it
"""

from typing import Any, Dict, List, Optional
from ..canvas.node import Node, NodeType, Yarn, YarnType
from ..loom.runtime import Loom
from .format import Disc, Track


# Reverse mappings
_NODE_TYPE_MAP = {t.value: t for t in NodeType}
_YARN_TYPE_MAP = {t.value: t for t in YarnType}


class DecoderError(Exception):
    """Raised when a disc cannot be decoded."""
    pass


class Decoder:
    """
    Loads a Disc into a runnable Loom.

    The decoder:
    1. Validates the disc
    2. Creates Node objects from Tracks
    3. Wires them together with Yarn
    4. Returns a ready-to-weave Loom
    """

    @staticmethod
    def load(
        disc: Disc,
        loom_name: Optional[str] = None,
        strict: bool = True,
    ) -> Loom:
        """
        Load a Disc into a Loom.

        Args:
            disc: The disc to decode.
            loom_name: Override name for the Loom (defaults to disc name).
            strict: If True, raise on validation errors. If False, warn and continue.

        Returns:
            A wired Loom ready to weave.

        Raises:
            DecoderError: If disc validation fails in strict mode.
        """
        # Validate first
        issues = disc.validate()
        if issues and strict:
            raise DecoderError(
                f"Disc '{disc.metadata.name}' has {len(issues)} issue(s): "
                + "; ".join(issues)
            )

        loom = Loom(name=loom_name or disc.metadata.name)

        # Phase 1: Create all nodes
        name_to_node: Dict[str, Node] = {}
        for track in disc.tracks:
            node = Decoder._track_to_node(track)
            loom.add_node(node)
            name_to_node[track.name] = node

        # Phase 2: Wire connections (yarn)
        for track in disc.tracks:
            source_node = name_to_node.get(track.name)
            if not source_node:
                continue

            yarn_type = _YARN_TYPE_MAP.get(track.yarn_type, YarnType.DATA)
            for target_name in track.outputs_to:
                target_node = name_to_node.get(target_name)
                if target_node:
                    source_node.connect(target_node, yarn_type=yarn_type)
                elif strict:
                    raise DecoderError(
                        f"Track '{track.name}' references missing target '{target_name}'"
                    )

        return loom

    @staticmethod
    def _track_to_node(track: Track) -> Node:
        """Convert a Track back into a Node."""
        node_type = _NODE_TYPE_MAP.get(track.node_type, NodeType.TRANSFORM)
        return Node(
            name=track.name,
            node_type=node_type,
            position=track.position,
        )

    @staticmethod
    def check_auth(disc: Disc) -> Dict[str, bool]:
        """
        Check which auth requirements are satisfied.
        Returns {toolkit: is_connected} for each required toolkit.

        NOTE: In the full runtime, this would query Composio for
        active connections. For now, returns all as unknown (False).
        """
        return {
            auth.toolkit: False
            for auth in disc.auth_manifest
        }

    @staticmethod
    def preview(disc: Disc) -> str:
        """
        Human-readable preview of what loading this disc would do.
        Like reading the back of a CD case.
        """
        lines = [
            f"💿 {disc.metadata.name} v{disc.metadata.version}",
            f"   by {disc.metadata.author or 'unknown'}",
            f"   {disc.metadata.description}" if disc.metadata.description else "",
            f"",
            f"   Tracks ({len(disc.tracks)}):",
        ]
        for i, track in enumerate(disc.tracks, 1):
            handler_info = f" [{track.handler}]" if track.handler else ""
            lines.append(f"   {i:2d}. {track.name} ({track.node_type}){handler_info}")

        auth = disc.auth_manifest
        if auth:
            lines.append(f"")
            lines.append(f"   Auth required ({len(auth)}):")
            for a in auth:
                opt = " (optional)" if a.optional else ""
                lines.append(f"     • {a.toolkit}{opt}")

        topo = disc.topology
        wired = sum(1 for targets in topo.values() if targets)
        lines.append(f"")
        lines.append(f"   Wiring: {wired}/{len(topo)} tracks have downstream connections")
        lines.append(f"   Checksum: {disc.checksum}")

        return "\n".join(lines)
