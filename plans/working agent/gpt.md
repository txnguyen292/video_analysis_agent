Here’s an updated, ADK-aligned plan that keeps Codex’s good ideas, but fixes the two big failure modes: (1) mixing transcripts with “memory,” and (2) using Redis for everything without clear boundaries.

⸻

Updated Plan: ADK Assistant with Redis STM + Redis/DB LTM (Hybrid Retrieval)

Goal

Build an ADK-based chat assistant with:
	•	Short-term memory (STM) = conversation session + working state
	•	Long-term memory (LTM) = curated, durable memories + summaries (semantic + keyword retrieval)
	•	Local-first: no GCP required
	•	Embeddings: OpenAI

⸻

Architecture

A) Short-term memory (STM): Session/State (Redis + TTL)

What it stores
	•	Recent turns (or ADK session transcript pointer)
	•	In-progress task plan
	•	Tool outputs you’ll reuse soon
	•	Temporary variables (e.g., “current_project”, “draft_email_v2”)

How
	•	Implement a Redis-backed SessionService (or equivalent) with TTL (e.g., 1–7 days)
	•	Session keyspace:
	•	sess:{app}:{user}:{session_id}

Why
	•	STM needs speed, TTL cleanup, and multi-worker safety.

⸻

B) Long-term memory (LTM): MemoryService (curated facts + summaries)

What it stores (NOT raw chat logs)
	•	preference: stable preferences and constraints
	•	project: ongoing workstreams + status snapshots
	•	person: important entities and relationship context
	•	decision: durable decisions and rationale
	•	summary: session summary + topic summaries (periodic distillation)

How
	•	Implement RedisMemoryService using Redis Stack / RediSearch:
	•	TEXT fields for keyword recall
	•	TAG fields for filtering (user_id, type, project_id, etc.)
	•	VECTOR field for semantic recall (OpenAI embeddings)
	•	Memory keyspace:
	•	mem:{app}:{user}:{memory_id}

Optional
	•	Keep raw transcripts in a separate “transcript store” (for debug/audit only):
	•	tx:{app}:{user}:{session_id}

⸻

C) Retrieval strategy: Preload first, then Load

Phase 1 (MVP): PreloadMemory
	•	Always fetch top-K relevant LTM items each turn (K small, like 5–10)
	•	Works well only if your LTM is curated

Phase 2: LoadMemory
	•	Agent fetches memory only when needed (cheaper + less noise)
	•	Switch once memory volume grows

⸻

Redis schema and indexing (LTM)

Memory record schema (example)

Fields:
	•	user_id, session_id (optional link), type (preference/project/person/decision/summary)
	•	text (the human-readable memory)
	•	created_at, updated_at
	•	source (manual/auto/tool)
	•	importance (0–1) + confidence (low/med/high)
	•	embedding (VECTOR)

RediSearch index
	•	TEXT: text
	•	TAG: user_id, type, project_id, source
	•	NUMERIC: created_at, importance
	•	VECTOR: embedding
	•	Queries:
	•	Hybrid: text query + KNN vector + filters by user/type + recency/importance rerank

Design requirement: retrieval must be scoped to user_id (and optionally app_name) to avoid leakage.

⸻

Memory write policy (this is the “make it good” part)

1) Write filter (“Should we store this?”)

Only store if it is:
	•	durable (matters in >2 weeks), OR
	•	reusable preference/constraint, OR
	•	ongoing project context, OR
	•	user explicitly says “remember this”

Everything else stays in STM or transcripts.

2) Memory shaping

Don’t store raw turns. Store atomic, clean statements, e.g.:
	•	Preference: “User prefers local-first architecture and short answers.”
	•	Project: “Building ADK assistant with Redis STM and curated LTM.”
	•	Decision: “Use PreloadMemory initially; switch to LoadMemory when memory grows.”

3) Distillation

Every N turns (e.g., 20) or at session end:
	•	Generate a session summary memory
	•	Optionally merge/refresh “project summaries” and “profile summary”

⸻

Build Plan (2 weeks)

Week 1 — MVP that works end-to-end

Step 1: Scaffold ADK chat app
	•	Create assistant/ module + entrypoint CLI
	•	Basic chat loop + model config

Step 2: STM via Redis SessionService
	•	Store session state + recent context
	•	TTL cleanup
	•	Confirm multi-session works

Step 3: LTM via RedisMemoryService (curated memories)
	•	Implement:
	•	put_memory(user_id, type, text, meta)
	•	search_memory(user_id, query, top_k, filters)
	•	Add embeddings for each stored memory

Step 4: Wire memory retrieval into agent
	•	Use PreloadMemory at the start of each turn
	•	Provide retrieved memories as “context block” (separate from conversation transcript)

Step 5: Persist memories with an “after turn” hook
	•	After each agent response:
	•	run write filter
	•	store 0–2 new memories max (avoid spam)

End of Week 1 deliverable: restart the app → new session → assistant still remembers durable facts.

⸻

Week 2 — Make it assistant-grade

Step 6: Summaries + distillation
	•	Session-end summary memory
	•	Optional rolling summary every N turns

Step 7: Reranking + hygiene
	•	RRF/linear blend or simple weighted scoring:
	•	semantic score + keyword score + recency + importance
	•	Add “forget/overwrite” behavior:
	•	update existing preference instead of duplicating

Step 8: Switch to LoadMemory (optional)
	•	Only retrieve memory when the agent detects a need (projects, preferences, people)

Step 9: Testing
	•	Unit tests:
	•	write filter correctness
	•	memory put/search behaviors
	•	Integration:
	•	local Redis Stack
	•	end-to-end chat scenario test

⸻

Repo layout (suggested)

repo/
  assistant/
    main.py                  # CLI entrypoint
    agent.py                  # ADK agent definition
    config.py
    memory/
      session_store_redis.py  # STM (SessionService)
      memory_service_redis.py # LTM (MemoryService)
      schema.py               # record types, validation
      write_policy.py         # should_store + shaping
      summarizer.py           # distillation jobs
      retrieval.py            # hybrid search + rerank
    tools/
      notes.py
      tasks.py
  tests/
    test_write_policy.py
    test_memory_service.py
    test_integration_local_redis.py


⸻
