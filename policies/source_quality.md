# Source Quality Policy

This is read-only organization-level memory. The agent may reference it but
must not edit it.

## Source Hierarchy

1. Primary official sources: regulators, central banks, exchanges, company
   filings, audited reports, KAP/SEC/EDGAR-style disclosures.
2. Reputable data providers and financial institutions with methodology notes.
3. Established financial media for news context and event chronology.
4. Academic papers and technical reports for models and frameworks.
5. LLM synthesis only for conceptual glue, never for market data or regulated
   claims.

## Financial Claim Rules

- Prices, rates, yields, market caps, inflation, GDP, financial statements, and
  regulatory rules are time-sensitive; verify freshness before presenting them.
- Distinguish reported facts from forecasts, estimates, model outputs, and
  management guidance.
- For conflicting sources, preserve the conflict with dates and citations.

## Wiki Ingest Rules

- Raw source -> manifest -> wiki page -> user answer lineage should be
  recoverable.
- Source profiles and recurring datasets belong in `/wiki/sources/`.
- Risk, regulation, and model assumptions should become separate pages when
  they are reusable across analyses.
