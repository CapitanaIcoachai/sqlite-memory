"""
A local chat loop that REMEMBERS — across restarts.

Run it once, tell it a few facts about yourself, quit. Run it again and ask
about them: the answers persist because they live in `memory.db`.

    ollama pull nomic-embed-text
    ollama pull qwen2.5:7b
    python example_chat.py
"""

import json
import os
import urllib.request

from sqlite_memory import Memory, OLLAMA_URL

CHAT_MODEL = os.environ.get("CHAT_MODEL", "qwen2.5:7b")


def chat(messages):
    body = json.dumps(
        {"model": CHAT_MODEL, "messages": messages, "stream": False}
    ).encode()
    req = urllib.request.Request(
        OLLAMA_URL + "/api/chat", body, {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["message"]["content"].strip()


def main():
    mem = Memory("memory.db")
    print(f"sqlite-memory chat — {mem.count()} memories on disk. Type 'quit' to exit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user or user.lower() in {"quit", "exit"}:
            break

        # 1) recall relevant long-term memories and build the context
        hits = mem.recall(user, k=5, min_score=0.4)
        memory_block = "\n".join(f"- {h['text']}" for h in hits)
        system = (
            "You are a helpful assistant with long-term memory.\n"
            "Relevant things you remember about this user:\n"
            + (memory_block or "(nothing relevant yet)")
        )

        reply = chat(
            [{"role": "system", "content": system},
             {"role": "user", "content": user}]
        )
        print("bot>", reply, "\n")

        # 2) persist this exchange so it can be recalled later
        mem.remember(user, role="user")
        mem.remember(reply, role="assistant")


if __name__ == "__main__":
    main()
