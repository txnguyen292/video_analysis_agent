# ADK Agent: personal_assistant

This document is derived from `core/src/personal_assistant_adk/agent.py` and is the source of truth for the current agent behavior.

## Overview
- **Agent name**: `personal_assistant`
- **Entry point**: `personal_assistant_adk.agent.chat`
- **Runner**: `google.adk.runners.Runner` with `InMemorySessionService`
- **Session IDs**: generated per request when not provided

## Configuration
- **Model**: `ADK_MODEL` env var (default: `gemini-2.5-flash`)

## Instruction
- "You are a helpful assistant."

## Tools
- **Configured tools**: none in `agent.py` (add tools here when available).

## Chat flow
1. `chat(message, session_id=None)` validates message input.
2. Builds a `Runner` with the ADK `LlmAgent` and `InMemorySessionService`.
3. `_run_sync` streams events from `runner.run_async` and returns the last text part.
4. Returns `ChatResult(session_id, response_text)`.

## Error handling
- Connection errors are wrapped in `ChatError` with a user-friendly Redis message.

## Outputs
- `ChatResult` with `session_id` and `response_text`.
