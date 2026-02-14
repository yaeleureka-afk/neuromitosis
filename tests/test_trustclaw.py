"""Tests for midio.trustclaw"""

from midio.trustclaw.config import TrustclawConfig
from midio.trustclaw.memory import MemoryStore
from midio.trustclaw.skills import SkillRegistry, SkillCategory
from midio.trustclaw.agent import Trustclaw


def test_config_defaults():
    config = TrustclawConfig()
    assert config.name == "Trustclaw"
    assert config.emoji == "🧠"
    assert config.owner_name == "Yael"
    assert "gmail" in config.connected_toolkits


def test_config_system_prompt():
    config = TrustclawConfig()
    prompt = config.to_system_prompt_fragment()
    assert "Trustclaw" in prompt
    assert "sassy" in prompt
    assert "Yael" in prompt


def test_memory_store(tmp_path):
    store = MemoryStore(path=str(tmp_path / "test_memory.json"))
    assert len(store) == 0

    store.save("Yael prefers visual learning")
    store.save("The morning ritual runs at 8 AM")
    assert len(store) == 2

    results = store.search("morning")
    assert len(results) == 1
    assert "morning" in results[0].content.lower()


def test_memory_persistence(tmp_path):
    path = str(tmp_path / "persist_test.json")
    store1 = MemoryStore(path=path)
    store1.save("important fact")

    # Reload from disk
    store2 = MemoryStore(path=path)
    assert len(store2) == 1
    assert store2.memories[0].content == "important fact"


def test_skill_registry():
    registry = SkillRegistry()
    assert len(registry) > 0  # defaults registered

    # Check built-in skills exist
    assert registry.get("memory_save") is not None
    assert registry.get("fetch_unread_emails") is not None

    # Check category filtering
    email_skills = registry.list_by_category(SkillCategory.EMAIL)
    assert len(email_skills) >= 1

    # Check confirmation filtering
    confirm_skills = registry.list_requiring_confirmation()
    assert len(confirm_skills) >= 1


def test_agent_creation():
    config = TrustclawConfig(memory_path="/tmp/test_tc_memory.json")
    agent = Trustclaw(config=config)
    assert agent.config.name == "Trustclaw"
    assert len(agent.skills) > 0


def test_agent_status():
    config = TrustclawConfig(memory_path="/tmp/test_tc_status.json")
    agent = Trustclaw(config=config)
    status = agent.get_status()
    assert status["name"] == "Trustclaw"
    assert status["memories"] >= 0
    assert status["skills"] > 0


def test_agent_remember_recall():
    config = TrustclawConfig(memory_path="/tmp/test_tc_recall.json")
    agent = Trustclaw(config=config)
    agent.memory.clear()

    agent.remember("The domain is æl.net")
    results = agent.recall("domain")
    assert len(results) == 1
    assert "æl.net" in results[0]


def test_agent_execute_skill_confirmation():
    config = TrustclawConfig(memory_path="/tmp/test_tc_confirm.json")
    agent = Trustclaw(config=config)
    result = agent.execute_skill("send_email", {"to": "test@example.com"})
    assert result["status"] == "confirmation_required"
