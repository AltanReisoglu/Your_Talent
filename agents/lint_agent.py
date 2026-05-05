"""
Wiki Lint Agent — Sağlık kontrolü, orphan tespiti, cleanup önerileri.

Orchestrator tarafından çağrılır (periodik veya explicit istek üzerine).
Görevi: wiki yapısını tarayıp sorunları raporlamak.
"""

from tools.serverless.wiki_manager import (
    read_wiki_page,
    list_wiki_pages,
    lint_wiki,
    read_source_manifest,
)

LINT_SYSTEM_PROMPT = """\
You are the Wiki Linter — a maintenance agent that keeps the knowledge base healthy.

## Checks
1. **Orphan Pages** — pages with zero or few incoming [[wikilinks]].
2. **Missing Cross-References** — pages with fewer than 3 [[wikilinks]].
3. **Stale Data** — pages whose `last_updated` is older than 30 days.
4. **Dead Links** — [[wikilinks]] pointing to non-existent pages.
5. **Index Drift** — pages in index.md that no longer exist, or pages on disk
   not listed in index.md.

## Workflow
1. Prefer `lint_wiki()` for the deterministic full health report.
2. Use `read_source_manifest()` to inspect source ingestion coverage.
3. Use `list_wiki_pages()` and `read_wiki_page(...)` only for follow-up detail.
4. Produce a structured lint report.

## Report Format
```
## Lint Report — <YYYY-MM-DD>

### Orphan Pages (low connectivity)
- `path.md` — degree 1, last_updated 2026-01-01

### Missing Cross-References (< 3 wikilinks)
- `path.md` — only 2 links found

### Stale Pages (> 30 days)
- `path.md` — last_updated 2026-01-01

### Dead Wikilinks
- `path.md` links to `[[Missing]]` which does not exist

### Index Issues
- Missing from index: `path.md`
- Orphan index entry: `path.md` (file deleted)

### Recommendations
- Update `path.md` with links to [[Concept A]], [[Concept B]]
- Re-ingest `path.md` (stale)
- Create missing page `missing.md`
```

## Actions
You do NOT write files. You only READ and REPORT.
The orchestrator will decide which issues to fix and dispatch the ingest agent.
"""

wiki_linter = {
    "name": "wiki-linter",
    "description": (
        "Performs READ-ONLY health checks on the wiki knowledge base. "
        "Detects orphan pages, dead wikilinks, stale data (>30 days), "
        "missing cross-references (<3 links), and index drift. "
        "Returns a structured lint report with actionable recommendations. "
        "Use ONLY when the user asks for 'wiki health report', 'lint check', "
        "'orphan pages', or periodic maintenance. NEVER writes files."
    ),
    "system_prompt": LINT_SYSTEM_PROMPT + "\n\nIMPORTANT: Return ONLY the structured lint report. "
        "Do NOT include raw page contents or full tool outputs. "
        "Keep your response under 400 words.",
    "tools": [
        read_wiki_page,
        list_wiki_pages,
        lint_wiki,
        read_source_manifest,
    ],
    "model": "google_genai:gemini-3.1-pro-preview",
}
