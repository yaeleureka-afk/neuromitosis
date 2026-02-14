"""
midio.bridge — JSON-RPC bridge between Electron and Python.

The MCP server in Electron calls this process via stdin/stdout JSON-RPC.
This module translates MCP tool calls into Midio Python operations.

Run with: python -m midio.bridge
"""

import json
import sys
from typing import Any, Dict

from ..trustclaw.agent import Trustclaw
from ..trustclaw.config import TrustclawConfig
from ..loom.runtime import Loom
from ..canvas.node import Node, NodeType
from ..molt.evaluator import MoltEvaluator
from ..workflows.morning_ritual import build_morning_ritual


# Initialize core systems
config = TrustclawConfig()
agent = Trustclaw(config)
looms: Dict[str, Loom] = {
    "morning_ritual": build_morning_ritual(),
}
molt_evaluator = MoltEvaluator()


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Route a JSON-RPC request to the appropriate handler."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", None)

    try:
        result = dispatch(method, params)
        return {"jsonrpc": "2.0", "result": result, "id": req_id}
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": req_id,
        }


def dispatch(method: str, params: Dict[str, Any]) -> Any:
    """Dispatch MCP tool name to Python handler."""
    handlers = {
        # Loom
        "midio/loom.weave": handle_loom_weave,
        "midio/loom.getTopology": handle_loom_topology,

        # Canvas
        "midio/canvas.addNode": handle_canvas_add_node,
        "midio/canvas.connect": handle_canvas_connect,
        "midio/canvas.removeNode": handle_canvas_remove_node,

        # Molt
        "midio/molt.evaluate": handle_molt_evaluate,
        "midio/molt.execute": handle_molt_execute,

        # Trustclaw
        "midio/trustclaw.chat": handle_trustclaw_chat,
        "midio/trustclaw.status": handle_trustclaw_status,

        # Memory
        "midio/memory.save": handle_memory_save,
        "midio/memory.search": handle_memory_search,

        # Skills
        "midio/skill.execute": handle_skill_execute,
        "midio/skill.list": handle_skill_list,
    }

    handler = handlers.get(method)
    if handler is None:
        raise ValueError(f"Unknown method: {method}")
    return handler(params)


# ── Handlers ──

def handle_loom_weave(params: Dict) -> Dict:
    name = params["loom_name"]
    loom = looms.get(name)
    if not loom:
        raise ValueError(f"Unknown loom: {name}")
    initial = params.get("initial_inputs", {})
    results = loom.weave(initial_inputs=initial if initial else None)
    return {
        "loom": name,
        "nodes_executed": len(results),
        "results": {nid: str(v)[:200] for nid, v in results.items()},
        "log": loom.execution_log[-5:],
    }


def handle_loom_topology(params: Dict) -> Dict:
    name = params["loom_name"]
    loom = looms.get(name)
    if not loom:
        raise ValueError(f"Unknown loom: {name}")
    topo = loom.get_topology()
    nodes_info = {
        nid: {"name": n.name, "type": n.node_type.value}
        for nid, n in loom.nodes.items()
    }
    return {"loom": name, "topology": topo, "nodes": nodes_info}


def handle_canvas_add_node(params: Dict) -> Dict:
    node = Node(
        name=params["name"],
        node_type=NodeType(params["node_type"]),
        position=tuple(params.get("position", {}).get("x", 0)),
    )
    return {"node_id": node.id, "name": node.name, "type": node.node_type.value}


def handle_canvas_connect(params: Dict) -> Dict:
    return {"status": "stub", "message": "Canvas connect requires loom context"}


def handle_canvas_remove_node(params: Dict) -> Dict:
    return {"status": "stub", "message": "Canvas remove requires loom context"}


def handle_molt_evaluate(params: Dict) -> Dict:
    name = params["loom_name"]
    loom = looms.get(name)
    if not loom:
        raise ValueError(f"Unknown loom: {name}")
    if params.get("drift_threshold"):
        molt_evaluator.drift_threshold = params["drift_threshold"]
    should, degraded = molt_evaluator.should_molt(loom.nodes)
    return {"should_molt": should, "degraded_nodes": degraded}


def handle_molt_execute(params: Dict) -> Dict:
    molt_evaluator.record_molt(params["reason"], [], "manual_trigger")
    return {"status": "molt_recorded", "reason": params["reason"]}


def handle_trustclaw_chat(params: Dict) -> Dict:
    response = agent.process_message(params["message"])
    return {"response": response}


def handle_trustclaw_status(params: Dict) -> Dict:
    return agent.get_status()


def handle_memory_save(params: Dict) -> Dict:
    mem = agent.memory.save(params["content"], tags=params.get("tags"))
    return {"id": mem.id, "content": mem.content}


def handle_memory_search(params: Dict) -> Dict:
    results = agent.memory.search(params["query"], max_results=params.get("max_results", 5))
    return {"results": [{"id": m.id, "content": m.content} for m in results]}


def handle_skill_execute(params: Dict) -> Dict:
    return agent.execute_skill(params["skill_name"], params.get("arguments", {}))


def handle_skill_list(params: Dict) -> Dict:
    skills = agent.skills.list_enabled()
    return {
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "category": s.category.value,
                "requires_confirmation": s.requires_confirmation,
                "composio_tool": s.composio_tool_slug,
            }
            for s in skills
        ]
    }


# ── Main loop ──

def main():
    """Read JSON-RPC requests from stdin, write responses to stdout."""
    print(json.dumps({"status": "ready", "tools": len(dispatch.__code__.co_consts)}), flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            error_resp = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None,
            }
            print(json.dumps(error_resp), flush=True)


if __name__ == "__main__":
    main()
