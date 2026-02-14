"""
midio.workflows.morning_ritual — The 8 AM Ritual

The proving ground for the æ loom:
  Cron → Gmail → Summarizer → Planner → Notion Logger → Verifier

This module defines the swarm topology for the morning ritual.
Actual integrations (Gmail API, Notion API, LLM calls) are stubbed
and meant to be wired via Composio or direct API clients.
"""

from ..canvas.node import Node, NodeType, YarnType
from ..loom.runtime import Loom


# ── Node Definitions ──

class GmailFetcherNode(Node):
    """Source node: fetches unread emails."""
    def __init__(self):
        super().__init__(name="gmail_fetcher", node_type=NodeType.SOURCE)

    def execute(self, input_data=None):
        super().execute(input_data)
        # STUB: Replace with actual Gmail fetch via Composio
        return {"emails": [], "count": 0}


class SummarizerNode(Node):
    """Transform node: summarizes email batch."""
    def __init__(self):
        super().__init__(name="summarizer", node_type=NodeType.TRANSFORM)

    def execute(self, input_data):
        super().execute(input_data)
        emails = input_data.get("emails", []) if isinstance(input_data, dict) else []
        # STUB: Replace with LLM summarization
        return {"summary": f"Summarized {len(emails)} emails", "emails": emails}


class PlannerNode(Node):
    """Transform node: extracts action items from summary."""
    def __init__(self):
        super().__init__(name="planner", node_type=NodeType.TRANSFORM)

    def execute(self, input_data):
        super().execute(input_data)
        # STUB: Replace with LLM planning
        return {"action_items": [], "plan_text": "No actions extracted yet."}


class NotionLoggerNode(Node):
    """Action node: writes plan to Notion."""
    def __init__(self):
        super().__init__(name="notion_logger", node_type=NodeType.ACTION)

    def execute(self, input_data):
        super().execute(input_data)
        # STUB: Replace with Notion API write via Composio
        return {"logged": True, "destination": "notion"}


class DriftVerifierNode(Node):
    """Guard node: compares today's plan to yesterday's, flags drift."""
    def __init__(self):
        super().__init__(name="drift_verifier", node_type=NodeType.GUARD)

    def execute(self, input_data):
        super().execute(input_data)
        yesterday = self.memory.get("last_plan", None)
        today = input_data.get("plan_text", "") if isinstance(input_data, dict) else ""
        drift = 0.0 if yesterday is None else 0.1  # STUB: real diff logic
        self.health["drift_score"] = drift
        self.memory["last_plan"] = today
        return {"drift_score": drift, "status": "ok" if drift < 0.5 else "molt_recommended"}


def build_morning_ritual() -> Loom:
    """Assemble the 8 AM ritual swarm and return the loom."""
    loom = Loom(name="morning_ritual")

    # Create nodes
    gmail = GmailFetcherNode()
    summarizer = SummarizerNode()
    planner = PlannerNode()
    notion = NotionLoggerNode()
    verifier = DriftVerifierNode()

    # Wire yarn
    gmail.connect(summarizer, YarnType.DATA)
    summarizer.connect(planner, YarnType.DATA)
    planner.connect(notion, YarnType.DATA)
    planner.connect(verifier, YarnType.DATA)

    # Register with loom
    for node in [gmail, summarizer, planner, notion, verifier]:
        loom.add_node(node)

    return loom
