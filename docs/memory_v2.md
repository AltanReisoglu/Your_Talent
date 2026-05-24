# FinWiki Memory v2

FinWiki Memory v2 implements the Remember, Cite, Forget contract.

## Remember

Memory is layered by authority and lifespan:

- Direct instruction: current task command.
- Canonical policy: read-only compliance and source-quality rules.
- Day-state: today's operating whiteboard in `finwiki-vault/state/day-state.md`.
- Project memory: learned operating lessons.
- Sourced wiki: durable financial facts in `finwiki-vault/wiki/`.
- Behavior memory: user and agent preferences.
- Retrieval summary: candidate context, not final authority.
- Compressed summary: background context only.

## Cite

Before high-impact or stale-prone answers, call `resolve_memory_authority`.
The resolver reports selected memory, rejected candidates, citation needs,
freshness status, and whether refresh or human confirmation is required.

## Forget

Facts are not deleted when stale. They are demoted, expired, or superseded with
history preserved. Use `mark_wiki_memory_stale` for explicit stale/supersession
decisions.

## Event Graph

`finwiki-vault/logs/memory-events.jsonl` is the append-only proof layer.
`memory_event_graph_report` replays events into a lightweight projection and
updates Obsidian maintenance pages.

## Day-State Rule

Day-state is operational context only. It can coordinate today's work, but it
cannot support financial facts or override canonical policy.
