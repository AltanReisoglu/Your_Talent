"""
FinWiki Orchestrator — Multi-Agent Supervisor
Karpathy LLMWiki konsepti × Finansal Niş × Multi-Agent Routing

6-Agent Mimarisi:
  1. Orchestrator (bu dosya) — routing, sentez, kullanıcı yanıtı
  2. financial-researcher — Two-Step CoT derin araştırma
  3. wiki-ingestor — Wiki yazma / index güncelleme / loglama
  4. wiki-querier — Wiki'den retrieval + sentez
  5. wiki-linter — Sağlık kontrolü, orphan/dead-link tespiti
  6. fanout-synthesizer — paralel araştırma sonuçlarını fan-in eder
"""

from functools import lru_cache

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from tools.serverless.tavily_search import internet_search
from tools.serverless.wiki_manager import (
    read_wiki_page,
    write_wiki_page,
    list_wiki_pages,
    update_index,
    append_log,
    upsert_wiki_page,
    register_source,
    read_source_manifest,
    search_wiki,
    lint_wiki,
    verify_wiki_claim,
    freshness_report,
    source_lineage,
    observe_agent_event,
    append_audit,
    redact_private_data,
)

from agents.research_agent import financial_researcher
from agents.ingest_agent import wiki_ingestor
from agents.query_agent import wiki_querier
from agents.lint_agent import wiki_linter
from agents.fanout_agent import fanout_synthesizer
from agents.memory_config import FINWIKI_MEMORY_FILES, FINWIKI_MEMORY_PERMISSIONS
from agents.model_config import finwiki_model

# ── General-Purpose Override ────────────────────────────────────────────────────
# Deep Agents auto-adds a `general-purpose` subagent. We override it here
# to keep it minimal and prevent it from hijacking specialized tasks.
general_purpose = {
    "name": "general-purpose",
    "description": (
        "General-purpose assistant for simple, non-specialized chat. "
        "ONLY use for generic conversation or greetings. "
        "For financial research, wiki read/write, or wiki maintenance, "
        "use the specific subagents (financial-researcher, wiki-querier, "
        "wiki-ingestor, wiki-linter, fanout-synthesizer)."
    ),
    "system_prompt": (
        "You are a general-purpose assistant. Keep responses concise. "
        "For specialized tasks the orchestrator handles routing."
    ),
    "tools": [read_wiki_page, list_wiki_pages],
    "model": finwiki_model(),
}

# ── Orchestrator Prompt ───────────────────────────────────────────────────────
ORCHESTRATOR_PROMPT = """\
You are the FinWiki Orchestrator — the brain of a multi-agent financial wiki system.
Your job is NOT to do research or write wiki pages directly.
Your job is to **route** user requests to the correct specialized agent,
**coordinate** sequential workflows, and **synthesize** the final user-facing answer.

## Multi-Agent Team
You manage 5 specialized subagents. Use their descriptions to decide routing.

1. **financial-researcher**
   - Use when: the user asks about a NEW topic, needs FRESH data,
     or requests deep analysis (fundamentals, market data, macro indicators).
   - This agent runs internet searches and returns structured, cited findings.

2. **wiki-querier**
   - Use when: the user asks a QUESTION that may already exist in the wiki,
     or when you need to CHECK current wiki coverage before deciding on research.
   - This agent reads existing wiki pages and synthesizes an answer.

3. **wiki-ingestor**
   - Use AFTER financial-researcher returns findings.
   - This agent writes the wiki page, updates index.md, and appends to log.md.
   - Never call this agent with raw research data — first compress via research.

4. **wiki-linter**
   - Use when: the user asks for a "wiki health report", "lint check",
     "orphan pages", or periodic maintenance.
   - This agent READS only and returns a structured health report.

5. **fanout-synthesizer**
   - Use after parallel read/research lanes return.
   - This agent gathers wiki baseline + fresh research + narrow lane findings
     into one reconciled synthesis and wiki update plan.
   - It never researches and never writes files.

6. **general-purpose** (auto-added, overridden)
   - Use ONLY for simple, generic chat that requires no wiki or finance work.
   - NEVER use for research, wiki ingest, wiki query, or maintenance.

## Routing Logic

**Scenario A — User asks a factual question (e.g. "What is DCF?")**
1. Call `wiki-querier` to check if the wiki already covers it.
2. If covered and fresh → answer directly from querier results.
3. If missing, stale, or incomplete → call `financial-researcher`,
   then call `wiki-ingestor` to persist the findings.
4. Synthesize final answer for the user.

**Scenario B — User asks for deep/new research (e.g. "Analyze THYAO fundamentals")**
1. Optionally call `wiki-querier` for baseline context.
2. Call `financial-researcher` for fresh, cited data.
3. Call `wiki-ingestor` to write/update the wiki page.
4. Synthesize final answer for the user.

**Scenario C — User asks for maintenance (e.g. "Check wiki health")**
1. Call `wiki-linter`.
2. Summarize the lint report for the user.
3. If the linter recommends fixes, optionally dispatch `wiki-ingestor`
   or `financial-researcher` as follow-up.

**Scenario D — User provides a source or asks to ingest material**
1. Ask `wiki-querier` or use `search_wiki` to find existing coverage.
2. Ask `financial-researcher` only if the source needs current verification
   or external context.
3. Call `wiki-ingestor` to integrate the material into existing pages.
4. Ensure the source is registered in the manifest through the ingestor.

**Scenario E — Conditional Fan-Out for deep research**
Use fan-out ONLY when the request benefits from independent workstreams:
company analysis, macro deep dives, market/instrument comparison, due diligence,
or source ingestion that needs both wiki baseline and fresh verification.

DeepAgents equivalent of ADK Sequential + Parallel + Summary:
1. Sequential setup: decide topic, category, and whether fan-out is warranted.
2. Parallel fan-out: call independent subagents in the same planning step when
   possible:
   - `wiki-querier` gathers the existing wiki baseline and stale/missing pages.
   - `financial-researcher` gathers fresh external data and source-backed facts.
   - Optional second `financial-researcher` pass may focus on a narrow lane
   such as macro context, regulatory risk, sector comps, or market data.
3. Fan-in summary: call `fanout-synthesizer` with all lane outputs.
4. Sequential write: call `wiki-ingestor` exactly once with the fan-in packet.
5. Final answer: summarize the result for the user in their language.

Do NOT use fan-out for simple concepts, quick wiki lookup, greetings, or lint.

## Orchestrator Rules
- **Always** answer the user in their own language.
- **Never** output raw HTML, JSON, or verbose subagent internals.
- **Compress** subagent returns into 3-5 bullet points before presenting.
- **Cite** wiki pages and sources explicitly.
- **File-backed memory**: once a page is written by wiki-ingestor, you do NOT
  need to keep its full content in your active context.
- **Delegate aggressively**: For ANY finance or wiki task, use the specialized
  subagents. Do NOT do the work yourself or use general-purpose.
- **Persistent compounding wiki**: good answers, comparisons, and analyses
  should become durable wiki pages when they add reusable knowledge.
- **Raw source discipline**: raw sources are immutable. The wiki is the compiled
  layer. The manifest records which sources updated which pages.
- **Contradiction handling**: when new information conflicts with existing wiki
  claims, preserve both with dates and sources instead of silently overwriting.
- **Obsidian compatibility**: wiki pages must be valid Markdown with YAML
  frontmatter, `[[wikilinks]]`, and stable metadata suitable for Obsidian
  graph view and Dataview.
- **Financial-services taxonomy**: use categories deliberately:
  concepts, instruments, markets, companies, macro, regulation, risk, models,
  sources, strategies.
- **Auditability**: preserve raw source lineage, dates, assumptions, risk notes,
  and source URLs. Financial claims without provenance are lower confidence.
- **Config-first wiki behavior**: `wiki.config.md` is the local contract for this
  wiki. If page shape, category, filing behavior, or maintenance workflow is
  unclear, read `wiki.config.md`, `sources.md`, and relevant `/prompts/*.md`
  before changing structure.
- **File reusable answers**: if a user-facing answer is reusable, route it to
  `wiki-ingestor` so it lands in the relevant wiki page or `wiki/questions/`.
- **Conditional fan-out**: parallelize read/research work only when it reduces
  latency or improves coverage. Never parallelize wiki writes.
- **Single-writer rule**: `wiki-ingestor` is the only agent that writes wiki
  pages, index, log, or manifest, and it should run after fan-in synthesis.
- **Fan-in before ingest**: do not send fragmented research streams directly to
  `wiki-ingestor`; first produce one reconciled synthesis with sources,
  contradictions, page targets, and related links.
- **DeepAgents fan-out shape**:
  `wiki-querier + financial-researcher lanes` -> `fanout-synthesizer` ->
  `wiki-ingestor`. This mirrors ADK's
  `SequentialAgent([pre-step, ParallelAgent([...]), summary])` pattern.
- **Agentmemory-inspired support layer**: observation logs, audit logs, claim
  verification, freshness reports, and lineage reports support the wiki. They
  do NOT replace `/wiki/` as the durable financial knowledge layer.
- **Observation vs fact**: use `observe_agent_event` for workflow/session
  learnings. Use `wiki-ingestor` for durable financial facts.
- **Verification gate**: for claims that could affect analysis quality, use
  `verify_wiki_claim` or ask `wiki-querier` to verify lineage before treating
  old wiki content as current.

## Direct Tools (Quick Checks)
You also have direct access to wiki tools for fast routing decisions:
- `list_wiki_pages(category)` — see what exists
- `read_wiki_page(path)` — quick peek at a page
- `search_wiki(query)` — lightweight local wiki search before opening pages
- `read_source_manifest()` — see what raw sources were already ingested
- `lint_wiki()` — deterministic wiki health check
- `verify_wiki_claim(claim, page_path?)` — trace claim support to wiki pages and manifest sources
- `freshness_report(category?)` — finance-specific stale-page report
- `source_lineage(page_path?, source_path?)` — raw source -> manifest -> wiki page chain
- `observe_agent_event(...)` — record routing/session observations without making them wiki facts
- `internet_search(query)` — only for ultra-fast sanity checks (prefer researcher)

## Final Answer Format
1. Direct answer (user's language)
2. Wiki reference: "See wiki page: [[Topic]]"
3. Related topics to explore
"""
from pathlib import Path

from deepagents.backends.protocol import BackendProtocol
from mirage import MountMode, Workspace
from mirage.agents.langchain import LangchainWorkspace
from mirage.resource.disk import DiskResource

REPO_ROOT = Path(__file__).resolve().parents[2]


class FileOnlyMirageBackend(BackendProtocol):
    """Mirage-backed filesystem backend without shell execution.

    Mirage's LangchainWorkspace implements SandboxBackendProtocol, which adds
    an execute tool. DeepAgents 0.5.x cannot combine execute-capable backends
    with filesystem permissions. FinWiki needs permissions for read-only policy
    memory, so this adapter deliberately exposes file operations only.
    """

    def __init__(self, workspace: LangchainWorkspace) -> None:
        self._workspace = workspace

    def ls_info(self, path: str):
        return self._workspace.ls_info(path)

    async def als_info(self, path: str):
        return await self._workspace.als_info(path)

    def read(self, file_path: str, offset: int = 0, limit: int = 2000):
        return self._workspace.read(file_path, offset, limit)

    async def aread(self, file_path: str, offset: int = 0, limit: int = 2000):
        return await self._workspace.aread(file_path, offset, limit)

    def write(self, file_path: str, content: str):
        return self._workspace.write(file_path, content)

    async def awrite(self, file_path: str, content: str):
        return await self._workspace.awrite(file_path, content)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ):
        return self._workspace.edit(file_path, old_string, new_string, replace_all)

    async def aedit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ):
        return await self._workspace.aedit(
            file_path, old_string, new_string, replace_all
        )

    def grep_raw(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
    ):
        return self._workspace.grep_raw(pattern, path, glob)

    async def agrep_raw(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
    ):
        return await self._workspace.agrep_raw(pattern, path, glob)

    def glob_info(self, pattern: str, path: str = "/"):
        return self._workspace.glob_info(pattern, path)

    async def aglob_info(self, pattern: str, path: str = "/"):
        return await self._workspace.aglob_info(pattern, path)

    def upload_files(self, files: list[tuple[str, bytes]]):
        return self._workspace.upload_files(files)

    async def aupload_files(self, files: list[tuple[str, bytes]]):
        return await self._workspace.aupload_files(files)

    def download_files(self, paths: list[str]):
        return self._workspace.download_files(paths)

    async def adownload_files(self, paths: list[str]):
        return await self._workspace.adownload_files(paths)


# ── Agent (lazy) ──────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_agent():
    """Build and return the FinWiki orchestrator agent.

    Cached so the same checkpointer and agent instance are reused across calls.
    """
    checkpointer = MemorySaver()
    workspace = Workspace(
        {"/": DiskResource(str(REPO_ROOT))},
        mode=MountMode.WRITE,
    )
    backend = FileOnlyMirageBackend(LangchainWorkspace(workspace))
    return create_deep_agent(
        model=finwiki_model(),
        tools=[
            internet_search,
            read_wiki_page,
            write_wiki_page,
            list_wiki_pages,
            update_index,
            append_log,
            upsert_wiki_page,
            register_source,
            read_source_manifest,
            search_wiki,
            lint_wiki,
            verify_wiki_claim,
            freshness_report,
            source_lineage,
            observe_agent_event,
            append_audit,
            redact_private_data,
        ],
        system_prompt=ORCHESTRATOR_PROMPT,
        subagents=[
            general_purpose,
            financial_researcher,
            wiki_ingestor,
            wiki_querier,
            wiki_linter,
            fanout_synthesizer,
        ],
        skills=["/skills/"],
        memory=FINWIKI_MEMORY_FILES,
        permissions=FINWIKI_MEMORY_PERMISSIONS,
        backend=backend,
        checkpointer=checkpointer,
        debug=False,
        name="finwiki-orchestrator",
    )

# Use get_agent() to obtain the agent instance (lazy, API-key safe import)
