"""
midio.codec.encoder — Burn a canvas into a disc.

The encoder reads a live Loom (nodes + yarn + topology) and serializes
it into a portable Disc. This is the "burn" operation.

Usage:
    from midio.loom.runtime import Loom
    from midio.codec import Encoder

    loom = build_my_workflow()
    disc = Encoder.burn(loom, name="my_workflow", author="yael")
    disc.to_json()  # → portable .disc file content
"""

from typing import Any, Dict, List, Optional
from ..canvas.node import Node, NodeType, Yarn, YarnType
from ..loom.runtime import Loom
from .format import (
    Disc,
    DiscMetadata,
    Track,
    AuthRequirement,
)


# Map known Composio tool slugs to their toolkit for auth requirements
SLUG_TO_TOOLKIT = {
    "GMAIL_FETCH_EMAILS": "gmail",
    "GMAIL_SEND_EMAIL": "gmail",
    "GMAIL_LIST_THREADS": "gmail",
    "GITHUB_CREATE_AN_ISSUE": "github",
    "GITHUB_GET_REPOSITORY_CONTENT": "github",
    "GITHUB_COMMIT_MULTIPLE_FILES": "github",
    "SLACK_SEND_MESSAGE": "slack",
    "SLACK_LIST_CHANNELS": "slack",
    "NOTION_CREATE_PAGE": "notion",
    "NOTION_SEARCH": "notion",
    "GOOGLECALENDAR_CREATE_EVENT": "google_calendar",
    "GOOGLECALENDAR_LIST_EVENTS": "google_calendar",
}


class Encoder:
    """
    Burns a Loom into a Disc.

    The encoder walks the node graph, captures each node as a Track,
    preserves the yarn wiring as track references, and extracts auth
    requirements from skill metadata.
    """

    @staticmethod
    def burn(
        loom: Loom,
        name: str,
        author: str = "",
        version: str = "0.1.0",
        description: str = "",
        tags: Optional[List[str]] = None,
        skill_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Disc:
        """
        Burn a Loom into a Disc.

        Args:
            loom: The live Loom instance to encode.
            name: Disc name (the album title).
            author: Who burned this disc.
            version: Semantic version.
            description: What this disc does.
            tags: Categorization tags.
            skill_map: Optional mapping of node_id → skill metadata.
                       Used to attach Composio tool slugs and auth info.
                       Format: {node_id: {"tool_slug": "...", "handler_type": "..."}}

        Returns:
            A Disc ready to serialize.
        """
        tags = tags or []
        skill_map = skill_map or {}

        # Build node_id → node_name map for referencing
        id_to_name: Dict[str, str] = {
            nid: node.name for nid, node in loom.nodes.items()
        }

        # Build reverse adjacency: node_id → [upstream_node_ids]
        reverse_adj: Dict[str, List[str]] = {nid: [] for nid in loom.nodes}
        for node in loom.nodes.values():
            for yarn in node.connections:
                if yarn.target_node in reverse_adj:
                    reverse_adj[yarn.target_node].append(node.id)

        # Encode each node as a Track
        tracks: List[Track] = []
        for nid, node in loom.nodes.items():
            # Resolve skill info
            skill_info = skill_map.get(nid, {})
            tool_slug = skill_info.get("tool_slug", "")
            handler_type = skill_info.get("handler_type", "builtin")

            # Build auth requirements from tool slug
            auth: List[AuthRequirement] = []
            if tool_slug:
                toolkit = SLUG_TO_TOOLKIT.get(tool_slug, "")
                if toolkit:
                    auth.append(AuthRequirement(
                        toolkit=toolkit,
                        reason=f"Required by {node.name}",
                    ))

            # Resolve yarn type for outputs
            yarn_type = "data"
            if node.connections:
                yarn_type = node.connections[0].yarn_type.value

            track = Track(
                name=node.name,
                node_type=node.node_type.value,
                handler=tool_slug,
                handler_type=handler_type,
                config=skill_info.get("config", {}),
                position=node.position,
                inputs_from=[
                    id_to_name[uid] for uid in reverse_adj.get(nid, [])
                    if uid in id_to_name
                ],
                outputs_to=[
                    id_to_name[y.target_node]
                    for y in node.connections
                    if y.target_node in id_to_name
                ],
                yarn_type=yarn_type,
                auth=auth,
                guard_invariant=skill_info.get("guard_invariant"),
                drift_threshold=skill_info.get("drift_threshold", 0.5),
                description=skill_info.get("description", ""),
                tags=skill_info.get("tags", []),
            )
            tracks.append(track)

        metadata = DiscMetadata(
            name=name,
            version=version,
            author=author,
            description=description,
            tags=tags,
        )

        return Disc(metadata=metadata, tracks=tracks)

    @staticmethod
    def burn_track(
        node: Node,
        tool_slug: str = "",
        handler_type: str = "builtin",
        **kwargs,
    ) -> Track:
        """
        Burn a single Node into a standalone Track.
        Useful for encoding individual skills outside a full Loom.
        """
        auth: List[AuthRequirement] = []
        if tool_slug:
            toolkit = SLUG_TO_TOOLKIT.get(tool_slug, "")
            if toolkit:
                auth.append(AuthRequirement(toolkit=toolkit))

        return Track(
            name=node.name,
            node_type=node.node_type.value,
            handler=tool_slug,
            handler_type=handler_type,
            config=kwargs.get("config", {}),
            position=node.position,
            auth=auth,
            description=kwargs.get("description", ""),
            tags=kwargs.get("tags", []),
        )
