# Tasks: FinWiki Obsidian Agent Plugin

**Input**: Design documents from `specs/005-obsidian-agent-plugin/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Syntax and smoke checks are required in evidence.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

**Evidence**: Add or update `evidence.md` before considering the feature complete.

## Phase 1: Setup

- [x] T001 Create plugin source directory in `obsidian-plugin/finwiki-agent/`
- [x] T002 Create install helper script in `scripts/install_obsidian_plugin.py`

## Phase 2: Foundational

- [x] T003 Create Obsidian plugin manifest in `obsidian-plugin/finwiki-agent/manifest.json`
- [x] T004 Implement settings and gateway request helper in `obsidian-plugin/finwiki-agent/main.js`
- [x] T005 Add plugin styles in `obsidian-plugin/finwiki-agent/styles.css`

## Phase 3: User Story 1 - Ask FinWiki From Obsidian (Priority: P1)

**Goal**: Send custom prompts and selected/note context to the existing FinWiki gateway.

**Independent Test**: Install plugin, run ask command, receive gateway response in Obsidian modal.

- [x] T006 [US1] Add custom prompt modal command in `obsidian-plugin/finwiki-agent/main.js`
- [x] T007 [US1] Add selection/current note context command in `obsidian-plugin/finwiki-agent/main.js`
- [x] T008 [US1] Add response modal rendering in `obsidian-plugin/finwiki-agent/main.js`

## Phase 4: User Story 2 - Append Useful Answers to Notes (Priority: P2)

**Goal**: Let the user append a response to the active note by explicit action.

**Independent Test**: Use append button and verify the active Markdown note receives one response block.

- [x] T009 [US2] Implement active-note append action in `obsidian-plugin/finwiki-agent/main.js`
- [x] T010 [US2] Guard append when no Markdown note is active in `obsidian-plugin/finwiki-agent/main.js`

## Phase 5: User Story 3 - Run Wiki Operations From Commands (Priority: P3)

**Goal**: Provide commands for ingest and lint workflows.

**Independent Test**: Run each command and verify the generated request reaches `/invoke`.

- [x] T011 [US3] Add ingest current note command in `obsidian-plugin/finwiki-agent/main.js`
- [x] T012 [US3] Add wiki lint command in `obsidian-plugin/finwiki-agent/main.js`

## Phase 6: Polish & Evidence

- [x] T013 Document plugin usage in `obsidian-plugin/finwiki-agent/README.md`
- [x] T014 Install plugin into `finwiki-vault/.obsidian/plugins/finwiki-agent/`
- [x] T015 Run manifest JSON validation and JavaScript syntax checks
- [x] T016 Create evidence bundle in `specs/005-obsidian-agent-plugin/evidence.md`

## Dependencies & Execution Order

- Setup precedes all implementation tasks.
- Foundational plugin manifest/settings precedes user-story commands.
- User Story 1 is the MVP.
- User Story 2 and User Story 3 can be implemented after the gateway helper exists.
- Evidence is final.
