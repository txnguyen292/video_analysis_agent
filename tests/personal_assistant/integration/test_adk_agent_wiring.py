from __future__ import annotations

import pytest

from personal_assistant_adk.agent import build_agent

pytestmark = [pytest.mark.adk, pytest.mark.integration]


def test_build_agent_includes_video_sub_agent() -> None:
    agent = build_agent()
    sub_agent_names = [sub_agent.name for sub_agent in agent.sub_agents]

    assert "video_assistant" in sub_agent_names
