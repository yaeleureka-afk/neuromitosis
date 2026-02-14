"""Tests for midio.canvas.node"""

from midio.canvas.node import Node, NodeType, YarnType, Yarn


def test_node_creation():
    n = Node(name="test", node_type=NodeType.TRANSFORM)
    assert n.name == "test"
    assert n.node_type == NodeType.TRANSFORM
    assert n.health["status"] == "idle"


def test_node_execute_passthrough():
    n = Node(name="passthrough")
    result = n.execute({"data": 42})
    assert result == {"data": 42}
    assert n.health["executions"] == 1


def test_node_connect():
    a = Node(name="a")
    b = Node(name="b")
    yarn = a.connect(b, YarnType.DATA)
    assert yarn.source_node == a.id
    assert yarn.target_node == b.id
    assert len(a.connections) == 1


def test_node_repr():
    n = Node(name="demo", node_type=NodeType.GUARD, position=(10, 20))
    assert "demo" in repr(n)
    assert "guard" in repr(n)
