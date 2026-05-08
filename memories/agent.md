# FinWiki Agent Memory

This file is writable long-term memory for FinWiki's operating behavior.
It is not the financial knowledge base. Durable financial facts belong in
`/wiki/`, and raw evidence belongs in `/raw/`.

## Learned Operating Preferences

- Prefer Turkish user-facing answers when the user writes in Turkish.
- Keep wiki pages in English for universal access and Obsidian portability.
- Use conditional fan-out only for multi-dimensional research; keep simple
  concept questions on the fast wiki-query path.
- Preserve the single-writer rule: read/research can fan out, but wiki writes
  happen through `wiki-ingestor` after fan-in synthesis.

## Research Habits To Preserve

- Check existing wiki coverage before fresh research.
- Keep source URLs attached to factual claims.
- Flag stale or conflicting claims instead of silently overwriting them.
- Separate reusable risk, regulation, model, and source-lineage notes into their
  own category pages.

## Memory Boundaries

- Do not store market facts, company financials, or regulatory claims here.
- Do not store secrets, API keys, customer data, or private account data here.
- Store reusable financial knowledge in `/wiki/`.
- Store policies in `/policies/`; those files are read-only to the agent.
