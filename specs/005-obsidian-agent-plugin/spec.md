# Feature Specification: FinWiki Obsidian Agent Plugin

**Feature Branch**: `005-obsidian-agent-plugin`

**Created**: 2026-05-25

**Status**: Draft

**Input**: User description: "Expose FinWiki as an Obsidian plugin so the user can operate the FinWiki agent directly from the Obsidian vault."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask FinWiki From Obsidian (Priority: P1)

A user working inside the FinWiki Obsidian vault can send a custom question, the active note, or the selected text to the existing local FinWiki agent and see the answer without leaving Obsidian.

**Why this priority**: This is the core value of the plugin. It turns Obsidian from a passive Markdown viewer into the operating console for the agent-backed knowledge base.

**Independent Test**: Start the local FinWiki gateway, enable the plugin in the vault, run the "Ask FinWiki" command, and receive an answer rendered in Obsidian.

**Acceptance Scenarios**:

1. **Given** the gateway is running, **When** the user runs "Ask FinWiki" and submits a prompt, **Then** the plugin sends the prompt to FinWiki and displays the response.
2. **Given** a note has selected text, **When** the user runs "Ask FinWiki about selection/current note", **Then** the plugin includes the selected text as context.
3. **Given** no text is selected, **When** the user runs the context command from a Markdown note, **Then** the plugin includes the active note path and content as context.

---

### User Story 2 - Append Useful Answers to Notes (Priority: P2)

A user can append the latest FinWiki answer to the active note so reusable outputs can become part of the Markdown knowledge workflow.

**Why this priority**: Useful answers should not remain trapped in a modal; they should land in the vault when the user chooses to keep them.

**Independent Test**: Run an agent request, click append, and verify the active Markdown note receives a timestamped FinWiki response block.

**Acceptance Scenarios**:

1. **Given** an answer is visible in the plugin response modal, **When** the user clicks "Append to note", **Then** the answer is added to the active Markdown note.
2. **Given** no Markdown note is active, **When** the user tries to append, **Then** the plugin shows a clear error and does not write elsewhere.

---

### User Story 3 - Run Wiki Operations From Commands (Priority: P3)

A user can trigger common FinWiki workflows from Obsidian commands: query the wiki, ingest the current note, and run a lint/health check.

**Why this priority**: These commands map directly to the user's desired workflow: Obsidian becomes the manual control surface for query, ingest, and lint.

**Independent Test**: Run each command from the command palette and verify that the plugin sends the appropriate request to the existing agent gateway.

**Acceptance Scenarios**:

1. **Given** a current note is open, **When** the user runs "Ingest current note", **Then** the plugin sends an ingest-oriented prompt containing note path and content.
2. **Given** the vault is open, **When** the user runs "Run FinWiki lint", **Then** the plugin asks the agent for a concise wiki health report.

---

### Edge Cases

- The gateway is not running or returns a non-200 response.
- The active view is not a Markdown note.
- The active note is very large.
- The agent returns hook-blocked output.
- The user changes the gateway URL or identity settings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an Obsidian plugin manifest and executable plugin entrypoint that can be installed into the FinWiki vault.
- **FR-002**: System MUST let users configure the local FinWiki invoke endpoint, user ID, and session prefix from Obsidian settings.
- **FR-003**: System MUST call the existing `/invoke` JSON contract and MUST NOT duplicate agent reasoning, memory, query, ingest, or lint logic in the plugin.
- **FR-004**: Users MUST be able to submit a custom prompt to FinWiki from Obsidian.
- **FR-005**: Users MUST be able to send selected text or active note content as context to FinWiki.
- **FR-006**: Users MUST be able to append the latest response to the active Markdown note by explicit action only.
- **FR-007**: System MUST provide command palette entries for ask, ask with context, ingest current note, and lint.
- **FR-008**: System MUST display readable errors when the gateway is unavailable or returns invalid data.
- **FR-009**: System MUST avoid reading `.env`, `.git`, raw protected files, or hidden vault internals as note context.

### Key Entities *(include if feature involves data)*

- **Plugin Settings**: Gateway URL, user identity, session prefix, and note context length limit.
- **Agent Request**: The JSON request sent to `/invoke` with `user_id`, `session_id`, and `message`.
- **Agent Response**: The JSON response received from `/invoke`, including text and optional hook trace.
- **Note Context**: Active note path, selected text, or note content included in a user-controlled prompt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A local Obsidian vault can load the plugin from `.obsidian/plugins/finwiki-agent/`.
- **SC-002**: A custom prompt sent from Obsidian receives a response from the running FinWiki gateway.
- **SC-003**: The context command includes selected text when selection exists and active note content otherwise.
- **SC-004**: Appending an answer modifies only the currently active Markdown note.
- **SC-005**: Plugin validation passes JavaScript syntax checks and manifest JSON validation.

## Assumptions

- The user runs the existing C# gateway locally at `http://127.0.0.1:8000/invoke` unless settings override it.
- The plugin is local-first and not yet packaged for the public Obsidian community marketplace.
- Obsidian desktop is the target runtime for v1.
- The plugin communicates with the agent through the gateway only; Python remains the agent runtime.
