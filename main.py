"""
FinWiki — Main Entry Point

Kullanım:
  uv run main.py                    # Interactive mod
  uv run main.py "BIST 100 nedir"   # Tek soru
"""

import os
import sys


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


load_local_env()

from agents.host_agent.agent import get_agent


def message_text(content) -> str:
    """Normalize LangChain message content into printable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(part for part in parts if part)
    return str(content)

def run(query: str, thread_id: str = "finwiki-default"):
    agent = get_agent()
    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": query}]
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    # Son AI mesajını yazdır
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.type == "ai":
            print(message_text(msg.content))
            break

def interactive():
    print("🏦 FinWiki — Finansal Bilgi Ajansı")
    print("Çıkmak için 'exit' yaz\n")
    thread_id = "finwiki-session-1"
    while True:
        try:
            query = input("Soru > ").strip()
            if query.lower() in ("exit", "quit", "q"):
                break
            if not query:
                continue
            run(query, thread_id)
            print()
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(" ".join(sys.argv[1:]))
    else:
        interactive()
