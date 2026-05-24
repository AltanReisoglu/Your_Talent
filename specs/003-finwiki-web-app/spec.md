# Feature Specification: FinWiki Working Web Application

**Feature Branch**: `003-finwiki-web-app`
**Created**: 2026-05-23
**Status**: Draft
**Input**: User description: "I want a working application now. Follow the global harness rules and use different languages if needed."

## User Scenarios & Testing

### User Story 1 - Use FinWiki from a browser (Priority: P1)

A user can open a local web page, type a question, send it to FinWiki, and see
the response without manually calling curl.

**Why this priority**: The project is not usable as an application until it has a
basic UI surface.

**Independent Test**: Run the C# gateway, open `/`, submit a message, and receive
a visible response.

**Acceptance Scenarios**:

1. **Given** the C# gateway is running, **When** the user visits `/`, **Then** a
   FinWiki web UI is served.
2. **Given** the user enters "DCF nedir?", **When** they submit, **Then** the UI
   posts to `/invoke` and renders the response.

---

### User Story 2 - Preserve the Python agent runtime (Priority: P1)

The browser and C# gateway must call the existing Python bridge rather than
reimplementing agent behavior in C#.

**Why this priority**: This preserves the project's runtime boundary discipline.

**Independent Test**: Inspect C# code and verify `/invoke` still uses
`scripts/invoke_agent.py`.

**Acceptance Scenarios**:

1. **Given** a request arrives at `/invoke`, **When** it is processed, **Then**
   C# launches the Python bridge and returns its JSON response.
2. **Given** a hook blocks a prompt, **When** the UI receives the response,
   **Then** the hook block message and trace are visible.

---

### User Story 3 - Show runtime status and traces (Priority: P2)

A user can see basic service status and the latest hook trace from a request.

**Why this priority**: Agent systems need visible execution state, not only final
text.

**Independent Test**: Submit a blocked prompt and verify hook trace details are
rendered in the UI.

**Acceptance Scenarios**:

1. **Given** `/health` is available, **When** the UI loads, **Then** it displays
   service status.
2. **Given** an invoke response includes `hooks`, **When** the UI renders it,
   **Then** hook events are visible.

### Edge Cases

- Empty messages must not be submitted.
- Python worker failures must return readable gateway errors without leaking
  secrets.
- The UI must remain usable on desktop and mobile widths.
- Missing API keys may cause the model call to fail; the gateway should surface a
  readable error from `/invoke`.
- Hugging Face Router requires `HF_TOKEN`; missing token must produce a clear
  Python-side configuration error.

## Requirements

### Functional Requirements

- **FR-001**: C# gateway MUST serve a browser UI at `/`.
- **FR-002**: Browser UI MUST call existing `/invoke` endpoint.
- **FR-003**: C# `/invoke` MUST continue using `scripts/invoke_agent.py`.
- **FR-004**: UI MUST display response text, user/session/thread metadata, and
  hook trace information when present.
- **FR-005**: UI MUST persist `user_id` and `session_id` locally for repeated
  conversations.
- **FR-006**: UI MUST provide sample prompts for quick smoke testing.
- **FR-007**: README MUST document how to run and test the working app.
- **FR-008**: Evidence MUST record syntax/build/smoke-test results.
- **FR-009**: Python model configuration MUST support Hugging Face Router via an
  OpenAI-compatible provider without moving agent logic into C#.

### Key Entities

- **InvokeRequest**: `user_id`, `session_id`, `message`
- **InvokeResponse**: `user_id`, `session_id`, `thread_id`, `response`, `hooks`
- **HookTrace**: events and last quality gate returned from Python runtime

## Success Criteria

### Measurable Outcomes

- **SC-001**: `dotnet build dotnet-api/FinWiki.Api.csproj` passes.
- **SC-002**: `GET /health` returns `200`.
- **SC-003**: `GET /` returns HTML containing the FinWiki app shell.
- **SC-004**: `POST /invoke` returns JSON for a hook-blocked prompt without a
  model call.
- **SC-005**: The UI uses no new runtime service beyond the C# gateway and Python
  bridge.

## Assumptions

- The C# gateway is the preferred product surface for local browser use.
- Python remains the only agent runtime.
- A full production auth layer is out of scope for this first working app.
