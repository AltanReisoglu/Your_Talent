# FinWiki Mobile Privacy Inventory

Status: draft for beta submission.

This file is the source checklist for Apple App Privacy and Google Play Data
Safety declarations. Update it whenever a mobile SDK, backend log, model
provider, analytics tool, crash reporter, payment provider, or auth provider is
added.

| Data Type | Collected | Linked To User | Shared With Third Parties | Purpose | Processor | Retention / Deletion |
|-----------|-----------|----------------|---------------------------|---------|-----------|----------------------|
| User content: prompts | Yes | Yes for signed-in users; session-scoped for guest users | Model provider may process via backend | App functionality, FinWiki responses | FinWiki backend, model provider | Retained according to backend session policy; deletion request starts account workflow |
| User content: ingest submissions | Yes | Yes | Model provider only if later processed by ingest workflow | User-requested knowledge capture | FinWiki backend | Stored in backend state queue; eligible for deletion/anonymization unless legal/audit hold applies |
| Identifiers: user ID/session ID | Yes | Yes | No direct mobile sharing | Session continuity, abuse prevention | FinWiki backend | Deleted/anonymized through account deletion workflow |
| Diagnostics | Planned, not enabled in MVP scaffold | Depends on SDK | Depends on SDK | Crash/debug support | TBD | Must be declared before SDK is enabled |
| Usage analytics | No in MVP scaffold | N/A | N/A | N/A | N/A | Add a new row before enabling analytics |
| Financial account/brokerage data | No | N/A | N/A | Out of scope | N/A | Must require a separate spec and compliance review |

## Store Mapping Notes

- Apple App Privacy must reflect prompt content, ingest submissions, identifiers,
  diagnostics, and any third-party SDKs actually included in the build.
- Google Play Data Safety must be completed even if a later build collects no
  user data.
- Model/provider processing is server-side. No provider keys are present in the
  mobile app bundle.
- If account creation is enabled, account deletion must be available in-app and
  through a public web path where required.

## Release Blockers

- Do not submit with analytics, crash reporting, auth, or payment SDKs until
  this inventory is updated.
- Do not claim trading, brokerage, lending, crypto custody, money management, or
  personalized investment advice unless licenses and store declarations support
  those claims.
