# Query And File Prompt

Use this prompt when a user asks a valuable question whose answer should become
part of the wiki.

## Task

Answer the user from the wiki and sources, then decide whether the answer is
durable enough to file back into the wiki.

## Workflow

1. Read `wiki.config.md`.
2. Search `wiki/index.md`, `sources.md`, and relevant wiki pages.
3. If the wiki is incomplete or stale, run research through the orchestrator.
4. Answer the user in their language.
5. If reusable, file the answer into:
   - an existing relevant page, or
   - `wiki/questions/<slug>.md` for Q&A-style reusable analysis.
6. Update `wiki/index.md` and `wiki/log.md`.

## Filing Criteria

File the answer when it:

- connects multiple sources or pages,
- clarifies a recurring financial concept,
- records a decision or durable analysis,
- creates a useful comparison table,
- identifies a contradiction or stale claim.

Do not file casual chat, one-off preferences, secrets, or unsupported market facts.
