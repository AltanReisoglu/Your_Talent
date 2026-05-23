# Implementation Plan: Obsidian-Integrated Spec Workspace

**Branch**: `002-obsidian-workspace` | **Date**: 2026-05-23 | **Spec**: `spec.md`

**Input**: Feature specification from `specs/002-obsidian-workspace/spec.md`

## Summary

Build a Markdown-first integration where Obsidian becomes the navigable workspace
around Spec Kit feature artifacts, FinWiki wiki pages, architecture notes, and
evidence bundles. Spec Kit remains the execution source of truth; Obsidian adds
durable navigation, backlinks, graph view, and project memory.

## Technical Context

**Language/Version**: Markdown, YAML frontmatter, Python 3.13 helper scripts

**Primary Dependencies**: GitHub Spec Kit, Obsidian-compatible Markdown, existing
FinWiki wiki conventions

**Storage**: Local repository files under `specs/`, `wiki/`, `docs/`, `logs/`,
`raw/`, and `.specify/`

**Testing**: `scripts/spec_evidence_check.py`, Markdown link review,
`tools/serverless/wiki_manager.py::lint_wiki` where applicable

**Target Platform**: Local developer machine; repository opened as Obsidian vault

**Project Type**: Documentation/workflow integration over an AI agent harness

**Performance Goals**: No runtime performance impact; navigation should be
file-based and instant for local Markdown

**Constraints**: Do not move Spec Kit canonical files; do not require Obsidian
plugins for core operation; do not duplicate raw sources; do not write financial
facts into memory files

**Scale/Scope**: Dozens to hundreds of feature specs, wiki pages, evidence
bundles, and architecture notes

## Constitution Check

*GATE: Passed before Phase 0 research. Re-check after Phase 1 design.*

- Runtime Boundary: No Python/C# runtime boundary change. Obsidian integration is
  Markdown/workflow only.
- Financial Safety: FinWiki source lineage, no-advice, raw-source immutability,
  and policy read-only rules are preserved.
- Protected Surfaces: `.env`, `.git`, `raw/`, and `policies/` are not modified.
- Single Writer: This plan does not introduce parallel wiki mutation. Future
  automation must route canonical wiki writes through existing wiki tooling.
- Evidence: Completed implementation must produce `evidence.md` and pass
  `scripts/spec_evidence_check.py --require-evidence`.

## Project Structure

### Documentation (this feature)

```text
specs/002-obsidian-workspace/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── obsidian-frontmatter.schema.json
│   └── spec-linking-contract.md
└── tasks.md
```

### Source Code / Knowledge Surfaces

```text
wiki/
├── index.md
├── project/                 # proposed Obsidian project navigation pages
└── concepts/

specs/
└── NNN-feature-name/
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── evidence.md

docs/
logs/
raw/
.specify/
```

**Structure Decision**: Use repository root as the Obsidian vault for development
because it exposes `wiki/`, `specs/`, `docs/`, and `logs/` together. Keep
`.specify/` as hidden workflow infrastructure, not as the primary Obsidian
navigation surface.

## FinWiki Constitution Gates

- Runtime Boundary: Python remains the agent runtime; C# remains a gateway unless
  this plan explicitly justifies a boundary change. **Status: passed.**
- Financial Safety: User-facing financial behavior avoids personalized buy/sell
  advice and preserves source/freshness/lineage where facts are durable.
  **Status: passed.**
- Protected Surfaces: `.env`, `.git`, `raw/`, and `policies/` are not modified
  without explicit risk acceptance. **Status: passed.**
- Single Writer: Wiki/index/log/manifest writes remain serialized through the
  wiki-ingestor path. **Status: passed.**
- Evidence: The feature must produce `evidence.md` with checks run, checks not
  run, and residual risk before commit or push. **Status: required for
  implementation phase.**

## Phase 0: Research

See `research.md`.

## Phase 1: Design & Contracts

- Data model: `data-model.md`
- Frontmatter schema: `contracts/obsidian-frontmatter.schema.json`
- Linking contract: `contracts/spec-linking-contract.md`
- Quickstart: `quickstart.md`

## Post-Design Constitution Re-check

- Runtime Boundary: still passed; no runtime implementation selected.
- Financial Safety: still passed; design keeps facts in `wiki/` and evidence in
  `specs/`, not memory.
- Protected Surfaces: still passed; design reads `raw/` links but does not move
  sources.
- Single Writer: still passed; proposed project navigation pages summarize and
  link, while canonical wiki writes stay with wiki tooling.
- Evidence: pending for implementation tasks.

## Complexity Tracking

No constitution violations. The only added complexity is a project navigation
layer, justified because it keeps AI coding artifacts and FinWiki knowledge
discoverable as a single durable environment.
