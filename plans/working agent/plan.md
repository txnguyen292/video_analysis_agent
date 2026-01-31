# Working Assistant (Google ADK + Hybrid Memory)

## Goal
Build an ADK-based chat assistant with:
- Short‑term memory (session state)
- Long‑term memory (durable store + hybrid retrieval)
- Local Redis for fast hybrid search
- OpenAI embeddings (no GCP)
- Both full conversation and summaries for recall
- UI chat view replaced by ADK multi‑turn chat (session IDs)

## High‑level approach
- **ADK** provides agent runtime + session state
- **Durable store** keeps source‑of‑truth memory (full conversation chunks + summaries)
- **Redis** acts as hybrid search index (BM25 + vector) for fast retrieval
- **Custom MemoryService** wires ADK to Redis + durable store
- **UI** calls the ADK chat service and keeps memory retrieval hidden

## Architecture

### A) Short‑term memory (STM)
- ADK Session/State for in‑chat context, ephemeral by design
- Optional Redis SessionService for TTL‑based session cache (1–7 days)

### B) Long‑term memory (LTM)
**Source of truth (durable):**
- SQLite/Postgres/filesystem store for full conversation chunks + summaries
- Records:
  - `kind`: `full` | `summary`
  - `user_id`, `session_id`, `text`, `created_at`, `meta`

**Retrieval index (Redis Stack):**
- RediSearch index over:
  - `TEXT`: text (BM25)
  - `TAG`: user_id, kind, session_id
  - `VECTOR`: embedding (OpenAI)
- Redis holds embeddings + lightweight metadata + pointer to durable record

### C) Hybrid search
- Preferred: **Redis Stack 8.4+** using `FT.HYBRID` (RRF or linear fusion)
- Fallback: run text search + vector KNN, then merge/rerank in app

## ADK integration points
- Implement `RedisMemoryService` (ADK `BaseMemoryService`):
  - `add_session_to_memory(session)` → write full chunks + summaries to durable store and index in Redis
  - `search_memory(app_name, user_id, query)` → embed query, run hybrid search, return top‑k memories
- Use `PreloadMemoryTool` (initially) and `after_agent_callback` to persist memory
- Session `state` for short‑term memory
- Keep agent docs co-located with the package (`core/src/personal_assistant_adk/docs/agent.md`)
- Maintain `docs/workflow.svg` in the agent package reflecting `agent.py`

## UI integration (refinement)
- Replace current UI chat view with ADK chat.
- Maintain a session ID across turns in UI state.
- Keep memory retrieval hidden (no debug memory panels).
- Read OpenAI + Redis settings from `.env` (defaults: `REDIS_HOST=localhost`, `REDIS_PORT=6379`).
- If Redis is unavailable, show a clear UI error.

## Plan

1) **Scaffold ADK assistant (package layout)**
   - Ensure `core/src/personal_assistant_adk/agent.py` is the agent entrypoint
   - Move runner logic to `core/src/personal_assistant_adk/runner.py`
   - Add `core/src/personal_assistant_adk/docs/agent.md` sourced from `agent.py`
   - Add `core/src/personal_assistant_adk/docs/workflow.svg` based on agent flow
   - Document agent instruction + tools list (even if empty)

2) **Durable store**
   - Choose SQLite (local) with tables for memory entries
   - Store `full` and `summary` records

3) **Redis index**
   - Create RediSearch index
   - Store embeddings + metadata + durable record ID
   - Enable FT.HYBRID if Redis Stack 8.4+

4) **Custom MemoryService**
   - Implement RedisMemoryService (read/write)
   - OpenAI embeddings for writes and queries

5) **Memory write policy**
   - Always store full conversation chunks
   - Periodically store summaries (per N turns or session end)
   - Add “explicit remember” path to store curated facts

6) **Retrieval wiring**
   - Preload top‑k memories (mix full + summary)
   - Separate “memory context” from transcript in prompt

7) **UI replacement**
   - Replace UI chat view to call ADK chat service
   - Preserve session ID across turns
   - Keep memory retrieval hidden

8) **Testing**
   - Unit tests for write policy and RedisMemoryService (mock Redis/OpenAI)
   - Integration test with local Redis Stack
   - UI smoke test: two turns in same session

9) **Docs**
   - Update README with ADK chat usage, Redis Stack startup, `.env` requirements
   - Keep agent docs in `core/src/personal_assistant_adk/docs/` in sync with `agent.py`

## Open Questions
- Embedding model choice (OpenAI small vs large)
- Summary cadence (per session end vs every N turns)
- Redis Stack version (8.4+ for FT.HYBRID) or fallback mode
