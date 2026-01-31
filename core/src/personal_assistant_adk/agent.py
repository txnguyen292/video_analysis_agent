"""ADK agent definition for the personal assistant.

This module exposes the root agent and ADK app used by CLI tooling
such as `adk web`.

Example:
    >>> root_agent.name
    'personal_assistant'
"""

from __future__ import annotations

from pathlib import Path

from google.adk.cli.fast_api import get_fast_api_app
from google.adk.agents import LlmAgent

from personal_assistant import config


def build_agent() -> LlmAgent:
    """Build and return the ADK LLM agent.

    Returns:
        LlmAgent configured with a default model and instruction, used
        as the root ADK agent.

    Example:
        >>> agent = build_agent()
        >>> agent.name
        'personal_assistant'
    """

    model = config.get_env("ADK_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"
    return LlmAgent(
        name="personal_assistant",
        model=model,
        description="ADK-backed personal assistant.",
        instruction="You are a helpful assistant.",
    )


root_agent = build_agent()
"""Root agent used by ADK CLI tooling."""

AGENTS_DIR = Path(__file__).resolve().parent.parent
"""Directory containing ADK agent packages for web serving."""

app = get_fast_api_app(agents_dir=str(AGENTS_DIR), web=True)
"""FastAPI application used by `adk web` and related tooling."""
