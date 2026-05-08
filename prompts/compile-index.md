# Compile Index Prompt

Use this prompt when rebuilding or refreshing `wiki/index.md`.

## Task

Read `wiki.config.md`, list wiki pages, inspect key frontmatter and summaries,
then update `wiki/index.md` so it remains a useful catalog for humans and agents.

## Requirements

- Preserve YAML frontmatter in `wiki/index.md`.
- Organize pages by FinWiki category.
- Each entry should include a link and one-line summary.
- Do not list `wiki/log.md` or `wiki/.manifest.json` as knowledge pages.
- Flag pages missing from the index and index entries whose files do not exist.
- Keep categories aligned with `wiki.config.md`.

## Output

Write the updated index and append a maintenance note to
`logs/maintenance-log.md` if this was a manual maintenance pass.
