# Lint Wiki Prompt

Use this prompt for maintenance and self-healing checks.

## Task

Run a structural and knowledge-quality health check over the FinWiki vault.

## Checks

- Missing index entries
- Orphan pages with no inbound links
- Dead `[[wikilinks]]`
- Pages with fewer than three useful links
- Missing or malformed YAML frontmatter
- Missing source markers on factual claims
- Stale `last_updated` dates
- Conflicting claims across pages
- Raw sources not compiled into wiki pages
- Important concepts mentioned but lacking pages
- Verified pages contradicted by newer draft/context pages

## Output

Write a report with:

- Findings by severity
- Suggested page fixes
- Suggested source checks
- Candidate pages to create
- Human verification needed

Append a short maintenance summary to `logs/maintenance-log.md` when changes are made.
