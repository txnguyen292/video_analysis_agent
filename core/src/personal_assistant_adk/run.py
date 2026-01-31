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
from personal_assistant_adk.models import ChatResult
from personal_assistant_adk.utils import ChatError, generate_session_id


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

    agent = build_agent()
    return Runner(
        app_name="personal_assistant",
        agent=agent,
        session_service=InMemorySessionService(),
    )


def chat(message: str, session_id: str | None = None) -> ChatResult:
    """Send a message to the ADK chat runner.

    Args:
        message: User input text.
        session_id: Optional session ID. If omitted, a new one is generated.

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
        response_text = _run_sync(runner, session_id, message)
    except ConnectionError as exc:
        logger.error(f"Chat backend connection error: {exc}")
        raise ChatError("Redis connection failed. Please try again.") from exc

    return ChatResult(session_id=session_id, response_text=response_text)


def _run_sync(runner: Runner, session_id: str, message: str) -> str:
    """Run the ADK runner and return response text.

    Args:
        runner: ADK Runner configured with the agent.
        session_id: Session ID for the chat.
        message: User input text to send.

    Returns:
        The assistant response text.

    Example:
        >>> runner = _build_runner()
        >>> _run_sync(runner, "sess-1", "Hello")  # doctest: +SKIP
        'Hello!'
    """

    async def _run_async() -> str:
        content = types.Content(role="user", parts=[types.Part(text=message)])
        response_text = ""
        async for event in runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text = part.text
        return response_text

    return asyncio.run(_run_async())
