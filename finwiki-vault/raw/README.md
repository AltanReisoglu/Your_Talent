# Raw Source Layer

This directory is the immutable source layer for FinWiki.

- `sources/` stores articles, reports, filings, exported notes, datasets, and clipped Markdown.
- `assets/` stores downloaded images and attachments referenced by sources.

Agents may read files here and register them in `wiki/.manifest.json`, but they should not rewrite raw sources during ingest. The compiled knowledge belongs in `wiki/`.
