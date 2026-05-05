"""
FinWiki Async Fan-Out Supervisor

Optional DeepAgents/Agent Protocol topology for background fan-out.

Use this when running under a LangGraph/Agent Protocol server with the graphs
registered in langgraph.json. The default CLI entry point still uses
agents.host_agent.agent:get_agent for the simpler sync fan-out workflow.
"""

from functools import lru_cache

from deepagents import AsyncSubAgent, create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from agents.fanout_agent import fanout_synthesizer
from agents.host_agent.agent import ORCHESTRATOR_PROMPT, general_purpose
from agents.ingest_agent import wiki_ingestor
from tools.serverless.tavily_search import internet_search
from tools.serverless.wiki_manager import (
    append_log,
    lint_wiki,
    list_wiki_pages,
    read_source_manifest,
    read_wiki_page,
    register_source,
    search_wiki,
    update_index,
    upsert_wiki_page,
    write_wiki_page,
)

ASYNC_FANOUT_PROMPT = ORCHESTRATOR_PROMPT + """\

## Async Fan-Out Runtime
You are running with DeepAgents `AsyncSubAgent` workers.
For deep research, use this ADK-like shape:

1. Sequential pre-step: decide if fan-out is warranted.
2. Parallel background step: use `start_async_task` for independent read/research
   lanes such as `wiki-querier` and `financial-researcher`.
3. Return control to the user with full task IDs. Do not immediately poll unless
   the user explicitly asked to wait for a completed report in this turn.
4. When the user asks for status or finalization, call `list_async_tasks` or
   `check_async_task` with the full task IDs.
5. Once required tasks are complete, pass their outputs to `fanout-synthesizer`.
6. Call `wiki-ingestor` exactly once after synthesis if the result should persist.

Never truncate task IDs. Task statuses mentioned earlier in the conversation are
stale; always check live status before reporting progress.
"""

async_fanout_subagents = [
    AsyncSubAgent(
        name="wiki-querier",
        description=(
            "Background wiki baseline worker. Reads FinWiki index/pages and "
            "returns existing coverage, stale claims, and missing page targets."
        ),
        graph_id="wiki_querier",
    ),
    AsyncSubAgent(
        name="financial-researcher",
        description=(
            "Background financial research worker. Uses web search for fresh, "
            "source-cited findings. Can be launched multiple times with narrow "
            "lanes such as macro, regulation, sector comps, or valuation."
        ),
        graph_id="financial_researcher",
    ),
]


@lru_cache(maxsize=1)
def get_async_agent():
    """Build the optional async fan-out FinWiki supervisor."""
    checkpointer = MemorySaver()
    return create_deep_agent(
        model="google_genai:gemini-3.1-pro-preview",
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
        ],
        system_prompt=ASYNC_FANOUT_PROMPT,
        subagents=[
            general_purpose,
            *async_fanout_subagents,
            fanout_synthesizer,
            wiki_ingestor,
        ],
        skills=["/skills/"],
        memory=["/AGENTS.md"],
        checkpointer=checkpointer,
        debug=False,
        name="finwiki-async-fanout-orchestrator",
    )


graph = get_async_agent()
