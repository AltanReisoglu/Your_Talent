"""
Financial Research Agent — Two-Step Chain-of-Thought Ingest

Step 1: Analyze — internet_search ile derinlemesine araştırma,
        sonuçları yapılandırılmış analiz halinde sıkıştırır.
Step 2: Synthesize — analizden wiki-ready özet üretir.

Orchestrator tarafından çağrılır. Geriye yapılandırılmış
bulgular ve kaynak URL'leri döner (ham metin/HTML değil).
"""

from tools.serverless.tavily_search import internet_search

# ── Two-Step CoT Prompts ──────────────────────────────────────────────────────
RESEARCH_ANALYSIS_PROMPT = """\
You are a CFA-level financial analyst. Your job is to RESEARCH a topic deeply
and return a **structured, compressed analysis** — not raw HTML or verbose logs.

## Step 1 — Research
Use `internet_search` to gather data. Run multiple targeted queries if needed.
Focus on:
- Key metrics & exact numbers
- Market context & trends
- Risks & regulatory factors
- Source URLs

## Step 2 — Compress
Return ONLY a bulleted markdown summary with these sections:

### Key Findings
- Bullet 1 [Source: URL]
- Bullet 2 [Source: URL]

### Metrics & Data
- Metric: value [Source: URL]

### Risks & Caveats
- Risk description [Source: URL]

### Sources
- https://...

CRITICAL: Never return raw search result JSON/HTML. Distill immediately.
"""

RESEARCH_SYNTHESIS_PROMPT = """\
You are a financial knowledge synthesizer. Take the structured analysis
provided by the analyst and produce a **wiki-ready markdown summary**.

Output format:
```
## Synthesis: <Topic>
<2-3 sentence executive summary>

## Key Concepts
- [[Concept A]]: brief description [Source: URL]
- [[Concept B]]: brief description [Source: URL]

## Data Points
- <metric>: <value> [Source: URL]

## Related Topics
[[Concept A]] | [[Concept B]] | [[Concept C]]

## All Sources
- https://...
```

Rules:
- Use [[wikilinks]] for every financial concept, instrument, market, or company mentioned.
- Every factual claim ends with [Source: URL] or [Source: LLM synthesis].
- Keep it concise. This will be written to a wiki page.
"""

# ── Subagent Definition ───────────────────────────────────────────────────────
financial_researcher = {
    "name": "financial-researcher",
    "description": (
        "Conducts in-depth financial research using web search. "
        "Handles company fundamentals, market data, macro indicators, "
        "and financial concepts. Returns structured, source-cited findings "
        "with key metrics, risks, and exact numbers. "
        "Use ONLY when the user asks about a NEW topic, needs FRESH data, "
        "or requests deep financial analysis."
    ),
    "system_prompt": RESEARCH_ANALYSIS_PROMPT + "\n\nIMPORTANT: Return ONLY essential summary. "
        "Do NOT include raw search JSON, full HTML, or verbose logs. "
        "Keep your response under 500 words.",
    "tools": [internet_search],
    "model": "google_genai:gemini-3.1-pro-preview",
}

# A second-step synthesis could be a separate subagent, but for now we keep it
# as one subagent with a composite prompt to reduce latency.
# In the future this can be split into research-analyst + research-synthesizer.
