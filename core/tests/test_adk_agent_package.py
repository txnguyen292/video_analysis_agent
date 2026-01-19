from __future__ import annotations

import pytest

pytestmark = pytest.mark.adk


def test_adk_agent_factory_exists() -> None:
    """Ensure ADK agent package exposes a factory for the runner/agent."""
    from personal_assistant_adk import agent as adk_agent

    assert hasattr(adk_agent, "build_agent")
    assert callable(adk_agent.build_agent)
