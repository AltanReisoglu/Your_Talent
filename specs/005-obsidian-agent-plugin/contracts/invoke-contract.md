# Contract: Obsidian Plugin to FinWiki Gateway

## Endpoint

`POST http://127.0.0.1:8000/invoke`

The URL is configurable in plugin settings.

## Request

```json
{
  "user_id": "obsidian-user",
  "session_id": "obsidian-20260525-120000",
  "message": "User prompt and optional note context"
}
```

## Success Response

```json
{
  "user_id": "obsidian-user",
  "session_id": "obsidian-20260525-120000",
  "thread_id": "finwiki:obsidian-user:obsidian-20260525-120000",
  "response": "FinWiki answer",
  "hooks": {
    "events": []
  }
}
```

## Error Response

Gateway errors may return JSON problem details or plain text. The plugin must show a readable error message and avoid writing anything to the note.
