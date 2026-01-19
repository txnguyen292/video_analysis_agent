from __future__ import annotations

import pytest

from personal_assistant_adk import agent as adk_agent
from personal_assistant_adk import utils as adk_utils

pytestmark = pytest.mark.adk


class _FakeRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def run_async(self, user_id: str, session_id: str, new_message: object):
        message_text = ""
        parts = getattr(new_message, "parts", None)
        if parts:
            first_part = parts[0]
            message_text = getattr(first_part, "text", "")
        self.calls.append((session_id, message_text))
        yield _FakeEvent("hello")


class _FailingRunner:
    async def run_async(self, user_id: str, session_id: str, new_message: object):
        raise ConnectionError("redis down")
        if False:
            yield None


class _FakeEvent:
    def __init__(self, text: str) -> None:
        self.content = _FakeContent(text)


class _FakeContent:
    def __init__(self, text: str) -> None:
        self.parts = [_FakePart(text)]


class _FakePart:
    def __init__(self, text: str) -> None:
        self.text = text


@pytest.mark.unit
def test_get_openai_api_key_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adk_utils.config, "get_env", lambda key, default=None: None)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        adk_utils.get_openai_api_key()


@pytest.mark.unit
def test_chat_generates_session_id(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _FakeRunner()
    monkeypatch.setattr(adk_agent, "_build_runner", lambda: runner)
    monkeypatch.setattr(adk_agent, "generate_session_id", lambda: "session-123")

    result = adk_agent.chat("hello", session_id=None)

    assert result.response_text == "hello"
    assert result.session_id == "session-123"
    assert runner.calls == [("session-123", "hello")]


@pytest.mark.unit
def test_chat_uses_existing_session_id(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _FakeRunner()
    monkeypatch.setattr(adk_agent, "_build_runner", lambda: runner)

    result = adk_agent.chat("ping", session_id="sess-1")

    assert result.session_id == "sess-1"
    assert runner.calls == [("sess-1", "ping")]


@pytest.mark.unit
def test_chat_raises_friendly_error_on_redis_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(adk_agent, "_build_runner", lambda: _FailingRunner())

    with pytest.raises(adk_utils.ChatError, match="Redis"):
        adk_agent.chat("hello", session_id="sess-err")
