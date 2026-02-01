from __future__ import annotations

import pytest

from personal_assistant_adk import video_agent as adk_video

pytestmark = [pytest.mark.adk, pytest.mark.unit]


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeVideoClient:
    def __init__(self) -> None:
        self.uploaded: list[str] = []
        self.calls: list[tuple[str, str]] = []

    def upload_video(self, video_path: str):
        self.uploaded.append(video_path)
        return "video-file"

    def analyze_video(self, video_file: object, prompt: str):
        self.calls.append((video_file, prompt))
        return _FakeResponse("answer")


def test_analyze_video_uses_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeVideoClient()
    monkeypatch.setattr(adk_video, "_get_video_client", lambda: fake_client)

    result = adk_video.analyze_video("/tmp/video.mp4", "What happened?")

    assert result == "answer"
    assert fake_client.uploaded == ["/tmp/video.mp4"]
    assert fake_client.calls == [("video-file", "What happened?")]
