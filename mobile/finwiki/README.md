# FinWiki Mobile

FinWiki Mobile is the App Store / Google Play client for the FinWiki agent
platform. It is intentionally a thin client:

- Chat and wiki browsing call the hosted FinWiki backend.
- Python remains the agent runtime.
- C# or another API gateway remains transport/BFF.
- Model/provider keys are never shipped in the mobile bundle.
- Durable wiki writes and ingest decisions stay server-side.

## Local Setup

Start the local FinWiki gateway from the repository root:

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Then start the Expo client:

```bash
cd mobile/finwiki
npm install
cp .env.example .env
# edit .env for local browser/simulator testing:
# EXPO_PUBLIC_FINWIKI_API_BASE_URL=http://127.0.0.1:8000
npx expo start --localhost --port 8081
```

Open the web preview at:

```text
http://localhost:8081
```

For a physical iOS/Android device, do not use `127.0.0.1`; that points to the
phone itself. Set `EXPO_PUBLIC_FINWIKI_API_BASE_URL` to a reachable LAN address
or secure tunnel URL, then restart Expo.

## Required Backend Endpoints

- `POST /invoke`
- `GET /wiki/search?q=DCF`
- `GET /wiki/page?path=concepts/discounted-cash-flow-dcf.md`
- `POST /ingest-submissions`
- `POST /account/delete`

The local C# gateway enables CORS for Expo web on `localhost:8081` and
`127.0.0.1:8081` by default. Override with `FINWIKI_ALLOWED_ORIGINS` when using
a different local or hosted client origin.

## Validation

```bash
cd mobile/finwiki
npm run typecheck
```

From the repository root:

```bash
dotnet build dotnet-api/FinWiki.Api.csproj
.venv/bin/python -m pytest tests/test_wiki_api_bridge.py
```

Chat requests call the live model provider configured in the backend `.env`.
If the provider quota or token is unavailable, use the Wiki tab and
`/wiki/search` endpoint to validate the mobile/backend connection without a
model call.

## Troubleshooting

- If Expo shows an Expo Router warning, confirm the shell entrypoint is under
  `src/shell/`, not `src/app/`.
- If the browser reports CORS errors, run the C# gateway and confirm the client
  origin is included in `FINWIKI_ALLOWED_ORIGINS`.
- If a physical phone cannot reach the backend, replace `127.0.0.1` with the
  computer LAN IP or a tunnel URL and restart Expo.

## Store Release Notes

Before TestFlight or Google Play testing, review:

- `docs/store/privacy-inventory.md`
- `docs/store/app-store-connect.md`
- `docs/store/google-play-console.md`
- `docs/store/release-checklist.md`

Do not add analytics, crash reporting, auth, payment, trading, brokerage,
lending, crypto, or personalized investment features without updating the Spec
Kit artefacts and privacy inventory first.
