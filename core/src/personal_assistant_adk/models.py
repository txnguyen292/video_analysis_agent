"""Shared models for the ADK assistant."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatResult:
    """Chat response payload.

    Attributes:
        session_id: Session identifier used for multi-turn context.
        response_text: Assistant response text.

    Example:
        >>> ChatResult(session_id="sess-1", response_text="Hello")
        ChatResult(session_id='sess-1', response_text='Hello')
    """

    session_id: str
    response_text: str
