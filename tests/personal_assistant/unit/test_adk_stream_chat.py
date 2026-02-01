from __future__ import annotations

import pytest

from personal_assistant_adk import run as adk_run
from personal_assistant_adk import utils as adk_utils

pytestmark = [pytest.mark.adk, pytest.mark.unit]


class _FakeRunner:
    def __init__(self, event_texts: list[str]) -> None:
        self.event_texts = event_texts
        self.calls: list[tuple[str, str]] = []

    async def run_async(self, user_id: str, session_id: str, new_message: object):
        parts = getattr(new_message, "parts", None)
        message_text = ""
        if parts:
            message_text = "".join(
                getattr(part, "text", "")
                for part in parts
                if getattr(part, "text", None)
            )
        self.calls.append((session_id, message_text))
        for text in self.event_texts:
            yield _FakeEvent(text)


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


@pytest.mark.asyncio
async def test_stream_chat_yields_deltas(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _FakeRunner(["Hello", "Hello world"])
    monkeypatch.setattr(adk_run, "_build_runner", lambda: runner)
    monkeypatch.setattr(adk_run, "generate_session_id", lambda: "session-123")

    session_id, stream = await adk_run.stream_chat("hi", session_id=None)
    chunks = [chunk async for chunk in stream]

    assert session_id == "session-123"
    assert chunks == ["Hello", " world"]
    assert runner.calls == [("session-123", "hi")]


@pytest.mark.asyncio
async def test_stream_chat_uses_existing_session_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = _FakeRunner(["pong"])
    monkeypatch.setattr(adk_run, "_build_runner", lambda: runner)

    session_id, stream = await adk_run.stream_chat("ping", session_id="sess-1")
    chunks = [chunk async for chunk in stream]

    assert session_id == "sess-1"
    assert chunks == ["pong"]
    assert runner.calls == [("sess-1", "ping")]


@pytest.mark.asyncio
async def test_stream_chat_includes_video_path(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _FakeRunner(["ok"])
    monkeypatch.setattr(adk_run, "_build_runner", lambda: runner)
    monkeypatch.setattr(adk_run, "generate_session_id", lambda: "session-456")

    session_id, stream = await adk_run.stream_chat(
        "What is happening?", session_id=None, video_path="/tmp/video.mp4"
    )
    _ = [chunk async for chunk in stream]

    assert session_id == "session-456"
    assert runner.calls == [
        (
            "session-456",
            "Video file path: /tmp/video.mp4\n\nUser message: What is happening?",
        )
    ]


@pytest.mark.asyncio
async def test_stream_chat_maps_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(adk_run, "_build_runner", lambda: _FailingRunner())

    session_id, stream = await adk_run.stream_chat("hello", session_id="sess-err")

    assert session_id == "sess-err"
    with pytest.raises(adk_utils.ChatError, match="Redis"):
        _ = [chunk async for chunk in stream]
