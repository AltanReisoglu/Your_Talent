import importlib
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def wiki_manager_module(tmp_path, monkeypatch):
    vault = tmp_path / "finwiki-vault"
    wiki = vault / "wiki"
    for directory in [
        "concepts",
        "companies",
        "instruments",
        "markets",
        "macro",
        "regulation",
        "risk",
        "models",
        "sources",
        "strategies",
        "maintenance",
    ]:
        (wiki / directory).mkdir(parents=True, exist_ok=True)
    _write(
        wiki / "index.md",
        """---
title: FinWiki Index
last_updated: 2026-05-24
total_pages: 0
---

# FinWiki Index

## Concepts

## Instruments

## Markets

## Companies

## Macroeconomics

## Regulation

## Risk

## Models

## Sources

## Strategies
""",
    )
    _write(wiki / "log.md", "---\ntitle: Log\n---\n\n# Log\n")
    _write(wiki / ".manifest.json", json.dumps({"sources": {}}, indent=2) + "\n")
    monkeypatch.setenv("FINWIKI_VAULT_ROOT", str(vault))

    import tools.serverless.wiki_manager as wiki_manager

    return importlib.reload(wiki_manager)
