# sqlite-memory

**Give your local LLM persistent long-term memory — in one Python file. No vector DB, no server, no framework.**

LLMs forget everything the moment a message scrolls out of the context window,
and everything again when the process restarts. `sqlite-memory` is the smallest
possible fix: embed each fact or chat turn with a local [Ollama](https://ollama.com)
model, store it in a single SQLite file, and semantically `recall()` the relevant
bits before the model answers. The memory is just a `.db` file, so it survives
restarts and is trivial to back up or move.

## Why another memory library?

Projects like Mem0, Zep, Letta and Cognee are powerful but heavy: servers,
vector databases, cloud accounts, many dependencies. `sqlite-memory` trades
features for radical simplicity:

- **One file, standard library only** — `sqlite3`, `urllib`, `json`, `math`.
- **Local & private** — nothing leaves your machine.
- **No infrastructure** — no daemon, no vector DB; the index is a portable `.db`.
- **Readable in one sitting** — easy to audit and fork.

## Quickstart

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:7b
python example_chat.py     # tell it facts, quit, run again, ask about them
```

## API

```python
from sqlite_memory import Memory

mem = Memory("memory.db")
mem.remember("The user ships firmware for ESP32 boards", role="fact", tags="work")
mem.recall("what does the user work on?", k=5)   # semantic search -> list of hits
mem.recent(10)                                    # last N memories
mem.forget(tag="work")                            # or forget(id=..) / forget(before_ts=..)
```

## How it works

1. `remember(text)` embeds the text via Ollama's `/api/embeddings` and stores
   `(ts, role, text, tags, embedding)` in SQLite.
2. `recall(query)` embeds the query and ranks every stored memory by cosine
   similarity (computed in Python), returning the top-k.
3. In a chat loop you `recall()` before generating and inject the hits into the
   system prompt, then `remember()` the new turns.

## Configuration (env vars)

| Variable | Default |
|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` |
| `EMBED_MODEL` | `nomic-embed-text` |
| `CHAT_MODEL` (example only) | `qwen2.5:7b` |

## Limits (honest)

- Linear cosine scan — great up to tens of thousands of memories; add an ANN
  index beyond that.
- No automatic **consolidation or selective forgetting** (the hard, unsolved part
  of agent memory): `forget()` is manual/rule-based. Contributions welcome.
- Recall quality is only as good as the embedding model.

## License

MIT
