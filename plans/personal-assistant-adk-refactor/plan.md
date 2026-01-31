# Plan: Personal Assistant ADK refactor

## Goals
- Move chat/runner (CLI-style entrypoints) out of `agent.py` into `run.py`.
- Keep `agent.py` focused on agent definition only.
- Add an `app` object in `agent.py` so ADK web can load the agent.
- Preserve existing chat behavior and tests.

## Approach
1) **Agent definition cleanup**
   - Keep `build_agent()` in `agent.py` to encapsulate model/config selection.
   - Define `root_agent = build_agent()` for ADK discovery.
   - Define `app = App(name=..., root_agent=root_agent)` using `google.adk.apps.App`.
   - Ensure docstrings remain detailed and include examples.

2) **Move runtime helpers to `run.py`**
   - Create `core/src/personal_assistant_adk/run.py`.
   - Move `_build_runner`, `_run_sync`, and `chat` into `run.py`.
   - Import `build_agent` from `agent.py` and `ChatResult`, `ChatError`, `generate_session_id` as needed.
   - Keep behavior identical to current `chat` (session ID generation, error mapping).

3) **ADK structure compliance**
   - Update `core/src/personal_assistant_adk/__init__.py` to `from . import agent` so ADK CLI can discover the agent package.

4) **Tests update**
   - Update `core/tests/test_adk_chat_service.py` to import `personal_assistant_adk.run` instead of `personal_assistant_adk.agent` for chat-related tests.
   - Keep tests aligned with the same behavior and monkeypatch targets.

## Files to change
- `core/src/personal_assistant_adk/agent.py`
- `core/src/personal_assistant_adk/run.py` (new)
- `core/src/personal_assistant_adk/__init__.py`
- `core/tests/test_adk_chat_service.py`

## Risks & Mitigations
- **ADK CLI discovery**: ensure `__init__.py` imports `agent` and `agent.py` defines `root_agent` and `app`.
- **Import cycles**: keep `run.py` importing `build_agent` only; avoid `agent.py` importing `run.py`.

## Test Plan
- `uv run video-agent-checks`
- `uv run pytest -m unit core/tests/test_adk_chat_service.py`
