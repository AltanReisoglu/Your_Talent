"""
Agent Protocol graph for the async wiki-querier worker.
"""

from deepagents import create_deep_agent

from agents.query_agent import QUERY_SYSTEM_PROMPT
from tools.serverless.wiki_manager import list_wiki_pages, read_wiki_page, search_wiki

graph = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    tools=[read_wiki_page, list_wiki_pages, search_wiki],
    system_prompt=QUERY_SYSTEM_PROMPT + "\n\nReturn wiki baseline, stale claims, and missing targets.",
    name="wiki-querier",
)
