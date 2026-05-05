"""
FinWiki — Main Entry Point

Kullanım:
  uv run main.py                    # Interactive mod
  uv run main.py "BIST 100 nedir"   # Tek soru
"""

import os
import sys
from agents.host_agent.agent import get_agent

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
            print(msg.content)
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
