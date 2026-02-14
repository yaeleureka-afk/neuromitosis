"""
midio.trustclaw.agent — The Trustclaw agent core.

This is the brain. It takes user input, decides which skills to use,
maintains memory across sessions, and respects boundaries.

Designed to run locally or in any Python environment with access to:
- An LLM (Claude API, local model, etc.)
- Composio for tool execution
- A memory backend
"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .config import TrustclawConfig
from .memory import MemoryStore
from .skills import SkillRegistry, Skill


class Trustclaw:
    """
    The Trustclaw agent.

    Lifecycle:
        1. Initialize with config
        2. Load memory from disk
        3. Accept user messages
        4. Route to skills (Composio tools or custom handlers)
        5. Persist memory after each interaction

    This class is the orchestrator. The actual LLM calls are delegated
    to whatever backend is configured (Anthropic, OpenAI, local).
    """

    def __init__(self, config: Optional[TrustclawConfig] = None):
        self.config = config or TrustclawConfig()
        self.memory = MemoryStore(path=self.config.memory_path)
        self.skills = SkillRegistry()
        self.conversation_history: List[Dict[str, str]] = []
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Assemble the system prompt from config + memory."""
        identity = self.config.to_system_prompt_fragment()

        # Include recent memories as context
        recent = self.memory.search("important", max_results=10)
        memory_context = ""
        if recent:
            memory_context = "\n\nRelevant memories:\n" + "\n".join(
                f"- {m.content}" for m in recent
            )

        # Include available skills
        skill_list = "\n".join(
            f"- {s.name}: {s.description}"
            + (" ⚠️ requires confirmation" if s.requires_confirmation else "")
            for s in self.skills.list_enabled()
        )

        return (
            f"{identity}\n\n"
            f"Available skills:\n{skill_list}\n"
            f"{memory_context}"
        )

    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return a response.

        This is the main loop stub. In a full implementation:
        1. Send conversation + system prompt to LLM
        2. Parse LLM response for tool calls
        3. Execute tools via Composio or custom handlers
        4. Return final response to user

        Currently returns a placeholder — wire your LLM here.
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # STUB: Replace with actual LLM call
        # Example with Anthropic:
        #   from anthropic import Anthropic
        #   client = Anthropic(api_key=os.environ[self.config.llm_api_key_env])
        #   response = client.messages.create(
        #       model=self.config.llm_model,
        #       system=self._system_prompt,
        #       messages=self.conversation_history,
        #   )
        response_text = f"[Trustclaw] Received: {user_message[:100]}... (LLM not wired yet)"

        self.conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return response_text

    def execute_skill(self, skill_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a registered skill.

        For Composio-backed skills, this will call the Composio API.
        For custom skills, it calls the registered handler.
        """
        skill = self.skills.get(skill_name)
        if skill is None:
            return {"error": f"Unknown skill: {skill_name}"}

        if not skill.enabled:
            return {"error": f"Skill '{skill_name}' is disabled"}

        if skill.requires_confirmation and not self.config.auto_send_external:
            return {
                "status": "confirmation_required",
                "skill": skill_name,
                "arguments": arguments,
                "message": f"Action '{skill_name}' requires your confirmation before executing.",
            }

        # Composio-backed skill
        if skill.composio_tool_slug:
            return self._execute_composio_tool(skill.composio_tool_slug, arguments)

        # Custom handler
        if skill.custom_handler:
            return skill.custom_handler(**arguments)

        return {"error": f"Skill '{skill_name}' has no handler configured"}

    def _execute_composio_tool(self, tool_slug: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a Composio tool. Stub — wire Composio SDK here.

        Example:
            from composio import ComposioToolSet
            toolset = ComposioToolSet(api_key=os.environ[self.config.composio_api_key_env])
            result = toolset.execute_tool(tool_slug, arguments)
            return result
        """
        return {
            "status": "stub",
            "tool": tool_slug,
            "arguments": arguments,
            "message": "Composio SDK not wired yet. See comments in agent.py.",
        }

    def remember(self, content: str, tags: Optional[List[str]] = None) -> None:
        """Save something to persistent memory."""
        self.memory.save(content, tags=tags)

    def recall(self, query: str, max_results: int = 5) -> List[str]:
        """Search memory and return matching content."""
        results = self.memory.search(query, max_results=max_results)
        return [m.content for m in results]

    def get_status(self) -> Dict[str, Any]:
        """Return current agent status."""
        return {
            "name": self.config.name,
            "personality": self.config.personality,
            "memories": len(self.memory),
            "skills": len(self.skills),
            "skills_requiring_confirmation": len(self.skills.list_requiring_confirmation()),
            "conversation_turns": len(self.conversation_history),
            "llm_provider": self.config.llm_provider,
            "llm_model": self.config.llm_model,
            "connected_toolkits": self.config.connected_toolkits,
        }

    def __repr__(self):
        return (
            f"<Trustclaw 🧠 memories={len(self.memory)} "
            f"skills={len(self.skills)} "
            f"turns={len(self.conversation_history)}>"
        )
