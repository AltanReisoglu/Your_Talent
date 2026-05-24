# FinWiki Config

## Identity

- Name: FinWiki
- Flavor: financial-services
- Audience: financial analysts, operators, researchers, agent workflows, and technical users who need source-backed financial context
- Primary language: wiki pages in English; user-facing answers in the user's language
- Interface: isolated Obsidian-native local Markdown vault

## Purpose

FinWiki compiles financial-services knowledge from raw sources, conversations,
and research tasks into a durable, interlinked Markdown wiki. It should reduce
repeated research, preserve source lineage, and keep financial knowledge
auditable, fresh, and easy to query.

## Knowledge Layers

- `raw/`: immutable source material and attachments
- `raw/assets/`: Obsidian attachment folder
- `home.md`: human entry point for the vault
- `wiki/`: canonical Obsidian Markdown knowledge base
- `wiki/templates/`: manual Obsidian templates
- `derived/`: generated artifacts such as tables, briefs, decks, datasets, and exports
- `prompts/`: local workflow prompts for this wiki
- `logs/maintenance-log.md`: human-readable maintenance and lint history
- `logs/audit-log.jsonl`: machine-readable mutation/provenance events
- `logs/agent-observations.jsonl`: agent/session observations that are not promoted to wiki facts
- `sources.md`: source registry and source quality notes
- `memories/`: agent/user behavioral memory
- `policies/`: read-only compliance and source-quality memory

## Page Types

- Concept page: valuation, accounting, risk, market structure, and methodology concepts
- Company page: issuer/counterparty profiles and analysis
- Instrument page: equities, bonds, funds, derivatives, crypto assets
- Market page: exchange, index, asset-class, or country-market notes
- Macro page: rates, inflation, growth, FX, commodities, policy
- Regulation page: regulators, rules, disclosures, supervisory guidance
- Risk page: credit, market, liquidity, operational, compliance, and model risk
- Model page: valuation, risk, forecast, retrieval, and agent methodologies
- Source page: source profiles, datasets, filings, APIs, providers, lineage notes
- Strategy page: investment frameworks, screening rules, portfolio approaches
- Question page: reusable answers filed from user queries

## Update Rules

1. Read this config before changing wiki structure or page conventions.
2. Preserve raw sources. Do not rewrite files in `raw/` during ingest.
3. Prefer updating existing pages over creating duplicates.
4. Use source-backed claims. If no source exists, mark `[Source: LLM synthesis]`.
5. Preserve contradictions with dates and sources instead of silently overwriting.
6. Use `review_status` to separate draft, reviewed, verified, stale, and deprecated content.
7. File reusable user answers into `wiki/questions/` or the relevant category page.
8. Append maintenance decisions to `logs/maintenance-log.md` when running manual maintenance.
9. Keep `wiki/index.md`, `wiki/log.md`, `wiki/.manifest.json`, and `sources.md` aligned.
10. Use `verify_wiki_claim` before relying on stale or high-impact claims.
11. Use `freshness_report` for time-sensitive company, market, macro, regulation, and strategy pages.
12. Use `observe_agent_event` for operational learnings; do not store financial facts there.
13. Keep the code repository outside this user-facing vault. The agent may use
    repo instructions, but users should only see and edit vault knowledge files.

## Quality Bar

- Every page has YAML frontmatter.
- Every page uses Obsidian-compatible `[[wikilinks]]`.
- Every reusable page should aim for at least three meaningful links.
- Every factual financial claim has source provenance or an explicit synthesis marker.
- Time-sensitive data includes date/freshness context.
- Claim lineage can be traced from page sources and manifest entries.
- Mutation events are audit-logged when tools update wiki pages, index, logs, or manifest.
- Financial analysis uses risk, assumption, and uncertainty framing.
- No direct personalized investment advice.

## Preferred Workflow

```text
raw/source or user question
  -> read wiki.config.md
  -> check wiki/index.md and sources.md
  -> retrieve existing pages
  -> verify lineage/freshness for high-impact claims
  -> research or ingest if needed
  -> fan-in synthesis when multiple lanes are used
  -> write/update wiki page
  -> update index, manifest, logs, audit log, and source registry
  -> answer user with wiki/source references
```

## Agentmemory-Inspired Support Layer

FinWiki borrows selected infrastructure patterns from agentmemory, adapted to a
markdown-first financial wiki:

- Observation journal: `observe_agent_event(...)` records workflow/session
  learnings in `logs/agent-observations.jsonl`. These are not financial facts.
- Audit log: wiki mutations append structured events to `logs/audit-log.jsonl`.
- Claim verification: `verify_wiki_claim(...)` reports candidate supporting
  pages, page sources, source manifest lineage, and freshness status.
- Freshness scoring: `freshness_report(...)` applies finance-specific staleness
  thresholds by category.
- Source lineage: `source_lineage(...)` traces raw/external sources to affected
  wiki pages.
- Privacy redaction: log/source notes pass through `redact_private_data(...)`
  before durable support logs are written.

The wiki remains the source of compiled financial truth. Support logs are
operational memory and observability, not a replacement for `/wiki/`.
