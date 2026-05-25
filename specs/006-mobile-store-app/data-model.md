# Data Model: FinWiki Mobile Store App

## MobileUser

- `id`: Stable backend identity.
- `auth_provider`: Guest, email, Apple, Google, or enterprise SSO.
- `created_at`: Account creation timestamp.
- `deletion_requested_at`: Optional timestamp for account deletion workflow.
- `region`: Optional locale/store region for policy and language handling.

## MobileSession

- `id`: Session identifier sent to FinWiki backend.
- `user_id`: Owning user or guest ID.
- `device_id`: Non-secret device installation identifier where allowed.
- `created_at`: Session start timestamp.
- `last_active_at`: Last interaction timestamp.
- `status`: Active, expired, deleted, or restricted.

## ChatMessage

- `id`: Message ID.
- `session_id`: Mobile session ID.
- `role`: User, assistant, tool, or system event.
- `content`: Prompt or response text.
- `source_refs`: Wiki/source references returned by backend.
- `risk_flags`: Financial safety, stale data, no-source, or hook-blocked markers.
- `created_at`: Message timestamp.

## WikiPageSummary

- `path`: Canonical wiki page path.
- `title`: Display title.
- `summary`: Mobile-safe short summary.
- `category`: Concepts, companies, markets, macro, regulation, risk, models, sources, strategies.
- `last_updated`: Page freshness timestamp.
- `review_status`: Draft, active, stale, expired, or needs-review.
- `related`: Related wiki page references.

## IngestSubmission

- `id`: Submission ID.
- `user_id`: Submitter.
- `type`: Note, URL, excerpt, or attachment metadata.
- `content`: User-provided text or URL.
- `status`: Draft, queued, running, completed, blocked, failed.
- `target_page`: Suggested or actual wiki page path.
- `created_at`: Submission timestamp.
- `result_summary`: Backend ingest result.

## PrivacyInventoryItem

- `data_type`: Contact info, identifiers, user content, diagnostics, usage data, etc.
- `purpose`: App functionality, analytics, fraud prevention, support, personalization.
- `linked_to_user`: Boolean.
- `shared_with_third_parties`: Boolean.
- `processor`: Backend, model provider, analytics SDK, crash reporter, or payment provider.
- `retention_policy`: Retention and deletion handling.
- `store_form_mapping`: Apple App Privacy and Google Data Safety labels.

## StoreSubmissionPackage

- `platform`: iOS or Android.
- `bundle_id`: App identifier/package name.
- `build_number`: Submitted build version.
- `privacy_policy_url`: Public policy URL.
- `support_url`: Public support URL.
- `review_notes`: Reviewer instructions and test credentials.
- `screenshots`: Required screenshots by device class.
- `declarations`: Financial, data safety, content rating, encryption, tracking.
- `status`: Draft, beta-ready, submitted, approved, rejected, released.

## State Transitions

### Chat Request

Draft prompt → submitted → backend running → completed | failed | blocked

### Ingest Submission

Draft → queued → running → completed | blocked | failed

### Account Deletion

Active → deletion requested → retention/legal hold check → deleted/anonymized

### Store Release

Local build → internal test → external/closed beta → store submission → review
→ approved/rejected → release
