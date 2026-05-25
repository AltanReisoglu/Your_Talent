# Tasks: FinWiki Mobile Store App

**Input**: Design documents from `/specs/006-mobile-store-app/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature explicitly requires backend smoke tests, mobile API contract checks, and store-readiness evidence. Mobile dependency installation is not assumed in this task list.

**Organization**: Tasks are grouped by independently testable user story.

**Evidence**: Add or update `evidence.md` before considering the feature complete. Record commands/checks run, checks intentionally skipped, and residual risk.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the mobile app workspace and repository hygiene needed for store-targeted development.

- [x] T001 Create Expo mobile project metadata in `mobile/finwiki/package.json`, `mobile/finwiki/app.json`, `mobile/finwiki/eas.json`, `mobile/finwiki/tsconfig.json`, and `mobile/finwiki/babel.config.js`
- [x] T002 [P] Create mobile source directory layout and environment sample in `mobile/finwiki/src/` and `mobile/finwiki/.env.example`
- [x] T003 [P] Add mobile build/cache ignore patterns to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the backend/mobile contract without moving agent reasoning or wiki mutation into the client.

**Critical**: No user story work can begin until this phase is complete.

- [x] T004 Add Python wiki API bridge for search/page/ingest/account operations in `scripts/wiki_api.py`
- [x] T005 Extend the C# gateway with `/wiki/search`, `/wiki/page`, `/ingest-submissions`, and `/account/delete` in `dotnet-api/Program.cs`
- [x] T006 Define shared mobile API types and HTTP client in `mobile/finwiki/src/services/finwikiApi.ts`
- [x] T007 [P] Add shared mobile UI primitives and financial safety copy in `mobile/finwiki/src/components/`

**Checkpoint**: Backend/mobile contract ready; user story implementation can proceed.

---

## Phase 3: User Story 1 - Use FinWiki From A Mobile App (Priority: P1) MVP

**Goal**: A mobile user can ask FinWiki questions and receive source-aware educational answers.

**Independent Test**: Configure `EXPO_PUBLIC_FINWIKI_API_BASE_URL`, run the app, submit "DCF nedir?", and see a response or recoverable backend error without losing the prompt.

- [x] T008 [US1] Implement chat state, request handling, and recoverable errors in `mobile/finwiki/src/features/chat/ChatScreen.tsx`
- [x] T009 [US1] Implement app shell and tab navigation in `mobile/finwiki/src/shell/App.tsx` and `mobile/finwiki/App.tsx`
- [x] T010 [US1] Surface financial education disclaimer and hook/error status in `mobile/finwiki/src/features/chat/ChatScreen.tsx`

**Checkpoint**: User Story 1 is independently testable.

---

## Phase 4: User Story 2 - Browse And Reuse The Knowledge Base (Priority: P1)

**Goal**: A mobile user can search/open compiled FinWiki pages without using Obsidian.

**Independent Test**: Search "DCF", open the returned page, and see title, freshness/status, body, and related/source hints.

- [x] T011 [US2] Implement wiki search and result rendering in `mobile/finwiki/src/features/wiki/WikiSearchScreen.tsx`
- [x] T012 [US2] Implement wiki page loading and mobile markdown fallback rendering in `mobile/finwiki/src/features/wiki/WikiPageScreen.tsx`

**Checkpoint**: User Story 2 is independently testable.

---

## Phase 5: User Story 3 - Capture Notes And Request Ingest (Priority: P2)

**Goal**: A mobile user can submit a note or URL to backend-managed ingest without direct wiki file writes.

**Independent Test**: Submit a URL or note and receive queued/running/completed/blocked/failed status from the gateway.

- [x] T013 [US3] Implement note/URL capture form and ingest status display in `mobile/finwiki/src/features/capture/CaptureScreen.tsx`
- [x] T014 [US3] Ensure capture uses backend ingest submission API only in `mobile/finwiki/src/services/finwikiApi.ts`

**Checkpoint**: User Story 3 is independently testable.

---

## Phase 6: User Story 4 - Meet Store Review And Privacy Requirements (Priority: P1)

**Goal**: Operators can prepare App Store and Google Play submissions with privacy, financial safety, account deletion, and reviewer evidence.

**Independent Test**: Review `docs/store/release-checklist.md`; no release blocker remains before beta submission.

- [x] T015 [US4] Implement account/privacy settings and deletion request UI in `mobile/finwiki/src/features/account/AccountScreen.tsx`
- [x] T016 [US4] Create privacy inventory in `docs/store/privacy-inventory.md`
- [x] T017 [US4] Create App Store, Google Play, and shared release checklists in `docs/store/app-store-connect.md`, `docs/store/google-play-console.md`, and `docs/store/release-checklist.md`

**Checkpoint**: User Story 4 store-readiness artefacts exist.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate contracts, update evidence, and make the implementation reviewable.

- [x] T018 [P] Add Python tests for the wiki API bridge in `tests/test_wiki_api_bridge.py`
- [x] T019 Update mobile quickstart and operator runbook in `mobile/finwiki/README.md`
- [x] T020 Run available validation commands and record results in `specs/006-mobile-store-app/evidence.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Stories (Phase 3-6)**: Depend on Foundational. US1, US2, and US4 are P1; US3 is P2.
- **Polish (Phase 7)**: Depends on implemented target stories.

### User Story Dependencies

- **US1**: Requires T004-T007.
- **US2**: Requires T004-T007.
- **US3**: Requires T004-T007.
- **US4**: Requires T004-T007 for account deletion endpoint and store docs.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 starts.
- T007 can run in parallel with backend bridge work after the mobile directory exists.
- US1 and US2 UI work can proceed in parallel after T006.
- T016 and T017 can run in parallel with T015.
- T018 can run in parallel with documentation updates after T004.

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 chat and US2 wiki browse because they define the mobile product.
3. Complete US4 store-readiness documents before any beta submission.
4. Add US3 capture after the core mobile app is stable.

### Boundary Rule

The mobile app and C# gateway must remain transport/UI layers. Python remains the agent runtime and the only place that performs FinWiki reasoning or durable wiki mutation.
