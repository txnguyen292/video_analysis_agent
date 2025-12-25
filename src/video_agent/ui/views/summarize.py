import flet as ft
from video_agent.ui.agent_helper import AgentHelper
from video_agent.ui import theme
import asyncio
import os
import subprocess

class SummarizeView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.agent_helper = AgentHelper()
        self.selected_file = None
        self.selected_file_name = None
        self.selected_file_size = None
        self.save_default_name = "summary.md"
        self._replace_pending = False
        
        # UI Components
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.save_file_picker = ft.FilePicker(on_result=self.on_save_result)

        self.upload_area = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=50, color=theme.ACCENT),
                ft.Text("Drop video to summarize", size=18, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                ft.Text("Drag a file here or browse", color=theme.TEXT_SECONDARY),
                ft.Text("No file selected", key="file_status", color=theme.TEXT_MUTED)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.border.all(1, theme.DROP_BORDER),
            border_radius=18,
            padding=36,
            bgcolor=theme.CARD_BG,
            alignment=ft.alignment.center,
            ink=True,
            on_click=self.open_file_picker,
            on_hover=self._on_upload_hover,
            animate=ft.Animation(200, "easeOut"),
        )

        self.browse_btn = ft.OutlinedButton(
            "Browse Video",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.open_file_picker,
            style=ft.ButtonStyle(
                color=theme.TEXT_PRIMARY,
                bgcolor=theme.BUTTON_SECONDARY_BG,
                side=ft.BorderSide(1, theme.BORDER),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
        )
        
        self.process_btn = ft.ElevatedButton(
            "Process Video", 
            icon=ft.Icons.PLAY_ARROW, 
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=26, vertical=14),
                color=ft.Colors.WHITE,
                bgcolor={ft.ControlState.DISABLED: theme.BUTTON_DISABLED_BG, "": theme.BUTTON_PRIMARY_BG},
            ),
            on_click=self.process_video,
            disabled=True
        )

        self.processed_title = ft.Text(
            "Video processed",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=theme.TEXT_PRIMARY,
        )
        self.processed_file_text = ft.Text(
            "No file selected",
            color=theme.TEXT_SECONDARY,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.processed_header = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.CHECK, size=16, color=theme.BG_COLOR),
                    width=24,
                    height=24,
                    bgcolor=theme.SUCCESS,
                    border_radius=12,
                    alignment=ft.alignment.center,
                ),
                self.processed_title,
            ],
            spacing=10,
        )
        self.processed_info = ft.Column(
            [self.processed_header, self.processed_file_text],
            spacing=6,
            expand=True,
        )
        self.replace_btn = ft.OutlinedButton(
            "Replace video",
            icon=ft.Icons.SWAP_HORIZ,
            on_click=self._on_replace_video,
            style=ft.ButtonStyle(
                color=theme.TEXT_PRIMARY,
                bgcolor=theme.BUTTON_SECONDARY_BG,
                side=ft.BorderSide(1, theme.BORDER),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
        )
        self.processed_process_btn = ft.ElevatedButton(
            "Process",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.process_video,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                color=ft.Colors.WHITE,
                bgcolor={ft.ControlState.DISABLED: theme.BUTTON_DISABLED_BG, "": theme.BUTTON_PRIMARY_BG},
            ),
            disabled=True,
        )
        self.processed_actions = ft.Row(
            [self.replace_btn, self.processed_process_btn],
            spacing=12,
            alignment=ft.MainAxisAlignment.END,
        )
        self.processed_section = ft.Container(
            content=ft.Row(
                [self.processed_info, self.processed_actions],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            bgcolor=theme.CARD_BG,
            border=ft.border.all(1, theme.BORDER),
            border_radius=18,
            visible=False,
        )
        
        self.progress_bar = ft.ProgressBar(width=400, color=theme.ACCENT, bgcolor=theme.BORDER_SOFT, visible=False)
        self.status_text = ft.Text("", color=theme.TEXT_MUTED)
        
        self.result_markdown = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            md_style_sheet=theme.markdown_style(),
            on_tap_link=lambda e: self.page.launch_url(e.data),
        )
        
        self.save_btn = ft.ElevatedButton(
            "Save Results",
            icon=ft.Icons.SAVE,
            bgcolor=theme.SUCCESS,
            color=theme.BG_COLOR,
            visible=False,
            on_click=self.open_save_dialog
        )

        self.results_header = ft.Row(
            [
                ft.Text("Results", size=20, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                self.save_btn,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.results_body = ft.Container(
            content=ft.Column(
                [self.result_markdown],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            border_radius=12,
            padding=20,
            bgcolor=theme.RESULT_BG,
            border=ft.border.all(1, theme.BORDER_SOFT),
            expand=True,
        )
        self.results_container = ft.Container(
            content=ft.Column(
                [self.results_header, self.results_body],
                expand=True,
            ),
            visible=False,
            expand=True,
            padding=ft.padding.only(top=20),
            bgcolor=theme.CARD_BG,
            border=ft.border.all(1, theme.BORDER),
            border_radius=18,
        )

        self.pre_process_section = ft.Column(
            [
                self.upload_area,
                ft.Row([self.browse_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.process_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=16,
        )

        self.controls = [
            ft.Text("Summarize Video", size=28, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
            self.pre_process_section,
            self.processed_section,
            ft.Column([self.progress_bar, self.status_text], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            self.results_container
        ]

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._apply_selected_file(e.files[0].path, e.files[0].name)
            return
        if self._replace_pending:
            self._replace_pending = False

    def _apply_selected_file(self, path: str, name: str):
        self.selected_file = path
        self.selected_file_name = name
        self.selected_file_size = self._get_file_size_label(path)
        # Update upload area text (naive way roughly)
        self.upload_area.content.controls[3].value = name
        self.upload_area.content.controls[3].color = theme.SUCCESS
        self.upload_area.update()
        self.processed_file_text.value = self._format_file_label(name, self.selected_file_size)
        self.processed_file_text.update()
        self.process_btn.disabled = False
        self.process_btn.update()
        self.processed_process_btn.disabled = False
        self.processed_process_btn.update()
        if self._replace_pending:
            self._replace_pending = False
            self._set_processed_title("Video selected")
            self.results_container.visible = False
            self.save_btn.visible = False
            self.status_text.value = ""
            self.status_text.color = theme.TEXT_MUTED
            self._toggle_sections(show_processed=True)
            self.update()

    def _on_upload_hover(self, e):
        self.upload_area.border = ft.border.all(
            1,
            theme.TEXT_PRIMARY if e.data == "true" else theme.DROP_BORDER
        )
        self.upload_area.update()

    def _register_overlays(self):
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
        if self.save_file_picker not in self.page.overlay:
            self.page.overlay.append(self.save_file_picker)

    def _unregister_overlays(self):
        if self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)
        if self.save_file_picker in self.page.overlay:
            self.page.overlay.remove(self.save_file_picker)

    def did_mount(self):
        self._register_overlays()
        self.page.update()

    def will_unmount(self):
        self._unregister_overlays()

    def open_file_picker(self, e=None):
        if not self.page.web and self.page.platform == ft.PagePlatform.MACOS:
            self.page.run_task(self._open_macos_file_dialog)
            return
        self._register_overlays()
        if os.getenv("UI_DEBUG"):
            self._show_snack("Opening file picker...")
        self.page.update()
        self.page.run_task(self._open_file_picker_async)

    async def _open_file_picker_async(self):
        await asyncio.sleep(0.05)
        self.file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.VIDEO,
        )

    async def _open_macos_file_dialog(self):
        path = await asyncio.to_thread(self._choose_file_macos)
        if path:
            self._apply_selected_file(path, os.path.basename(path))
        elif self._replace_pending:
            self._replace_pending = False

    def _choose_file_macos(self):
        script = 'POSIX path of (choose file with prompt "Select a video file")'
        try:
            return subprocess.check_output(
                ["osascript", "-e", script],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return None

    def _toggle_sections(self, show_processed: bool):
        self.pre_process_section.visible = not show_processed
        self.processed_section.visible = show_processed

    def _set_processed_title(self, title: str):
        self.processed_title.value = title
        self.processed_title.update()

    def _format_file_label(self, name: str, size_label: str | None) -> str:
        if size_label:
            return f"{name} ({size_label})"
        return name

    def _get_file_size_label(self, path: str) -> str | None:
        try:
            size_bytes = os.path.getsize(path)
        except OSError:
            return None
        return self._format_bytes(size_bytes)

    def _format_bytes(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        return f"{size_bytes / (1024 ** 3):.1f} GB"

    def _on_replace_video(self, e=None):
        self._replace_pending = True
        self.open_file_picker()

    async def process_video(self, e):
        if not self.selected_file:
            return
            
        self.process_btn.disabled = True
        self.processed_process_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Uploading and processing video... (this may take a minute)"
        self.status_text.color = theme.TEXT_MUTED
        self.results_container.visible = False
        self.save_btn.visible = False
        self.update()
        
        try:
            result_text, stats, elapsed = await self.agent_helper.analyze_video(self.selected_file, 'summarize')
            
            self.result_markdown.value = result_text
            self.results_container.visible = True
            self.save_btn.visible = True
            self._set_processed_title("Video processed")
            self._toggle_sections(show_processed=True)
            self.status_text.value = f"Completed in {elapsed:.1f}s | Cost: ${stats.estimated_cost:.4f}"
            self.status_text.color = theme.SUCCESS
            
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = theme.DANGER
        
        self.process_btn.disabled = False
        self.processed_process_btn.disabled = False
        self.progress_bar.visible = False
        self.update()

    def on_save_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._write_result(e.path)

    def _write_result(self, path: str):
        with open(path, 'w') as f:
            f.write(self.result_markdown.value or "")
        self.status_text.value = f"Saved to {path}"
        self.status_text.color = theme.SUCCESS
        self.status_text.update()
        self._show_snack(f"Saved to {path}")

    def open_save_dialog(self, e=None):
        if not self.page.web and self.page.platform == ft.PagePlatform.MACOS:
            self.page.run_task(self._open_macos_save_dialog)
            return
        self._register_overlays()
        self.page.update()
        self.save_file_picker.save_file(file_name=self.save_default_name)

    async def _open_macos_save_dialog(self):
        path = await asyncio.to_thread(self._choose_save_macos, self.save_default_name)
        if path:
            self._write_result(path)

    def _choose_save_macos(self, default_name: str):
        safe_name = default_name.replace('"', '\\"')
        script = f'POSIX path of (choose file name with prompt "Save results" default name "{safe_name}")'
        try:
            return subprocess.check_output(
                ["osascript", "-e", script],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return None

    def _show_snack(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message, color=theme.TEXT_PRIMARY), bgcolor=theme.CARD_BG_SOLID)
        self.page.snack_bar.open = True
        self.page.update()
