# FinWiki Mobile Release Checklist

## Technical Gates

- [ ] `mobile/finwiki` installs dependencies successfully.
- [ ] `npm run typecheck` passes in `mobile/finwiki`.
- [ ] iOS preview build completes through EAS.
- [ ] Android preview build completes through EAS.
- [ ] Backend `/health` is reachable over HTTPS.
- [ ] Mobile `/invoke` flow returns a FinWiki response.
- [ ] Mobile `/wiki/search` returns seed concepts including DCF and WACC.
- [ ] Mobile `/ingest-submissions` queues a source package without direct wiki writes.
- [ ] Mobile `/account/delete` returns a deletion request status when accounts are enabled.

## Store Policy Gates

- [ ] Privacy policy URL is live.
- [ ] Support URL is live.
- [ ] Apple App Privacy labels match `docs/store/privacy-inventory.md`.
- [ ] Google Play Data Safety matches `docs/store/privacy-inventory.md`.
- [ ] Financial metadata avoids regulated advice/trading/money-management claims.
- [ ] App has financial safety disclaimer in onboarding or first relevant answer.
- [ ] Reviewer notes and guest/test access are ready.
- [ ] Account deletion is in-app and web-accessible if accounts are enabled.

## Beta Gates

- [ ] TestFlight build tested.
- [ ] Google Play internal or closed testing tested.
- [ ] Known backend/model failure states are documented.
- [ ] Remaining residual risk is recorded in feature `evidence.md`.
