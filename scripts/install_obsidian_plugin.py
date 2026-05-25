"""Install the local FinWiki Obsidian plugin into the FinWiki vault."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "finwiki-agent"
SOURCE_DIR = REPO_ROOT / "obsidian-plugin" / PLUGIN_ID
VAULT_DIR = REPO_ROOT / "finwiki-vault"
TARGET_DIR = VAULT_DIR / ".obsidian" / "plugins" / PLUGIN_ID
COMMUNITY_PLUGINS = VAULT_DIR / ".obsidian" / "community-plugins.json"
RUNTIME_FILES = ("manifest.json", "main.js", "styles.css")


def install_plugin() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"Plugin source not found: {SOURCE_DIR}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for filename in RUNTIME_FILES:
        source = SOURCE_DIR / filename
        if not source.exists():
            raise SystemExit(f"Required plugin file missing: {source}")
        shutil.copy2(source, TARGET_DIR / filename)

    enable_plugin()
    print(f"Installed {PLUGIN_ID} into {TARGET_DIR}")


def enable_plugin() -> None:
    COMMUNITY_PLUGINS.parent.mkdir(parents=True, exist_ok=True)
    if COMMUNITY_PLUGINS.exists():
        try:
            enabled = json.loads(COMMUNITY_PLUGINS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            enabled = []
    else:
        enabled = []

    if not isinstance(enabled, list):
        enabled = []
    if PLUGIN_ID not in enabled:
        enabled.append(PLUGIN_ID)

    COMMUNITY_PLUGINS.write_text(
        json.dumps(enabled, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    install_plugin()
