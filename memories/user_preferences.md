# Default User Preferences

This file is writable memory for local/default user preferences. In deployed
multi-user environments this should become user-scoped memory via a StoreBackend
namespace such as `(rt.server_info.user.identity,)`.

## Response Preferences

- Default language: Turkish, unless the user requests otherwise.
- Prefer concise summaries with concrete file references after implementation.
- For architecture questions, explain tradeoffs before recommending a path.

## Financial Research Preferences

- Emphasize BIST, TCMB, SPK, KAP, and Turkish-market context when relevant.
- For financial analysis, include risks, assumptions, source freshness, and
  "not investment advice" posture.

## Watchlist

- Empty. Add only when the user explicitly asks to remember tickers, sectors,
  markets, or recurring research interests.
