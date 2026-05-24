"""
FinWiki memory configuration.

Memory is for agent/user/policy behavior. Durable financial knowledge remains
in `/wiki/`; raw evidence remains in `/raw/`.
"""

from deepagents.middleware.filesystem import FilesystemPermission

FINWIKI_MEMORY_FILES = [
    "/AGENTS.md",
    "/finwiki-vault/wiki.config.md",
    "/finwiki-vault/sources.md",
    "/finwiki-vault/home.md",
    "/finwiki-vault/wiki/home.md",
    "/finwiki-vault/state/day-state.md",
    "/memories/agent.md",
    "/memories/user_preferences.md",
    "/policies/compliance.md",
    "/policies/source_quality.md",
]

FINWIKI_MEMORY_PERMISSIONS = [
    FilesystemPermission(
        operations=["write"],
        paths=["/policies/**"],
        mode="deny",
    ),
]
