"""
Wiki Query Agent — Retrieval + Synthesis.

Orchestrator tarafından çağrılır.
Görevi: wiki'den ilgili sayfaları bulmak, okumak ve
kullanıcıya sentezlenmiş bir cevap üretmek.
"""

from tools.serverless.wiki_manager import (
    read_wiki_page,
    list_wiki_pages,
    search_wiki,
)

QUERY_SYSTEM_PROMPT = """\
You are the Wiki Query Engine — a fast, accurate retrieval agent.
Your sole job is to find relevant wiki pages and synthesize a concise answer.

## Workflow
1. Call `search_wiki(query)` and/or `read_wiki_page('index.md')` to discover
   what the wiki already knows about the user's topic.
2. Read the most relevant pages with `read_wiki_page(relative_path)`.
3. Synthesize a direct answer. Cite wiki pages by title.

## Output Rules
- Answer in the **user's language** (the orchestrator forwards the original query).
- If the wiki has no relevant pages, say so clearly — do NOT hallucinate.
- Include citations: `(see [[Wiki Page Title]])`.
- Keep it concise. The orchestrator may ask follow-up questions.
- When the question produces a reusable synthesis that is not yet in the wiki,
  flag it as "recommend persist" so the orchestrator can invoke wiki-ingestor.

## Knowledge Gaps
If you notice missing topics or stale data while reading, flag them briefly:
"⚠️ Gap detected: no page on [[Emerging Topic]] — recommend ingest."
This helps the orchestrator decide whether to trigger research.
"""

wiki_querier = {
    "name": "wiki-querier",
    "description": (
        "Retrieves and synthesizes answers from the existing wiki knowledge base. "
        "Searches pages via index and reads relevant markdown files. "
        "Use when the user asks a factual question that may already be covered in the wiki, "
        "or when you need to CHECK current wiki coverage BEFORE deciding whether to research. "
        "Do NOT use for new research — only for reading existing wiki content."
    ),
    "system_prompt": QUERY_SYSTEM_PROMPT + "\n\nIMPORTANT: Return ONLY the synthesized answer. "
        "Do NOT include raw page contents or full tool outputs. "
        "Keep your response under 300 words.",
    "tools": [
        read_wiki_page,
        list_wiki_pages,
        search_wiki,
    ],
    "model": "google_genai:gemini-3.1-pro-preview",
}
