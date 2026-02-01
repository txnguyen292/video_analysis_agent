from __future__ import annotations

import asyncio
import os
import subprocess

import flet as ft

from personal_assistant_ui import theme
from personal_assistant_ui.agent_helper import AdkChatHelper

BUBBLE_MIN_WIDTH = 280
BUBBLE_MAX_WIDTH = 680
BUBBLE_SCALE = 0.9
BUBBLE_PADDING_ALLOWANCE = 120
BUBBLE_HORIZONTAL_PADDING = 24
BUBBLE_CHAR_WIDTH = 9
BUBBLE_MAX_TEXT_WIDTH = 5000


class ChatView(ft.Column):
    """Personal Assistant chat view with optional video attachment.

    This view streams ADK responses into a chat transcript and keeps the
    session ID alive for the lifetime of the UI instance.

    Example:
        >>> isinstance(ChatView, type)
        True
    """

    def __init__(self, page: ft.Page):
        """Initialize the chat UI and wire up ADK streaming helpers.

        Args:
            page: Flet page instance hosting the view.

        Example:
            >>> ChatView  # doctest: +SKIP
            <class 'personal_assistant_ui.views.chat.ChatView'>
        """

        super().__init__()
        self.page = page
        self.expand = True
        self.adk_helper = AdkChatHelper()
        self.selected_file: str | None = None
        self._prior_on_resize = None

        # File picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)

        self.attach_btn = ft.IconButton(
            icon=ft.Icons.ATTACH_FILE,
            icon_color=theme.TEXT_PRIMARY,
            tooltip="Attach video",
            on_click=self.open_file_picker,
            style=ft.ButtonStyle(
                bgcolor=theme.BUTTON_SECONDARY_BG,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=10,
            ),
        )

        self.message_field = ft.TextField(
            label="Message",
            multiline=True,
            min_lines=1,
            max_lines=4,
            shift_enter=True,
            expand=True,
            filled=True,
            fill_color=theme.INPUT_BG,
            border_color=theme.BORDER,
            focused_border_color=theme.ACCENT,
            color=theme.TEXT_PRIMARY,
            label_style=ft.TextStyle(color=theme.TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=theme.TEXT_DIM),
            cursor_color=theme.ACCENT,
            border_radius=12,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            on_submit=self.send_message,
        )

        self.send_btn = ft.IconButton(
            icon=ft.Icons.SEND,
            icon_color=theme.TEXT_PRIMARY,
            on_click=self.send_message,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DISABLED: theme.BORDER_SOFT,
                    "": theme.BUTTON_PRIMARY_BG,
                },
                color={
                    ft.ControlState.DISABLED: theme.TEXT_DIM,
                    "": theme.TEXT_PRIMARY,
                },
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=12,
            ),
        )

        self.input_row = ft.Row(
            [self.attach_btn, self.message_field, self.send_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        self.attachment_label = ft.Text(
            "",
            color=theme.TEXT_MUTED,
            size=12,
        )
        self.clear_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=theme.TEXT_SECONDARY,
            tooltip="Clear attached video",
            on_click=self.clear_selected_file,
            style=ft.ButtonStyle(padding=6),
        )
        self.attachment_row = ft.Row(
            [
                ft.Icon(ft.Icons.MOVIE, color=theme.TEXT_MUTED),
                self.attachment_label,
                self.clear_btn,
            ],
            visible=False,
            alignment=ft.MainAxisAlignment.START,
            spacing=6,
        )

        self.chat_history = ft.ListView(
            expand=True,
            spacing=12,
            auto_scroll=True,
        )

        self.progress_bar = ft.ProgressBar(
            width=180,
            color=theme.ACCENT,
            bgcolor=theme.BORDER_SOFT,
            visible=False,
        )
        self.status_text = ft.Text("", color=theme.TEXT_MUTED, size=12)
        self.thinking_row = ft.Row(
            [self.progress_bar, self.status_text],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        self.chat_container = ft.Container(
            content=ft.Column(
                [self.chat_history, self.thinking_row],
                expand=True,
                spacing=12,
            ),
            border_radius=12,
            padding=20,
            bgcolor=theme.RESULT_BG,
            border=ft.border.all(1, theme.BORDER_SOFT),
            expand=True,
        )

        self.controls = [
            ft.Text(
                "Personal Assistant",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=theme.TEXT_PRIMARY,
            ),
            self.chat_container,
            self.attachment_row,
            self.input_row,
        ]

    def _register_overlays(self) -> None:
        """Ensure file pickers are registered on the page overlay."""

        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)

    def _unregister_overlays(self) -> None:
        """Remove file pickers from the page overlay if present."""

        if self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)

    def did_mount(self) -> None:
        """Register overlays when the view is mounted."""

        self._register_overlays()
        self._prior_on_resize = self.page.on_resize
        self.page.on_resize = self._handle_resize
        self.page.update()

    def will_unmount(self) -> None:
        """Cleanup overlays when the view is unmounted."""

        self._unregister_overlays()
        if self._prior_on_resize is not None:
            self.page.on_resize = self._prior_on_resize

    def _handle_resize(self, e: ft.ControlEvent | None = None) -> None:
        """Handle page resize events by reflowing chat bubbles.

        Args:
            e: Optional resize event payload from Flet.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view._handle_resize()  # doctest: +SKIP
        """

        self._refresh_bubble_widths()
        self.page.update()

    def _refresh_bubble_widths(self) -> None:
        """Recalculate bubble widths for all messages after resize.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view._refresh_bubble_widths()  # doctest: +SKIP
        """

        max_width = self._bubble_max_width()
        for row in self.chat_history.controls:
            if not isinstance(row, ft.Row) or not row.controls:
                continue
            bubble = row.controls[0]
            if not isinstance(bubble, ft.Container):
                continue
            content_row = bubble.content
            if not isinstance(content_row, ft.Row) or not content_row.controls:
                continue
            text_control = content_row.controls[0]
            if not isinstance(text_control, ft.Text):
                continue
            text_control.data = {
                "bubble": bubble,
                "content_row": content_row,
            }
            self._apply_text_layout(text_control, max_width)
        self.chat_history.update()
        self._scroll_to_bottom()

    def on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        """Handle file picker result and store the selected video path."""

        if e.files:
            self._apply_selected_file(e.files[0].path, e.files[0].name)

    def _apply_selected_file(self, path: str, name: str) -> None:
        """Persist a selected video file and update UI indicators."""

        self.selected_file = path
        self.attachment_label.value = name
        self.attachment_row.visible = True
        self.update()

    def clear_selected_file(self, e: ft.ControlEvent | None = None) -> None:
        """Clear the selected video file and reset the UI state."""

        self.selected_file = None
        self.attachment_label.value = ""
        self.attachment_row.visible = False
        self.update()

    def open_file_picker(self, e: ft.ControlEvent | None = None) -> None:
        """Open a file picker to select a local video file."""

        if not self.page.web and self.page.platform == ft.PagePlatform.MACOS:
            self.page.run_task(self._open_macos_file_dialog)
            return
        self._register_overlays()
        self.page.update()
        self.page.run_task(self._open_file_picker_async)

    async def _open_file_picker_async(self) -> None:
        """Open the standard file picker asynchronously."""

        await asyncio.sleep(0.05)
        self.file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.VIDEO,
        )

    async def _open_macos_file_dialog(self) -> None:
        """Open a native macOS file dialog for video selection."""

        path = await asyncio.to_thread(self._choose_file_macos)
        if path:
            self._apply_selected_file(path, os.path.basename(path))

    def _choose_file_macos(self) -> str | None:
        """Run AppleScript to open a macOS file chooser."""

        script = 'POSIX path of (choose file with prompt "Select a video file")'
        try:
            return subprocess.check_output(
                ["osascript", "-e", script],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return None

    def _add_message(self, author: str, text: str) -> ft.Text:
        """Append a message bubble to the chat history.

        Args:
            author: "user" or "assistant".
            text: Message content.

        Returns:
            The Text control used for the message content.
        """

        is_user = author == "user"
        max_width = self._bubble_max_width()
        text_control = ft.Text(
            text,
            selectable=True,
            color=theme.TEXT_PRIMARY,
            no_wrap=False,
            overflow=ft.TextOverflow.CLIP,
        )
        content_row = ft.Row(
            [text_control],
            wrap=False,
            scroll=ft.ScrollMode.ALWAYS,
            width=max_width,
            expand=True,
        )
        bubble = ft.Container(
            content=content_row,
            bgcolor=theme.BUTTON_PRIMARY_BG if is_user else theme.CARD_BG,
            padding=12,
            border_radius=12,
            border=ft.border.all(1, theme.BORDER_SOFT),
            width=max_width,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        text_control.data = {"bubble": bubble, "content_row": content_row}
        self._apply_text_layout(text_control, max_width)
        row = ft.Row(
            [bubble],
            alignment=(
                ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            ),
            expand=True,
        )
        self.chat_history.controls.append(row)
        self.chat_history.update()
        self._scroll_to_bottom()
        return text_control

    def _bubble_max_width(self) -> int:
        """Return the maximum width for chat bubbles.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view.page = type("P", (), {"width": 1000})()  # doctest: +SKIP
            >>> view._bubble_max_width()  # doctest: +SKIP
            680
        """

        viewport_width = self.page.width or 900
        available = max(
            viewport_width - theme.SIDEBAR_WIDTH - BUBBLE_PADDING_ALLOWANCE,
            BUBBLE_MIN_WIDTH,
        )
        scaled = int(available * BUBBLE_SCALE)
        return min(max(scaled, BUBBLE_MIN_WIDTH), BUBBLE_MAX_WIDTH)

    def _estimate_text_width(self, text: str, min_width: int) -> int:
        """Estimate a text width for horizontal scrolling.

        Args:
            text: Message content.
            min_width: Minimum width for the text container.

        Returns:
            Estimated pixel width for the longest line.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view._estimate_text_width("hello", 200)  # doctest: +SKIP
            200
        """

        max_line_len = max((len(line) for line in text.splitlines()), default=0)
        base_width = max_line_len * BUBBLE_CHAR_WIDTH + BUBBLE_HORIZONTAL_PADDING
        return max(min_width, min(base_width, BUBBLE_MAX_TEXT_WIDTH))

    def _needs_horizontal_scroll(self, text: str, max_width: int) -> bool:
        """Return True if the text should enable horizontal scrolling.

        Args:
            text: Message content.
            max_width: Current bubble max width.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view._needs_horizontal_scroll("short", 300)  # doctest: +SKIP
            False
        """

        return self._estimate_text_width(text, max_width) > max_width

    def _apply_text_layout(self, text_control: ft.Text, max_width: int) -> None:
        """Apply wrapping or horizontal scroll layout to a message.

        Args:
            text_control: The message text control to update.
            max_width: Current bubble max width.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> text = ft.Text("hello")  # doctest: +SKIP
            >>> view._apply_text_layout(text, 300)  # doctest: +SKIP
        """

        data = text_control.data or {}
        bubble = data.get("bubble")
        content_row = data.get("content_row")
        if bubble is None or content_row is None:
            return

        raw_text = text_control.value or ""
        if self._needs_horizontal_scroll(raw_text, max_width):
            text_control.no_wrap = True
            text_control.overflow = ft.TextOverflow.VISIBLE
            text_control.width = self._estimate_text_width(raw_text, max_width)
        else:
            text_control.no_wrap = False
            text_control.overflow = ft.TextOverflow.CLIP
            text_control.width = max_width

        content_row.width = max_width
        bubble.width = max_width

    def _update_message_layout(self, text_control: ft.Text) -> None:
        """Refresh layout for a message after text or size changes.

        Args:
            text_control: The text control to update.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> text = ft.Text("hello")  # doctest: +SKIP
            >>> view._update_message_layout(text)  # doctest: +SKIP
        """

        self._apply_text_layout(text_control, self._bubble_max_width())

    def _scroll_to_bottom(self) -> None:
        """Scroll the chat history to the latest message.

        Example:
            >>> view = ChatView.__new__(ChatView)  # doctest: +SKIP
            >>> view.chat_history = None  # doctest: +SKIP
            >>> view._scroll_to_bottom()  # doctest: +SKIP
        """

        self.chat_history.scroll_to(offset=1e9)

    def _set_busy(self, busy: bool) -> None:
        """Toggle UI busy state during streaming."""

        self.progress_bar.visible = busy
        self.status_text.value = "thinking" if busy else ""
        self.message_field.disabled = busy
        self.send_btn.disabled = busy
        self.update()

    async def send_message(self, e: ft.ControlEvent | None = None) -> None:
        """Send a message and stream the assistant response."""

        message = (self.message_field.value or "").strip()
        if not message:
            return

        self.message_field.value = ""
        self._add_message("user", message)
        assistant_text = self._add_message("assistant", "")
        self._set_busy(True)

        try:
            _, stream = await self.adk_helper.stream_chat(
                message, video_path=self.selected_file
            )
            async for chunk in stream:
                assistant_text.value = (assistant_text.value or "") + chunk
                self._update_message_layout(assistant_text)
                assistant_text.update()
                self._scroll_to_bottom()
                await asyncio.sleep(0)
        except Exception as ex:  # noqa: BLE001 - surface in UI
            assistant_text.value = f"Error: {ex}"
            self._update_message_layout(assistant_text)
            assistant_text.update()
        finally:
            self._set_busy(False)
            self.page.update()
