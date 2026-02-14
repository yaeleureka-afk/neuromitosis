"""
midio.molt.evaluator — Molt trigger and reweave logic.

Molt is Midio's mechanism for deliberate system evolution.
When drift exceeds tolerance, the evaluator can:
1. Detect which nodes/connections are degraded
2. Propose a reweave (new topology)
3. Execute the molt (swap old topology for new)
"""

from typing import Any, Dict, List, Tuple
from ..canvas.node import Node


class MoltEvaluator:
    """Evaluates swarm health and triggers molt when needed."""

    def __init__(self, drift_threshold: float = 0.5):
        self.drift_threshold = drift_threshold
        self.molt_history: List[Dict[str, Any]] = []

    def assess_drift(self, nodes: Dict[str, Node]) -> Dict[str, float]:
        """Return drift scores for each node."""
        return {
            nid: node.health.get("drift_score", 0.0)
            for nid, node in nodes.items()
        }

    def should_molt(self, nodes: Dict[str, Node]) -> Tuple[bool, List[str]]:
        """
        Determine if the swarm should molt.
        Returns (should_molt, list_of_degraded_node_ids).
        """
        drift_map = self.assess_drift(nodes)
        degraded = [
            nid for nid, score in drift_map.items()
            if score >= self.drift_threshold
        ]
        return len(degraded) > 0, degraded

    def record_molt(self, reason: str, degraded_nodes: List[str], action: str) -> None:
        self.molt_history.append({
            "reason": reason,
            "degraded_nodes": degraded_nodes,
            "action": action,
        })

    def __repr__(self):
        return f"<MoltEvaluator threshold={self.drift_threshold} molts={len(self.molt_history)}>"
