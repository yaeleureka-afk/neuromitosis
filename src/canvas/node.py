"""
midio.canvas.node — Base node types for the Midio canvas.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class NodeType(Enum):
    SOURCE = "source"
    TRANSFORM = "transform"
    ACTION = "action"
    GUARD = "guard"       # æ guard
    CONTROL = "control"


class YarnType(Enum):
    DATA = "data"
    SIGNAL = "signal"
    STATE = "state"
    GUARD = "guard"


@dataclass
class Yarn:
    """A typed connection between two nodes."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_node: str = ""
    target_node: str = ""
    yarn_type: YarnType = YarnType.DATA
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    """Base canvas node — the atomic unit of agency in Midio."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "unnamed"
    node_type: NodeType = NodeType.TRANSFORM
    position: tuple = (0, 0)  # canvas x, y

    # Buffers
    input_buffer: List[Any] = field(default_factory=list)
    output_buffer: List[Any] = field(default_factory=list)

    # Persistent memory across executions
    memory: Dict[str, Any] = field(default_factory=dict)

    # Health & drift
    health: Dict[str, Any] = field(default_factory=lambda: {
        "status": "idle",
        "executions": 0,
        "errors": 0,
        "drift_score": 0.0,
    })

    # Outgoing yarn
    connections: List[Yarn] = field(default_factory=list)

    def execute(self, input_data: Any) -> Any:
        """Override in subclasses. Default is passthrough."""
        self.health["executions"] += 1
        return input_data

    def connect(self, target: "Node", yarn_type: YarnType = YarnType.DATA) -> Yarn:
        """Create a yarn connection to another node."""
        yarn = Yarn(
            source_node=self.id,
            target_node=target.id,
            yarn_type=yarn_type,
        )
        self.connections.append(yarn)
        return yarn

    def __repr__(self):
        return f"<Node:{self.name} ({self.node_type.value}) @ {self.position}>"
