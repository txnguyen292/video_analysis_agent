from __future__ import annotations

import uuid

import pytest

from personal_assistant_adk import run as adk_run
from personal_assistant_adk import utils as adk_utils

pytestmark = pytest.mark.adk


@pytest.mark.unit
def test_utils_chat_error_is_runtime_error() -> None:
    assert issubclass(adk_utils.ChatError, RuntimeError)
    assert adk_run.ChatError is adk_utils.ChatError


@pytest.mark.unit
def test_generate_session_id_returns_uuid() -> None:
    session_id = adk_utils.generate_session_id()

    assert isinstance(session_id, str)
    assert session_id
    uuid.UUID(session_id)
