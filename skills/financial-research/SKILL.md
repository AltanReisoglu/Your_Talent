# FinWiki Financial Research Skill

## When to use this skill
Use this skill when the user asks about:
- Financial concepts (DCF, WACC, P/E, Beta, Sharpe Ratio...)
- Market instruments (stocks, bonds, ETFs, options, futures, crypto)
- Company analysis (fundamental, technical, valuation)
- Macroeconomic topics (inflation, interest rates, GDP, currency)
- Investment strategies (value investing, momentum, factor investing)
- Turkish markets (BIST, TCMB, SPK regulations)

## Research Workflow
1. **Search** the wiki first with `search_wiki(...)`, then inspect `/wiki/index.md`
2. **Read** existing pages if topic is covered
3. **Research** using `internet_search` with `topic="finance"` when current data is needed
4. **Merge** new findings into existing pages; avoid duplicate pages for naming variants
5. **Write** using `upsert_wiki_page(...)` so page, index, and log update together
6. **Register** sources with `register_source(...)` for URLs or files in `/raw/sources/`
7. **Cross-reference** related pages using [[wikilinks]]

## Quality Standards
- Every factual claim → cite source [Kaynak: URL]
- Every page → minimum 3 cross-references
- Every metric → provide context (e.g., "P/E of 15x vs. sector average 20x")
- Contradictions → explicitly flag with ⚠️
- Raw sources → immutable; never rewrite `/raw/` during ingest
- Reusable answers → persist them as wiki pages when they add durable knowledge

## Turkish Market Specifics
- BIST: Borsa İstanbul (XU100, XU030 indices)
- TCMB: Türkiye Cumhuriyet Merkez Bankası (central bank)
- SPK: Sermaye Piyasası Kurulu (capital markets regulator)
- KAP: Kamuyu Aydınlatma Platformu (disclosure platform)

## Output Format
Always return:
1. Direct answer to user's question
2. Reference to wiki page created/updated
3. Related topics the user might want to explore
