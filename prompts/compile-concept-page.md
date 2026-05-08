# Compile Concept Page Prompt

Use this prompt when creating or improving a durable financial concept page.

## Task

Create an Obsidian-compatible wiki page that explains a financial concept,
connects it to related topics, and preserves provenance.

## Page Shape

```markdown
---
title: <Concept>
tags: [finance, concepts]
domain: financial-services
last_updated: YYYY-MM-DD
review_status: draft
aliases: []
sources:
  - "..."
related:
  - "..."
---

# <Concept>

## Summary

## Key Mechanics

## Financial Services Context

## Risks / Caveats

## Sources

## See Also
```

## Requirements

- Use `[[wikilinks]]` for related concepts, instruments, companies, markets,
  risks, regulations, and models.
- Mark assumptions and synthesis clearly.
- Add freshness notes when the concept depends on current rules or market data.
