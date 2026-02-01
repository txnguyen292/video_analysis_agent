from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

from personal_assistant.agent import VideoAgent
from personal_assistant.config import load_config
from personal_assistant.main import get_agent
from personal_assistant.usage import UsageStats, UsageTracker
from personal_assistant_adk import run as adk_run
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
            assert self.agent is not None
            # Upload
            print(f"Uploading {video_path}...")
            video_file = self.agent.client.upload_video(video_path)

            # Process
            response = None
            if task_type == "summarize":
                response = self.agent.get_summary(video_file)
            elif task_type == "ask":
                assert query is not None, "Query string is required for 'ask' task"
                response = self.agent.ask_question(video_file, query)
            elif task_type == "events":
                response = self.agent.detect_events(video_file)
            elif task_type == "transcribe":
                response = self.agent.transcribe_and_diarize(video_file)

            if response is None:
                raise ValueError("No response from agent")

            elapsed = time.perf_counter() - start_time
            stats = UsageTracker.extract_usage(response, self.model_id)
            return response.text, stats, elapsed

        return await asyncio.to_thread(_run)


class AdkChatHelper:
    """Helper for streaming ADK chat responses in the UI.

    This helper keeps the ADK session ID in memory for the lifetime of
    the UI instance, enabling multi-turn conversations.

    Example:
        >>> helper = AdkChatHelper()
        >>> isinstance(helper.session_id, (str, type(None)))
        True
    """

    def __init__(self) -> None:
        self.session_id: str | None = None

    async def stream_chat(
        self, message: str, video_path: str | None = None
    ) -> tuple[str, AsyncIterator[str]]:
        """Stream chat response chunks from the ADK agent.

        Args:
            message: User input text.
            video_path: Optional video file path for video questions.

        Returns:
            Tuple of (session_id, async iterator of response chunks).

        Example:
            >>> helper = AdkChatHelper()  # doctest: +SKIP
            >>> session_id, stream = await helper.stream_chat(\"Hello\")  # doctest: +SKIP
            >>> async for chunk in stream:  # doctest: +SKIP
            ...     print(chunk)
        """

        session_id, stream = await adk_run.stream_chat(
            message, session_id=self.session_id, video_path=video_path
        )
        self.session_id = session_id
        return session_id, stream
