# Obsidian Workspace

FinWiki can be opened from the repository root as an Obsidian vault. The goal is
to make specs, implementation evidence, architecture notes, wiki pages, and
maintenance logs navigable without copying canonical files into a second system.

## Vault Root

Open this directory in Obsidian:

```text
/home/altan/Desktop/Your_Talent/finwiki-vault
```

Do not open the code repository root as the user-facing vault. The user-facing
vault is intentionally isolated so `agents/`, `tools/`, `specs/`, `dotnet-api/`,
and other implementation files do not appear in Obsidian.

The vault includes:

- `home.md` for the user-facing entry point
- `wiki/` for compiled financial knowledge
- `raw/` for source material
- `raw/assets/` for attachments
- `logs/` for vault maintenance notes
- `wiki/templates/` for Obsidian templates

The isolated vault includes tracked vault configuration under
`finwiki-vault/.obsidian/`.
Machine-specific workspace files are ignored by Git:

```text
finwiki-vault/.obsidian/workspace.json
finwiki-vault/.obsidian/workspace-mobile.json
finwiki-vault/.obsidian/cache/
```

## Knowledge Base Contract

FinWiki's agent knowledge base is the Obsidian Markdown vault:

- Agent tools read and write `wiki/**/*.md`.
- Obsidian reads the same files for graph view, backlinks, search, and manual
  editing.
- `home.md` is the human entry point.
- `wiki/index.md` is the financial knowledge catalog.
- `raw/assets/` is the attachment folder for Obsidian.
- `wiki/templates/` contains manual note templates.

No separate vector database, SaaS memory product, or hidden document store is
the source of truth for durable knowledge. Those can be added later as indexes
over the vault, not replacements for it.

## Canonical Ownership

Spec Kit remains the source of truth for AI coding workflow artifacts inside the
code repository:

```text
specs/NNN-feature-name/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

Those artifacts are intentionally not part of the user-facing vault. The user
edits knowledge, not the code repo.

## Project Navigation Pages

The user-facing vault lives under:

```text
finwiki-vault/
├── home.md
├── wiki/
├── raw/
├── logs/
├── sources.md
└── wiki.config.md
```

## Frontmatter Standard

Project navigation pages use this metadata shape:

```yaml
---
title: Example
type: project-index
tags:
  - project
  - obsidian
last_updated: YYYY-MM-DD
status: active
related:
  - specs
---
```

Allowed `type` values are documented in
`specs/002-obsidian-workspace/contracts/obsidian-frontmatter.schema.json`.

## Link Rules

- Use relative Markdown links for repo files:
  `[plan](../../specs/002-obsidian-workspace/plan.md)`
- Use Obsidian wikilinks for compiled wiki topics:
  `[[discounted-cash-flow-dcf]]`
- Link to raw sources and assets; do not copy raw source contents into project
  pages.
- Link evidence bundles directly when a feature has `evidence.md`.

## Plugin-Optional Operation

No Obsidian plugin is required for the core workflow. The pages are plain
Markdown and can be browsed with any editor.

Optional improvements:

```dataview
TABLE status, last_updated
FROM "wiki/project"
WHERE contains(tags, "spec-kit")
SORT last_updated DESC
```

Treat Dataview snippets as convenience only. The repository must remain usable
without Dataview, Canvas, Sync, Publish, or any SaaS dependency.

## CLI-Only Validation

These checks do not require Obsidian:

```bash
.venv/bin/python scripts/update_obsidian_project_index.py
.venv/bin/python -m py_compile scripts/update_obsidian_project_index.py
.venv/bin/python scripts/spec_evidence_check.py --feature 002-obsidian-workspace --require-plan --require-tasks --require-evidence
```

For link review, inspect generated links in:

```text
wiki/project/index.md
wiki/project/specs.md
wiki/project/features/*.md
wiki/project/evidence/index.md
```

## Safety Rules

- Do not write financial facts into `memories/`.
- Do not modify `.specify/` generated infrastructure from Obsidian pages.
- Do not edit `policies/` through project navigation pages.
- Keep raw evidence under `raw/`; project pages link to it.
- Evidence bundles must record checks run, skipped checks, and residual risks.
