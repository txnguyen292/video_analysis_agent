from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from personal_assistant.usage import UsageStats
from personal_assistant_ui import agent_helper


@dataclass
class _Call:
    method: str
    video_file: Any
    query: str | None


class _FakeClient:
    def __init__(self) -> None:
        self.uploaded_paths: list[str] = []

    def upload_video(self, video_path: str) -> str:
        self.uploaded_paths.append(video_path)
        return f"video:{video_path}"


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeAgent:
    def __init__(self) -> None:
        self.client = _FakeClient()
        self.calls: list[_Call] = []

    def get_summary(self, video_file: Any) -> _FakeResponse:
        self.calls.append(_Call("summarize", video_file, None))
        return _FakeResponse("summary")

    def ask_question(self, video_file: Any, query: str | None) -> _FakeResponse:
        self.calls.append(_Call("ask", video_file, query))
        return _FakeResponse("answer")

    def detect_events(self, video_file: Any) -> _FakeResponse:
        self.calls.append(_Call("events", video_file, None))
        return _FakeResponse("events")

    def transcribe_and_diarize(self, video_file: Any) -> _FakeResponse:
        self.calls.append(_Call("transcribe", video_file, None))
        return _FakeResponse("transcript")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("task_type", "expected_method", "expected_text"),
    [
        ("summarize", "summarize", "summary"),
        ("ask", "ask", "answer"),
        ("events", "events", "events"),
        ("transcribe", "transcribe", "transcript"),
    ],
)
async def test_analyze_video_routes_task(
    monkeypatch: pytest.MonkeyPatch,
    task_type: str,
    expected_method: str,
    expected_text: str,
) -> None:
    fake_agent = _FakeAgent()
    captured: dict[str, str] = {}

    def fake_get_agent(model_id: str) -> _FakeAgent:
        captured["model_id"] = model_id
        return fake_agent

    async def fake_to_thread(fn):
        return fn()

    monkeypatch.setattr(agent_helper, "get_agent", fake_get_agent)
    monkeypatch.setattr(agent_helper, "load_ui_config", lambda: {})
    monkeypatch.setattr(agent_helper, "load_config", lambda: {})
    monkeypatch.setattr(agent_helper.asyncio, "to_thread", fake_to_thread)

    helper = agent_helper.AgentHelper()

    text, stats, _elapsed = await helper.analyze_video(
        "video.mp4", task_type, query="question"
    )

    assert captured["model_id"] == "gemini-3-flash"
    assert fake_agent.client.uploaded_paths == ["video.mp4"]
    assert fake_agent.calls[0].method == expected_method
    if task_type == "ask":
        assert fake_agent.calls[0].query == "question"
    else:
        assert fake_agent.calls[0].query is None
    assert text == expected_text
    assert isinstance(stats, UsageStats)
