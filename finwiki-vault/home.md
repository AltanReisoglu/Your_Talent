---
title: FinWiki Vault Home
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
  - "wiki/index"
---

# FinWiki Vault Home

This vault is the user-facing knowledge base managed by the FinWiki agent.

The code repository is intentionally not part of this Obsidian vault. The agent
runtime lives outside the vault and reads/writes these Markdown files as its
durable knowledge base.

## Start Here

- [Financial Knowledge Index](wiki/index.md)
- [Memory Governance](wiki/maintenance/memory-governance.md)
- [Memory Expiry Review](wiki/maintenance/expiry-review.md)
- [Day State](state/day-state.md)
- [DCF Example](wiki/concepts/discounted-cash-flow-dcf.md)
- [Ingest Log](wiki/log.md)

## Folders

- `wiki/`: canonical compiled knowledge pages
- `raw/`: source material and attachments
- `raw/assets/`: Obsidian attachment folder
- `wiki/inbox/`: manual inbox notes
- `wiki/templates/`: note templates
- `wiki/maintenance/`: memory governance and expiry review
- `state/`: short-lived operational agent state
- `logs/`: vault-level maintenance notes

## Operating Rule

Chat with the FinWiki agent to create, update, lint, and ingest this vault. Use
Obsidian for reading, graph exploration, manual review, and small editorial
corrections.
