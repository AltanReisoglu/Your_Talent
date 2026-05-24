from pathlib import Path


def test_update_day_state_creates_and_supersedes_entries(wiki_manager_module):
    first = wiki_manager_module.update_day_state(
        "Work on article A first.",
        next_actions=["Collect source A"],
    )
    second = wiki_manager_module.update_day_state(
        "Switch to article B.",
        next_actions=["Collect source B"],
    )

    path = Path(wiki_manager_module._DAY_STATE_PATH)
    content = path.read_text(encoding="utf-8")

    assert "Day-state updated" in first
    assert "Day-state updated" in second
    assert "Switch to article B." in content
    assert "Work on article A first." in content
    assert "## Superseded Entries" in content


def test_day_state_is_memory_config_operational_context():
    from agents.memory_config import FINWIKI_MEMORY_FILES

    assert "/finwiki-vault/state/day-state.md" in FINWIKI_MEMORY_FILES
