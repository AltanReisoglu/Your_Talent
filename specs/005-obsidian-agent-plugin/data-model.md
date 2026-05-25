# Data Model: FinWiki Obsidian Agent Plugin

## PluginSettings

- `endpoint`: Full local invoke URL. Default `http://127.0.0.1:8000/invoke`.
- `userId`: User identity sent to FinWiki. Default `obsidian-user`.
- `sessionPrefix`: Prefix used when generating session IDs. Default `obsidian`.
- `maxContextChars`: Maximum selected/note context characters. Default `12000`.

## AgentRequest

- `user_id`: User identity from settings.
- `session_id`: Generated per request using session prefix and timestamp.
- `message`: User prompt plus optional note context.

## AgentResponse

- `response`: User-facing answer rendered in Obsidian.
- `thread_id`: FinWiki thread ID returned by gateway.
- `hooks`: Optional hook trace from the existing runtime.

## NoteContext

- `path`: Active vault-relative note path.
- `mode`: `selection` or `note`.
- `content`: Selected text or truncated active note content.
- `truncated`: Whether content exceeded `maxContextChars`.

## State Transitions

1. User runs command.
2. Plugin builds `AgentRequest`.
3. Plugin displays loading notice.
4. Gateway returns `AgentResponse` or error.
5. Plugin shows response modal.
6. User may explicitly append response to active note.
