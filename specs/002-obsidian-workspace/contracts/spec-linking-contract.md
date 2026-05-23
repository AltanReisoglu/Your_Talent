# Contract: Spec-to-Obsidian Linking

## Canonical Artifact Rule

Spec Kit artifacts remain canonical in `specs/NNN-feature-name/`:

- `spec.md`
- `plan.md`
- `tasks.md`
- `evidence.md`

Obsidian-facing project pages may summarize these artifacts, but they must link
back to the canonical files.

## Required Links for Feature Summary Pages

Each feature summary page must include:

- Link to the feature directory
- Link to `spec.md`
- Link to `plan.md`
- Link to `tasks.md` when it exists
- Link to `evidence.md` when it exists
- Links to related FinWiki pages
- Links to related architecture docs or decisions

## Required Status Labels

Use one of:

- `draft`
- `planned`
- `tasks-ready`
- `implemented`
- `archived`

## Link Style

- Use Obsidian wikilinks for wiki pages, e.g. `[[discounted-cash-flow]]`.
- Use relative Markdown links for non-wiki repo files, e.g.
  `[plan](../../specs/002-obsidian-workspace/plan.md)`.
- Do not copy raw source content into project pages; link to `raw/` or source
  registry entries.

## Compliance Rule

Project pages must not override `.specify/memory/constitution.md`, `AGENTS.md`,
or files under `policies/`. They can link to those documents and summarize their
current role.
