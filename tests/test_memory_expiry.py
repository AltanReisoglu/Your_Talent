from pathlib import Path


def test_upsert_writes_memory_v2_frontmatter(wiki_manager_module):
    wiki_manager_module.upsert_wiki_page(
        title="Memory Test DCF",
        category="concepts",
        summary="Test DCF page.",
        body="## Notes\nA test page with [[WACC]], [[Cash Flow]], and [[Terminal Value]].",
        sources=["test-source"],
        related=["WACC", "Cash Flow", "Terminal Value"],
    )

    page = Path(wiki_manager_module._WIKI_ROOT) / "concepts" / "memory-test-dcf.md"
    content = page.read_text(encoding="utf-8")

    assert "authority_level: synthesis" in content
    assert "decision_scope: evidence" in content
    assert "valid_from:" in content
    assert "valid_until:" in content
    assert "freshness_policy: event_driven" in content
    assert "supersedes: []" in content
    assert "superseded_by: []" in content


def test_mark_stale_preserves_history_and_updates_review_status(wiki_manager_module):
    wiki_manager_module.upsert_wiki_page(
        title="Stale Test Page",
        category="concepts",
        summary="Test stale page.",
        body="## Notes\nHistorical claim with [[Source]], [[Risk]], and [[Update]].",
        sources=["test-source"],
        related=["Source", "Risk", "Update"],
    )

    result = wiki_manager_module.mark_wiki_memory_stale(
        "concepts/stale-test-page.md",
        "superseded by a newer source",
        replacement="concepts/new-test-page.md",
    )

    page = Path(wiki_manager_module._WIKI_ROOT) / "concepts" / "stale-test-page.md"
    content = page.read_text(encoding="utf-8")

    assert "Marked concepts/stale-test-page.md as superseded" in result
    assert "review_status: superseded" in content
    assert "superseded_by:" in content
    assert "concepts/new-test-page.md" in content
    assert "## Memory Governance Updates" in content
    assert "test-source" in content


def test_freshness_report_demotes_expired_page(wiki_manager_module):
    wiki_manager_module.upsert_wiki_page(
        title="Expired Test Page",
        category="concepts",
        summary="Test expired page.",
        body="## Notes\nExpired claim with [[A]], [[B]], and [[C]].",
        sources=["test-source"],
        related=["A", "B", "C"],
    )
    page = Path(wiki_manager_module._WIKI_ROOT) / "concepts" / "expired-test-page.md"
    content = page.read_text(encoding="utf-8").replace("valid_until: ", "valid_until: 2020-01-01")
    page.write_text(content, encoding="utf-8")

    report = wiki_manager_module.freshness_report("concepts")

    assert "expired-test-page.md" in report
    assert "expired" in report
