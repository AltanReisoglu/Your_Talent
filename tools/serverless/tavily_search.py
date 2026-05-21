import os
from typing import Literal
from tavily import TavilyClient

from app.hooks import hooked_tool

def _get_tavily_client() -> TavilyClient:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError(
            "TAVILY_API_KEY environment variable is not set. "
            "Please export it before running the agent."
        )
    return TavilyClient(api_key=key)

@hooked_tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search via Tavily."""
    client = _get_tavily_client()
    return client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
