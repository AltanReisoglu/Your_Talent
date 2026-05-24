---
title: FinWiki Home
tags:
  - finance
  - obsidian
  - knowledge-base
domain: financial-services
last_updated: 2026-05-24
review_status: active
aliases:
  - FinWiki
sources:
  - "LLM synthesis"
related:
  - "index"
  - "project/index"
---

# FinWiki Home

FinWiki's knowledge base is this Obsidian vault. The agent reads and writes the
Markdown files under `wiki/`, while Obsidian provides browsing, graph view,
backlinks, and manual editing.

## Main Areas

- [Financial Knowledge Index](index.md)
- [Project Workspace](project/index.md)
- [Spec Kit Feature Index](project/specs.md)
- [Evidence Index](project/evidence/index.md)
- [Architecture Map](project/architecture.md)

## Knowledge Layers

- `raw/`: immutable source material and attachments
- `wiki/`: canonical compiled knowledge base
- `wiki/project/`: project/spec/evidence navigation
- `memories/`: behavior and preference memory, not financial facts
- `policies/`: read-only compliance and source-quality rules
- `logs/`: audit, observation, and maintenance records

## Agent Rule

Durable financial knowledge belongs in `wiki/` as Obsidian-compatible Markdown.
Reusable project knowledge belongs in `wiki/project/`. Raw evidence stays in
`raw/`.

## See Also

[[discounted-cash-flow-dcf]] | [[spec-kit-workflow]] | [[finwiki-environment]]
