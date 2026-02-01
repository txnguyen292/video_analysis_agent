"""ADK chat runtime helpers.

This module provides a synchronous chat interface backed by the ADK Runner.

Example:
    >>> result = chat("Hello")  # doctest: +SKIP
    >>> result.response_text
    'Hello!'
"""

from __future__ import annotations

import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from loguru import logger

from personal_assistant_adk.agent import build_agent
from collections.abc import AsyncIterator

from personal_assistant_adk.models import ChatResult
from personal_assistant_adk.utils import ChatError, generate_session_id

_APP_NAME = "personal_assistant"
_USER_ID = "default_user"
_RUNNER: Runner | None = None


def _build_runner() -> Runner:
    """Build the ADK runner instance.

    This uses an in-memory session service for now. It will be replaced
    with Redis-backed session and memory services in later tasks.

    Returns:
        Runner configured with a default app name, agent, and session service.

    Example:
        >>> runner = _build_runner()
        >>> runner.app_name
        'personal_assistant'
    """

    global _RUNNER
    if _RUNNER is not None:
        return _RUNNER

    agent = build_agent()
    _RUNNER = Runner(
        app_name=_APP_NAME,
        agent=agent,
        session_service=InMemorySessionService(),
    )
    return _RUNNER


def chat(
    message: str,
    session_id: str | None = None,
    video_path: str | None = None,
) -> ChatResult:
    """Send a message to the ADK chat runner.

    Args:
        message: User input text.
        session_id: Optional session ID. If omitted, a new one is generated.
        video_path: Optional video file path used for video questions.

    Returns:
        ChatResult containing session_id and response_text.

    Raises:
        ChatError: If backend services fail (e.g., Redis unavailable).

    Example:
        >>> result = chat("Hello")  # doctest: +SKIP
        >>> result.response_text
        'Hello!'
    """

    if not message:
        raise ValueError("message is required")

    session_id = session_id or generate_session_id()

    try:
        runner = _build_runner()
        response_text = _run_sync(runner, session_id, message, video_path)
    except ConnectionError as exc:
        logger.error(f"Chat backend connection error: {exc}")
        raise ChatError("Redis connection failed. Please try again.") from exc

    return ChatResult(session_id=session_id, response_text=response_text)


def _run_sync(
    runner: Runner,
    session_id: str,
    message: str,
    video_path: str | None = None,
) -> str:
    """Run the ADK runner and return response text.

    Args:
        runner: ADK Runner configured with the agent.
        session_id: Session ID for the chat.
        message: User input text to send.
        video_path: Optional video file path used for video questions.

    Returns:
        The assistant response text.

    Example:
        >>> runner = _build_runner()
        >>> _run_sync(runner, "sess-1", "Hello")  # doctest: +SKIP
        'Hello!'
    """

    async def _run_async() -> str:
        await _ensure_session(runner, session_id)
        content = _build_user_content(message, video_path)
        response_text = ""
        async for event in runner.run_async(
            user_id=_USER_ID,
            session_id=session_id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text = part.text
        return response_text

    return asyncio.run(_run_async())


def _build_user_content(message: str, video_path: str | None) -> types.Content:
    """Build ADK user content, optionally including a video reference.

    Args:
        message: User input text.
        video_path: Optional video file path for video questions.

    Returns:
        ADK content payload with the user text.

    Example:
        >>> content = _build_user_content("Hello", None)
        >>> content.role
        'user'
    """

    if video_path:
        text = f"Video file path: {video_path}\n\nUser message: {message}"
    else:
        text = message
    return types.Content(role="user", parts=[types.Part(text=text)])


async def stream_chat(
    message: str,
    session_id: str | None = None,
    video_path: str | None = None,
) -> tuple[str, AsyncIterator[str]]:
    """Stream chat responses from the ADK runner.

    Args:
        message: User input text.
        session_id: Optional session ID. If omitted, a new one is generated.
        video_path: Optional video file path used for video questions.

    Returns:
        A tuple of (session_id, async iterator of response text chunks).

    Raises:
        ChatError: If backend services fail (e.g., Redis unavailable).

    Example:
        >>> session_id, stream = await stream_chat("Hello")  # doctest: +SKIP
        >>> async for chunk in stream:  # doctest: +SKIP
        ...     print(chunk)
    """

    if not message:
        raise ValueError("message is required")

    session_id = session_id or generate_session_id()
    runner = _build_runner()
    content = _build_user_content(message, video_path)

    async def _stream() -> AsyncIterator[str]:
        last_text = ""
        try:
            await _ensure_session(runner, session_id)
            async for event in runner.run_async(
                user_id=_USER_ID,
                session_id=session_id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            text = part.text
                            if text.startswith(last_text):
                                delta = text[len(last_text) :]
                            else:
                                delta = text
                            last_text = text
                            if delta:
                                yield delta
        except ConnectionError as exc:
            logger.error(f"Chat backend connection error: {exc}")
            raise ChatError("Redis connection failed. Please try again.") from exc

    return session_id, _stream()


async def _ensure_session(runner: Runner, session_id: str) -> None:
    """Ensure the ADK session exists before running the agent.

    Args:
        runner: ADK Runner instance.
        session_id: Session ID to validate or create.

    Example:
        >>> runner = _build_runner()  # doctest: +SKIP
        >>> await _ensure_session(runner, "sess-1")  # doctest: +SKIP
    """

    session_service = getattr(runner, "session_service", None)
    if session_service is None:
        return

    session = await session_service.get_session(
        app_name=_APP_NAME,
        user_id=_USER_ID,
        session_id=session_id,
    )
    if session is None:
        await session_service.create_session(
            app_name=_APP_NAME,
            user_id=_USER_ID,
            session_id=session_id,
        )
