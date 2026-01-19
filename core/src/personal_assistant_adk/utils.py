"""Shared helpers for ADK-backed agents."""

from __future__ import annotations

import uuid

from personal_assistant import config


class ChatError(RuntimeError):
    """User-facing chat error for UI/CLI surfaces."""


def get_openai_api_key() -> str:
    """Return the OpenAI API key from environment.

    Raises:
        ValueError: If OPENAI_API_KEY is missing.

    Example:
        >>> get_openai_api_key()  # doctest: +SKIP
        'sk-...'
    """

    api_key = config.get_env("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required")
    return api_key


def generate_session_id() -> str:
    """Generate a new session ID.

    Returns:
        A random UUID string.

    Example:
        >>> sid = generate_session_id()
        >>> isinstance(sid, str)
        True
    """

    return str(uuid.uuid4())
