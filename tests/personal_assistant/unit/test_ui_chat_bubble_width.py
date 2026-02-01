from __future__ import annotations

import pytest

from personal_assistant_ui.views import chat as chat_view

pytestmark = [pytest.mark.unit]


def _make_view(page_width: int) -> chat_view.ChatView:
    view = chat_view.ChatView.__new__(chat_view.ChatView)
    view.page = type("P", (), {"width": page_width})()
    return view


def test_bubble_width_narrow_window() -> None:
    view = _make_view(500)

    width = view._bubble_max_width()

    assert width == chat_view.BUBBLE_MIN_WIDTH


def test_bubble_width_wide_window() -> None:
    view = _make_view(1400)

    width = view._bubble_max_width()

    assert width == chat_view.BUBBLE_MAX_WIDTH
