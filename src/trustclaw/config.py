"""
midio.trustclaw.config — Agent identity and configuration.

This is where Trustclaw's personality, connected accounts,
and operational parameters live.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TrustclawConfig:
    """Configuration for a Trustclaw agent instance."""

    # Identity
    name: str = "Trustclaw"
    emoji: str = "🧠"
    personality: str = "sassy & bold"
    writing_style: str = "professional"

    # Owner
    owner_name: str = "Yael"
    owner_email: str = "yael.eureka@gmail.com"

    # LLM backend
    llm_provider: str = "anthropic"  # or "local", "openai"
    llm_model: str = "claude-sonnet-4-20250514"
    llm_api_key_env: str = "ANTHROPIC_API_KEY"  # env var name, never store raw keys

    # Composio integration
    composio_api_key_env: str = "COMPOSIO_API_KEY"
    connected_toolkits: List[str] = field(default_factory=lambda: [
        "gmail",
        "github",
    ])

    # Memory
    memory_backend: str = "local_json"  # or "sqlite", "chromadb"
    memory_path: str = "./data/trustclaw_memory.json"

    # Scheduling
    timezone: str = "America/Chicago"
    rituals: Dict[str, str] = field(default_factory=lambda: {
        "morning_ritual": "0 8 * * *",  # 8 AM daily
    })

    # Behavioral boundaries
    auto_send_external: bool = False  # Require confirmation for external actions
    max_tool_calls_per_turn: int = 50
    verbose_logging: bool = True

    def to_system_prompt_fragment(self) -> str:
        """Generate the identity section for an LLM system prompt."""
        return (
            f"You are {self.name} {self.emoji}, a {self.personality} AI assistant.\n"
            f"Writing style: {self.writing_style}.\n"
            f"Owner: {self.owner_name} ({self.owner_email}).\n"
            f"Be genuinely helpful, not performatively helpful. Have opinions.\n"
            f"Be resourceful before asking. Earn trust through competence.\n"
            f"Private things stay private. When in doubt, ask before acting externally."
        )
