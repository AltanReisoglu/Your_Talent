# Feature Specification: FinWiki Mobile Store App

**Feature Branch**: `006-mobile-store-app`

**Created**: 2026-05-25

**Status**: Draft

**Input**: User description: "Publish this FinWiki system on the Apple App Store and Google Play by building a mobile app."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use FinWiki From A Mobile App (Priority: P1)

A mobile user can install the FinWiki app, ask finance and knowledge-base questions, receive source-aware educational answers, and continue a session from their phone.

**Why this priority**: This is the core store product. Without a mobile chat/query surface, there is no App Store or Google Play app to publish.

**Independent Test**: Install a development build on iOS and Android, sign in or start a guest session, submit "DCF nedir?", and receive a FinWiki answer through the production-like HTTPS gateway.

**Acceptance Scenarios**:

1. **Given** the mobile app is installed and the backend is reachable, **When** the user submits a question, **Then** the app displays the FinWiki response, source hints, and hook/error status when relevant.
2. **Given** the backend is unavailable, **When** the user submits a question, **Then** the app shows a recoverable error without losing the draft prompt.
3. **Given** the answer contains financial content, **When** the app displays it, **Then** the app frames the response as education/research and avoids personalized buy/sell advice.

---

### User Story 2 - Browse And Reuse The Knowledge Base (Priority: P1)

A mobile user can browse/search key FinWiki knowledge pages and reuse the compiled wiki without needing Obsidian or a desktop repo.

**Why this priority**: The product is not just a chatbot; the durable value is the financial LLM wiki and its source-aware knowledge base.

**Independent Test**: Open the mobile knowledge tab, search "DCF", open the DCF page, and navigate related concepts.

**Acceptance Scenarios**:

1. **Given** the app has access to the backend knowledge index, **When** the user searches a concept, **Then** the app shows matching wiki pages with title, summary, freshness, and related topics.
2. **Given** a wiki page has sources or related pages, **When** the user opens it, **Then** the app renders source/freshness indicators and related navigation.

---

### User Story 3 - Capture Notes And Request Ingest (Priority: P2)

A mobile user can capture a note, URL, or short source excerpt and ask FinWiki to ingest or file it into the durable wiki.

**Why this priority**: Mobile capture makes the system useful outside the desktop workflow, but durable ingest must still go through the existing agent runtime and single-writer path.

**Independent Test**: Save a short note from mobile, request ingest, and verify the backend returns an ingest status or planned wiki update without the mobile app writing wiki files directly.

**Acceptance Scenarios**:

1. **Given** the user enters a note or URL, **When** they request ingest, **Then** the app sends the source package to the backend and shows queued/running/completed status.
2. **Given** ingest fails or is blocked by policy, **When** the backend returns an error, **Then** the app shows the reason and does not retry silently.

---

### User Story 4 - Meet Store Review And Privacy Requirements (Priority: P1)

An operator can submit the app to App Store Connect and Play Console with privacy, financial-safety, testing, and account-deletion requirements satisfied.

**Why this priority**: Store compliance is a release blocker. A technically working app that fails review is not shippable.

**Independent Test**: Complete a release-readiness checklist containing privacy labels, data safety, financial-services declarations, account deletion, review notes, test credentials, screenshots, and beta testing evidence.

**Acceptance Scenarios**:

1. **Given** the app collects account or prompt data, **When** the operator prepares store submission, **Then** privacy labels/data safety forms accurately reflect app and third-party processing.
2. **Given** the app supports account creation, **When** the user opens account settings, **Then** they can initiate account deletion and access a web deletion path where required.
3. **Given** the app is positioned as a financial knowledge assistant, **When** store metadata is reviewed, **Then** it avoids claims of trading, money management, regulated advice, or guaranteed outcomes unless licenses and declarations support those claims.

---

### Edge Cases

- Store reviewers need demo credentials or a reviewer-accessible guest mode.
- A model provider returns unsafe, personalized, or stale financial advice.
- A user asks for trading execution, brokerage, lending, crypto wallet, or regulated money-management actions.
- The user requests deletion while audit logs must be retained for legal/security reasons.
- A new Google Play personal developer account requires closed testing before production access.
- App Store/Google Play privacy declarations diverge from actual SDK/backend behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a cross-platform mobile app target for iOS and Android store distribution.
- **FR-002**: Mobile app MUST call a production HTTPS FinWiki backend and MUST NOT run Python, DeepAgents, local Obsidian vault mutation, or model keys on-device.
- **FR-003**: Backend/mobile contract MUST preserve the existing runtime boundary: mobile client is UI, C# or API gateway is transport, Python owns agent reasoning and wiki mutation.
- **FR-004**: Mobile app MUST support chat/query with session identity and recoverable network errors.
- **FR-005**: Mobile app MUST support knowledge search/browse for compiled wiki pages.
- **FR-006**: Mobile app MUST support note/URL capture for backend-managed ingest.
- **FR-007**: System MUST include financial-safety UX: educational framing, no personalized investment advice, source/freshness indicators, and explicit risk/disclaimer copy.
- **FR-008**: System MUST provide account deletion from the app if account creation exists, plus a web deletion path where store policy requires it.
- **FR-009**: System MUST maintain a privacy inventory for all collected/shared data and third-party SDKs before store submission.
- **FR-010**: System MUST produce App Store and Google Play release artefacts: app icons, screenshots, descriptions, privacy policy URL, support URL, reviewer notes, test credentials, age/content rating inputs, and financial declarations.
- **FR-011**: System MUST support beta distribution: TestFlight for iOS and internal/closed testing tracks for Android.
- **FR-012**: System MUST avoid store metadata that claims licensed financial trading, investing, money management, lending, crypto custody, or personalized advisory capability unless the operator supplies jurisdiction-specific licenses and compliance approvals.

### Key Entities *(include if feature involves data)*

- **MobileUser**: Account or guest identity used for sessions, deletion, and data export.
- **MobileSession**: Conversation context scoped to a user/device/session.
- **ChatMessage**: User prompt and assistant response metadata.
- **WikiPageSummary**: Mobile-safe view of a compiled wiki page.
- **IngestSubmission**: User-provided note, URL, or excerpt sent to backend ingest workflow.
- **PrivacyInventoryItem**: Data type, purpose, linkage, sharing, retention, and SDK owner.
- **StoreSubmissionPackage**: Platform-specific metadata, screenshots, declarations, review notes, and build identifiers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: iOS and Android development builds can submit a prompt and receive a FinWiki response through HTTPS backend.
- **SC-002**: Knowledge search returns relevant wiki pages for at least 5 seed concepts including DCF, WACC, FCF, Terminal Value, and risk.
- **SC-003**: Store readiness checklist has no unresolved blocker before beta submission.
- **SC-004**: Privacy inventory maps every mobile SDK/backend data flow to Apple App Privacy and Google Play Data Safety declarations.
- **SC-005**: Account deletion path is available in-app and as a web link if accounts are enabled.
- **SC-006**: App metadata and in-app copy pass a financial-safety review for no personalized investment advice or regulated-service claims.

## Assumptions

- MVP is a mobile companion for research/education and knowledge management, not a broker, lender, wallet, robo-advisor, or money-management service.
- A hosted FinWiki backend will be available before public store release; mobile apps cannot call `localhost` in production.
- Monetization is out of scope for the first plan. If subscriptions are added later, Apple/Google billing rules will require a separate spec.
- The operator will provide legal entity, privacy policy, support URL, developer accounts, screenshots, and jurisdiction decisions before submission.
