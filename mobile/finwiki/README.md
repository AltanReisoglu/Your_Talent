# FinWiki Mobile

FinWiki Mobile is the App Store / Google Play client for the FinWiki agent
platform. It is intentionally a thin client:

- Chat and wiki browsing call the hosted FinWiki backend.
- Python remains the agent runtime.
- C# or another API gateway remains transport/BFF.
- Model/provider keys are never shipped in the mobile bundle.
- Durable wiki writes and ingest decisions stay server-side.

## Local Setup

```bash
cd mobile/finwiki
npm install
cp .env.example .env
npm run start
```

Set `EXPO_PUBLIC_FINWIKI_API_BASE_URL` to a reachable backend. Device testing
cannot use `localhost` unless the backend is reachable from the device through a
LAN address, simulator mapping, or secure tunnel.

## Required Backend Endpoints

- `POST /invoke`
- `GET /wiki/search?q=DCF`
- `GET /wiki/page?path=concepts/discounted-cash-flow-dcf.md`
- `POST /ingest-submissions`
- `POST /account/delete`

## Store Release Notes

Before TestFlight or Google Play testing, review:

- `docs/store/privacy-inventory.md`
- `docs/store/app-store-connect.md`
- `docs/store/google-play-console.md`
- `docs/store/release-checklist.md`

Do not add analytics, crash reporting, auth, payment, trading, brokerage,
lending, crypto, or personalized investment features without updating the Spec
Kit artefacts and privacy inventory first.
