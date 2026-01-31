# Working Agent: ADK Chat in UI

## Overview
Replace the current UI chat view with a Google ADK–backed chat experience that supports multi‑turn conversations using session IDs. Memory retrieval should be hidden from the UI. OpenAI embeddings and Redis settings are loaded from `.env`.

## Requirements
- Replace the existing UI chat view with ADK chat.
- Support multi‑turn conversations using session IDs.
- Hide memory retrieval details in the UI (no memory debug display).
- Use OpenAI embeddings for memory search.
- Read OpenAI and Redis settings from `.env`.
- Default Redis port can be any unused port; if unset, use `6379`.

## Inputs / Outputs
**Inputs:**
- User message text
- Optional session ID (if not provided, generate one)
- `.env` values (e.g., `OPENAI_API_KEY`, `REDIS_HOST`, `REDIS_PORT`)

**Outputs:**
- Assistant response text
- Updated session state persisted in memory services

## Constraints
- No GCP usage.
- Redis is local (Docker/Podman acceptable).
- UI must keep memory retrieval hidden.

## Acceptance Criteria
- UI chat view uses ADK chat and supports multi‑turn sessions.
- Session ID persists across turns in a single UI session.
- OpenAI/Redis settings are read from `.env`.
- Memory retrieval does not appear in the UI.
- If Redis is unavailable, the UI surfaces a clear error message.

## Test Plan
- Unit tests for session ID handling and config loading.
- Integration test with local Redis Stack and a mocked OpenAI embedding call.
- UI smoke test: send two messages and verify the assistant responds both times in the same session.
