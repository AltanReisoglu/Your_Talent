# Data Model: FinWiki Memory Event Graph

## MemoryCandidate

Represents one context item that may influence an answer or wiki mutation.

Fields:

- `id`: stable local identifier
- `layer`: `direct_instruction | canonical_policy | day_state |
  project_memory | sourced_wiki | behavior_memory | retrieval_summary |
  compressed_summary`
- `content`: concise text or claim
- `source_path`: local file path, URL, message reference, or event ID
- `created_at`: ISO timestamp when the candidate was recorded
- `observed_at`: ISO timestamp when the candidate was surfaced
- `authority_level`: `canonical | sourced | operational | memory | summary |
  unknown`
- `decision_scope`: `final | evidence | hint | background`
- `valid_from`: optional ISO date
- `valid_until`: optional ISO date
- `freshness_policy`: `none | daily | weekly | monthly | quarterly | annual |
  event_driven`
- `stale_reason`: optional text

Relationships:

- Can be selected by an `AuthorityDecision`
- Can be derived from a `WikiClaim`, `DayStateEntry`, or `MemoryEvent`

## AuthorityDecision

Resolver output for a query or mutation.

Fields:

- `query`: user/system query being resolved
- `selected_candidate_id`: selected candidate, if any
- `selected_decision_scope`: selected candidate decision scope
- `rejected_candidates`: list of candidate IDs with reasons
- `requires_citation`: boolean
- `requires_refresh`: boolean
- `requires_human_confirmation`: boolean
- `reason`: concise resolver explanation
- `created_at`: ISO timestamp

Relationships:

- Emits a `MemoryEvent` of type `authority.decision`
- May create a `MaintenanceIssue` when no citable candidate exists

## WikiClaim

Durable claim contained in an Obsidian Markdown page.

Fields:

- `claim_id`: optional stable claim marker
- `page_path`: path relative to `finwiki-vault/wiki`
- `text`: claim text or excerpt
- `sources`: list of source paths or URLs
- `authority_level`: `canonical | sourced | synthesis | draft`
- `decision_scope`: `final | evidence | hint`
- `valid_from`: optional ISO date
- `valid_until`: optional ISO date
- `freshness_policy`: policy string
- `supersedes`: list of claim IDs or page paths
- `superseded_by`: list of claim IDs or page paths
- `review_status`: `active | needs-review | stale | expired | superseded`

Relationships:

- Supported or contradicted by `SourceCitation`
- Projected as a node in the memory event graph

## SourceCitation

Source/provenance record for a claim.

Fields:

- `source_id`: stable source key or manifest key
- `source_path`: URL or local raw source path
- `source_type`: `raw | url | policy | wiki | user_instruction | synthesis`
- `retrieved_at`: ISO timestamp
- `publisher`: optional publisher/source owner
- `confidence`: `high | medium | low | unknown`
- `notes`: optional redacted notes

Relationships:

- Supports, contradicts, or supersedes a `WikiClaim`
- Links to `wiki/.manifest.json` when available

## DayStateEntry

Short-lived operating whiteboard item.

Fields:

- `entry_id`: stable local identifier
- `status`: `current | superseded | done`
- `summary`: concise operational note
- `next_actions`: list of action strings
- `supersedes`: optional entry IDs
- `source_message`: optional user/system reference
- `updated_at`: ISO timestamp

Relationships:

- Emits `day_state.updated` MemoryEvent
- Can be a MemoryCandidate with `operational` authority

## MemoryEvent

Append-only event in the memory governance log.

Fields:

- `event_id`: monotonic event ID or ULID-like string
- `event_type`: dot-lowercase namespace, e.g. `source.registered`,
  `page.upserted`, `claim.expired`, `authority.decision`
- `target`: affected file, claim ID, source ID, or page path
- `payload`: JSON object with event-specific data
- `actor`: default `finwiki`
- `created_at`: ISO timestamp
- `caused_by`: optional prior event ID

Relationships:

- Replayed into `MemoryGraphProjection`
- Referenced from audit and maintenance reports

## MemoryGraphProjection

Deterministic report built from MemoryEvent records.

Fields:

- `nodes`: objects keyed by ID with type and data
- `relations`: typed edges such as `supports`, `contradicts`, `supersedes`,
  `updates`, `requires_review`
- `stale_items`: pages or claims that are stale/expired
- `contradictions`: claim/source conflicts
- `recent_decisions`: recent authority decisions
- `generated_at`: ISO timestamp

Relationships:

- Read-only projection; never the source of truth
- Can generate Obsidian maintenance pages

## MaintenanceIssue

Obsidian-visible task for memory governance work.

Fields:

- `issue_id`: stable local identifier
- `issue_type`: `stale | expired | uncited | contradiction | missing_owner |
  missing_validity`
- `target`: page path, claim ID, or source ID
- `severity`: `low | medium | high | critical`
- `summary`: concise issue text
- `recommended_action`: next step
- `created_at`: ISO timestamp
- `status`: `open | resolved | accepted-risk`

Relationships:

- Created by event projection or resolver
- Listed in `wiki/maintenance/expiry-review.md`
