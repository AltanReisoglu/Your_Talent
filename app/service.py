import os
from typing import Any


def load_local_env(path: str = ".env") -> None:
    """Load KEY=VALUE pairs from a local .env file without extra dependencies."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def message_text(content: Any) -> str:
    """Normalize LangChain message content into printable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(part for part in parts if part)
    return str(content)


def build_thread_id(user_id: str, session_id: str) -> str:
    return f"finwiki:{user_id}:{session_id}"


def invoke_agent(message: str, user_id: str, session_id: str) -> dict[str, str]:
    load_local_env()

    from agents.host_agent.agent import get_agent

    thread_id = build_thread_id(user_id, session_id)
    agent = get_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": thread_id}},
    )

    response_text = ""
    for msg in reversed(result.get("messages", [])):
        if getattr(msg, "type", None) == "ai" and hasattr(msg, "content"):
            response_text = message_text(msg.content)
            break

    return {
        "user_id": user_id,
        "session_id": session_id,
        "thread_id": thread_id,
        "response": response_text,
    }

