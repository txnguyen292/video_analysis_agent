from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from personal_assistant.agent import VideoAgent


@dataclass
class _Call:
    video_file: Any
    prompt: str


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[_Call] = []

    def analyze_video(self, video_file: Any, prompt: str) -> str:
        self.calls.append(_Call(video_file=video_file, prompt=prompt))
        return "ok"


@pytest.mark.unit
def test_get_summary_prompt() -> None:
    client = _FakeClient()
    agent = VideoAgent(client)

    video_obj = object()
    result = agent.get_summary(video_obj)

    assert result == "ok"
    assert client.calls[0].video_file is video_obj
    assert (
        client.calls[0].prompt
        == "Provide a concise but comprehensive summary of this video. Highlight the key events and their timestamps."
    )


@pytest.mark.unit
def test_ask_question_prompt() -> None:
    client = _FakeClient()
    agent = VideoAgent(client)

    video_obj = object()
    result = agent.ask_question(video_obj, "What is happening?")

    assert result == "ok"
    assert client.calls[0].video_file is video_obj
    assert (
        client.calls[0].prompt
        == "Based on this video, please answer the following question: What is happening?"
    )


@pytest.mark.unit
def test_detect_events_prompt() -> None:
    client = _FakeClient()
    agent = VideoAgent(client)

    video_obj = object()
    result = agent.detect_events(video_obj)

    assert result == "ok"
    assert client.calls[0].video_file is video_obj
    assert (
        client.calls[0].prompt
        == "Identify and list all significant events or actions in this video with their corresponding timestamps. Format the output as a bulleted list."
    )


@pytest.mark.unit
def test_transcribe_and_diarize_prompt() -> None:
    client = _FakeClient()
    agent = VideoAgent(client)

    video_obj = object()
    result = agent.transcribe_and_diarize(video_obj)

    assert result == "ok"
    assert client.calls[0].video_file is video_obj
    assert client.calls[0].prompt == (
        "Transcribe the audio from this video. "
        "Identify different speakers and label them accordingly. "
        "Format the output strictly as followed: '[timestamp] Speaker: <content>'. "
        "For example: '[00:15] Speaker 1: Hello world.'"
    )
