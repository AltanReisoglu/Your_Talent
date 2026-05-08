"""
Agent Protocol graph for the async financial-researcher worker.
"""

from deepagents import create_deep_agent

from agents.model_config import finwiki_model
from agents.research_agent import RESEARCH_ANALYSIS_PROMPT
from tools.serverless.tavily_search import internet_search

graph = create_deep_agent(
    model=finwiki_model(),
    tools=[internet_search],
    system_prompt=RESEARCH_ANALYSIS_PROMPT + "\n\nReturn concise, source-cited findings only.",
    name="financial-researcher",
)
