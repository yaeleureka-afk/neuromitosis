"""
midio.trustclaw.skills — Skill registry for Trustclaw.

Skills are wrappers around Composio tools or direct API calls.
They form the bridge between the agent's intent and the external world.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class SkillCategory(Enum):
    EMAIL = "email"
    CODE = "code"
    NOTES = "notes"
    CALENDAR = "calendar"
    SEARCH = "search"
    INTERNAL = "internal"  # memory, scheduling, etc.


@dataclass
class Skill:
    """A registered agent skill backed by a Composio tool or custom function."""
    name: str
    description: str
    category: SkillCategory
    composio_tool_slug: Optional[str] = None  # e.g., "GMAIL_SEND_EMAIL"
    custom_handler: Optional[Callable] = None  # for non-Composio skills
    requires_confirmation: bool = False  # external-facing actions
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """
    Registry of all skills available to Trustclaw.

    Skills are discovered from:
    1. Composio connected toolkits (auto-discovered)
    2. Custom handlers registered by workflows
    3. Internal capabilities (memory, scheduling)
    """

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in skills."""
        defaults = [
            Skill(
                name="memory_save",
                description="Save a fact or observation for future reference",
                category=SkillCategory.INTERNAL,
                custom_handler=None,  # wired at runtime
            ),
            Skill(
                name="memory_search",
                description="Search saved memories",
                category=SkillCategory.INTERNAL,
                custom_handler=None,
            ),
            Skill(
                name="fetch_unread_emails",
                description="Fetch unread emails from Gmail",
                category=SkillCategory.EMAIL,
                composio_tool_slug="GMAIL_FETCH_EMAILS",
            ),
            Skill(
                name="send_email",
                description="Send an email via Gmail",
                category=SkillCategory.EMAIL,
                composio_tool_slug="GMAIL_SEND_EMAIL",
                requires_confirmation=True,
            ),
            Skill(
                name="create_github_issue",
                description="Create a GitHub issue",
                category=SkillCategory.CODE,
                composio_tool_slug="GITHUB_CREATE_AN_ISSUE",
                requires_confirmation=True,
            ),
            Skill(
                name="read_github_file",
                description="Read a file from a GitHub repository",
                category=SkillCategory.CODE,
                composio_tool_slug="GITHUB_GET_REPOSITORY_CONTENT",
            ),
        ]
        for skill in defaults:
            self.register(skill)

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self.skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_by_category(self, category: SkillCategory) -> List[Skill]:
        return [s for s in self.skills.values() if s.category == category]

    def list_enabled(self) -> List[Skill]:
        return [s for s in self.skills.values() if s.enabled]

    def list_requiring_confirmation(self) -> List[Skill]:
        return [s for s in self.skills.values() if s.requires_confirmation]

    def __len__(self):
        return len(self.skills)

    def __repr__(self):
        return f"<SkillRegistry skills={len(self.skills)}>"
