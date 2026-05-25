# Contract: Mobile App ↔ FinWiki Backend

The mobile app calls production HTTPS endpoints. Endpoint names may be exposed by
the existing C# gateway/BFF or a deployment-specific API gateway. The mobile app
does not call Python scripts directly.

## POST /invoke

Send a FinWiki chat/query request.

### Request

```json
{
  "user_id": "mobile-user-id-or-guest-id",
  "session_id": "mobile-session-id",
  "message": "DCF nedir?"
}
```

### Response

```json
{
  "user_id": "mobile-user-id-or-guest-id",
  "session_id": "mobile-session-id",
  "thread_id": "finwiki:mobile-user-id:mobile-session-id",
  "response": "FinWiki answer",
  "hooks": {
    "events": []
  }
}
```

## GET /wiki/search?q={query}

Return mobile-safe wiki page summaries. This can be implemented as a wrapper
over existing `search_wiki`/read tools.

### Response

```json
{
  "results": [
    {
      "path": "concepts/discounted-cash-flow-dcf.md",
      "title": "Discounted Cash Flow (DCF)",
      "summary": "DCF estimates present value from future cash flows.",
      "category": "concepts",
      "last_updated": "2026-05-17",
      "review_status": "draft",
      "related": ["WACC", "Free Cash Flow"]
    }
  ]
}
```

## GET /wiki/page?path={path}

Return one mobile-renderable wiki page. Backend must enforce path validation.

## POST /ingest-submissions

Submit a mobile note, URL, or excerpt for backend-managed ingest.

### Request

```json
{
  "user_id": "mobile-user-id-or-guest-id",
  "type": "url",
  "content": "https://example.com/source",
  "notes": "Optional user note"
}
```

### Response

```json
{
  "submission_id": "ing_123",
  "status": "queued",
  "message": "FinWiki ingest request queued"
}
```

## POST /account/delete

Start account deletion. Required if account creation exists.

### Request

```json
{
  "user_id": "mobile-user-id",
  "confirmation": true
}
```

### Response

```json
{
  "status": "requested",
  "effective_after": "2026-06-24",
  "retained_data_notice": "Security/audit records may be retained where legally required."
}
```

## Error Shape

```json
{
  "error": {
    "code": "backend_unavailable",
    "message": "FinWiki backend is unavailable.",
    "retryable": true
  }
}
```
