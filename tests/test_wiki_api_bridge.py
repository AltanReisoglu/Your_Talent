import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _seed_vault(vault_root: Path) -> None:
    page_dir = vault_root / "wiki" / "concepts"
    page_dir.mkdir(parents=True)
    (page_dir / "discounted-cash-flow-dcf.md").write_text(
        """---
title: Discounted Cash Flow (DCF)
tags:
  - "finance"
domain: financial-services
last_updated: 2026-05-20
review_status: active
sources:
  - "Seed test source"
related:
  - "WACC"
---

# Discounted Cash Flow (DCF)

DCF estimates intrinsic value by discounting future cash flows.
""",
        encoding="utf-8",
    )


def _run_bridge(payload: dict, vault_root: Path) -> dict:
    env = {
        **os.environ,
        "FINWIKI_VAULT_ROOT": str(vault_root),
        "PYTHONUNBUFFERED": "1",
    }
    result = subprocess.run(
        [sys.executable, "scripts/wiki_api.py"],
        cwd=REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_search_and_page_operations_return_mobile_safe_payloads(tmp_path: Path) -> None:
    vault_root = tmp_path / "vault"
    _seed_vault(vault_root)

    search = _run_bridge({"operation": "search", "query": "DCF", "limit": 5}, vault_root)

    assert search["results"]
    assert search["results"][0]["path"] == "concepts/discounted-cash-flow-dcf.md"
    assert search["results"][0]["title"] == "Discounted Cash Flow (DCF)"

    page = _run_bridge(
        {"operation": "page", "path": "concepts/discounted-cash-flow-dcf.md"},
        vault_root,
    )

    assert page["page"]["title"] == "Discounted Cash Flow (DCF)"
    assert "discounting future cash flows" in page["page"]["content"]
    assert page["page"]["sources"] == ["Seed test source"]


def test_ingest_and_account_delete_write_state_not_wiki_pages(tmp_path: Path) -> None:
    vault_root = tmp_path / "vault"
    _seed_vault(vault_root)

    ingest = _run_bridge(
        {
            "operation": "ingest_submission",
            "user_id": "test-user",
            "type": "url",
            "content": "https://example.com/report",
            "notes": "source candidate",
        },
        vault_root,
    )
    deletion = _run_bridge(
        {
            "operation": "account_delete",
            "user_id": "test-user",
            "confirmation": True,
        },
        vault_root,
    )

    assert ingest["status"] == "queued"
    assert deletion["status"] == "requested"
    assert (vault_root / "state" / "mobile-ingest-submissions.jsonl").exists()
    assert (vault_root / "state" / "account-deletion-requests.jsonl").exists()
    assert not (vault_root / "wiki" / "mobile-ingest-submissions.jsonl").exists()
