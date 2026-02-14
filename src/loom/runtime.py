"""
midio.loom.runtime — The æ loom: Midio's runtime execution engine.
"""

from typing import Any, Dict, List, Optional
from collections import deque
from ..canvas.node import Node, NodeType, YarnType


class Loom:
    """
    The æ loom weaves nodes together and executes the swarm.

    Execution follows topological order with support for:
    - Parallel independent branches
    - Guard node interrupts
    - Molt signals
    """

    def __init__(self, name: str = "unnamed_loom"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self._molt_requested = False

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def remove_node(self, node_id: str) -> None:
        self.nodes.pop(node_id, None)
        # Clean up any yarn pointing to/from this node
        for n in self.nodes.values():
            n.connections = [
                y for y in n.connections
                if y.target_node != node_id
            ]

    def get_topology(self) -> Dict[str, List[str]]:
        """Return adjacency list of the current swarm topology."""
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for node in self.nodes.values():
            for yarn in node.connections:
                if yarn.target_node in adj:
                    adj[node.id].append(yarn.target_node)
        return adj

    def _topological_sort(self) -> List[str]:
        """Kahn's algorithm for execution order."""
        adj = self.get_topology()
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for nid, targets in adj.items():
            for t in targets:
                in_degree[t] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            nid = queue.popleft()
            order.append(nid)
            for t in adj.get(nid, []):
                in_degree[t] -= 1
                if in_degree[t] == 0:
                    queue.append(t)

        if len(order) != len(self.nodes):
            raise RuntimeError("Cycle detected in swarm topology. Consider a molt.")

        return order

    def weave(self, initial_inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the swarm in topological order.
        Returns a dict of node_id → output for each node.
        """
        order = self._topological_sort()
        results: Dict[str, Any] = {}
        initial_inputs = initial_inputs or {}

        for nid in order:
            if self._molt_requested:
                self.execution_log.append({"event": "molt_interrupt", "at_node": nid})
                break

            node = self.nodes[nid]

            # Gather inputs: from initial_inputs or from upstream nodes
            if nid in initial_inputs:
                node_input = initial_inputs[nid]
            else:
                # Collect outputs from all upstream nodes connected to this one
                upstream_outputs = []
                for other in self.nodes.values():
                    for yarn in other.connections:
                        if yarn.target_node == nid and other.id in results:
                            upstream_outputs.append(results[other.id])
                node_input = upstream_outputs[0] if len(upstream_outputs) == 1 else upstream_outputs

            # Execute
            try:
                output = node.execute(node_input)
                results[nid] = output
                self.execution_log.append({
                    "event": "executed",
                    "node": node.name,
                    "node_id": nid,
                    "status": "ok",
                })
            except Exception as e:
                node.health["errors"] += 1
                results[nid] = None
                self.execution_log.append({
                    "event": "error",
                    "node": node.name,
                    "node_id": nid,
                    "error": str(e),
                })

                # Guard nodes can trigger molt on error
                if node.node_type == NodeType.GUARD:
                    self._molt_requested = True

        return results

    def request_molt(self) -> None:
        """Signal that the swarm needs to molt."""
        self._molt_requested = True

    def reset_molt(self) -> None:
        self._molt_requested = False

    def __repr__(self):
        return f"<Loom:{self.name} nodes={len(self.nodes)}>"
