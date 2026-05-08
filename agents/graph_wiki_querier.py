"""
Agent Protocol graph for the async wiki-querier worker.
"""

from deepagents import create_deep_agent

from agents.query_agent import QUERY_SYSTEM_PROMPT
from agents.model_config import finwiki_model
from tools.serverless.wiki_manager import list_wiki_pages, read_wiki_page, search_wiki

graph = create_deep_agent(
    model=finwiki_model(),
    tools=[read_wiki_page, list_wiki_pages, search_wiki],
    system_prompt=QUERY_SYSTEM_PROMPT + "\n\nReturn wiki baseline, stale claims, and missing targets.",
    name="wiki-querier",
)
