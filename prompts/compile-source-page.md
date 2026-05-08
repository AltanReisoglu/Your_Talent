# Compile Source Page Prompt

Use this prompt when turning a raw source, URL, dataset, filing, or report into
compiled wiki knowledge.

## Task

Read `wiki.config.md`, inspect the source, register it in `sources.md` and
`wiki/.manifest.json`, then update the most relevant wiki pages.

## Requirements

- Treat `raw/` as immutable.
- Preserve source title, author/issuer, publication date, access date, URL/path,
  source type, and reliability notes where available.
- Extract reusable entities: companies, instruments, markets, risks, regulations,
  models, macro variables, and data sources.
- Prefer updating existing pages over creating duplicates.
- Create a `wiki/sources/` profile page for recurring or high-value sources.
- Every factual claim needs a source marker.

## Output

- Updated or created wiki page(s)
- Updated index/log/manifest/source registry
- A concise user-facing summary with changed pages
