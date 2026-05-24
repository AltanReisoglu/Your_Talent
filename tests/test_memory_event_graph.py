from pathlib import Path


def test_emit_memory_event_appends_jsonl_and_reports_corrupt_lines(wiki_manager_module):
    event_id = wiki_manager_module.emit_memory_event(
        "authority.decision",
        "test-query",
        {"selected": "policy", "secret": "Bearer " + "x" * 24},
    )
    event_log = Path(wiki_manager_module._MEMORY_EVENT_LOG_PATH)
    with event_log.open("a", encoding="utf-8") as f:
        f.write("{bad json\n")

    report = wiki_manager_module.memory_event_graph_report(limit=20)

    assert event_id.startswith("mem_")
    assert "authority.decision" in event_log.read_text(encoding="utf-8")
    assert "Projection Errors" in report
    assert "line" in report


def test_projection_tracks_page_source_and_stale_relations(wiki_manager_module):
    wiki_manager_module.emit_memory_event(
        "source.registered",
        "source-a",
        {"pages": ["concepts/a.md"]},
    )
    wiki_manager_module.emit_memory_event(
        "page.upserted",
        "concepts/a.md",
        {"sources": ["source-a"], "title": "A"},
    )
    wiki_manager_module.emit_memory_event(
        "page.stale",
        "concepts/a.md",
        {"reason": "old", "replacement": "concepts/b.md"},
    )

    report = wiki_manager_module.memory_event_graph_report(limit=20)

    assert "Nodes:" in report
    assert "Relations:" in report
    assert "concepts/a.md" in report


def test_maintenance_pages_are_generated_inside_vault(wiki_manager_module):
    wiki_manager_module.emit_memory_event("page.stale", "concepts/a.md", {"reason": "old"})
    wiki_manager_module.memory_event_graph_report(limit=20)

    expiry = Path(wiki_manager_module._EXPIRY_REVIEW_PATH)
    governance = Path(wiki_manager_module._MEMORY_GOVERNANCE_PATH)

    assert expiry.exists()
    assert governance.exists()
    assert str(expiry).startswith(str(wiki_manager_module._VAULT_ROOT))
    assert str(governance).startswith(str(wiki_manager_module._VAULT_ROOT))
