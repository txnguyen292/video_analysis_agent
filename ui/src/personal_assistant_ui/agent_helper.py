from __future__ import annotations

import asyncio
import time
from typing import Any

from personal_assistant.agent import VideoAgent
from personal_assistant.config import load_config
from personal_assistant.main import get_agent
from personal_assistant.usage import UsageStats, UsageTracker
from personal_assistant_ui.config import load_ui_config


class AgentHelper:
    def __init__(self) -> None:
        self.ui_config: dict[str, Any] = load_ui_config()
        self.core_config: dict[str, Any] = load_config()
        self.model_id = (
            self.ui_config.get("model")
            or self.core_config.get("model")
            or "gemini-3-flash"
        )
        self.agent: VideoAgent | None = None

    def _ensure_agent(self) -> None:
        if self.agent is None:
            self.agent = get_agent(self.model_id)

    async def analyze_video(
        self, video_path: str, task_type: str, query: str | None = None
    ) -> tuple[str, UsageStats, float]:
        """
        Runs the agent task in a separate thread to keep UI responsive.
        task_type: 'summarize', 'ask', 'events', 'transcribe'
        """

        def _run() -> tuple[str, UsageStats, float]:
            start_time = time.perf_counter()
            self._ensure_agent()
            # Upload
            print(f"Uploading {video_path}...")
            video_file = self.agent.client.upload_video(video_path)

            # Process
            response = None
            if task_type == "summarize":
                response = self.agent.get_summary(video_file)
            elif task_type == "ask":
                response = self.agent.ask_question(video_file, query)
            elif task_type == "events":
                response = self.agent.detect_events(video_file)
            elif task_type == "transcribe":
                response = self.agent.transcribe_and_diarize(video_file)

            elapsed = time.perf_counter() - start_time
            stats = UsageTracker.extract_usage(response, self.model_id)
            return response.text, stats, elapsed

        return await asyncio.to_thread(_run)
