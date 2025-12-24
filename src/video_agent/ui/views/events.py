import flet as ft
from video_agent.ui.agent_helper import AgentHelper
import asyncio
import os
import subprocess

class EventsView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.agent_helper = AgentHelper()
        self.selected_file = None
        self.save_default_name = "events.md"
        
        # Component Reuse (Ideally refactor to base class, but keeping simple for now)
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.save_file_picker = ft.FilePicker(on_result=self.on_save_result)

        self.upload_area = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=50, color=ft.Colors.PRIMARY),
                ft.Text("Drag & Drop Video Here", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("or click to browse", color=ft.Colors.GREY_400),
                ft.Text("No file selected", key="file_status", color=ft.Colors.GREY_500)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.border.all(2, ft.Colors.PRIMARY),
            border_radius=10,
            padding=40,
            alignment=ft.alignment.center,
            ink=True,
            on_click=self.open_file_picker,
        )

        self.browse_btn = ft.OutlinedButton(
            "Browse Video",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.open_file_picker,
        )
        
        self.process_btn = ft.ElevatedButton(
            "Detect Events", 
            icon=ft.Icons.SEARCH, 
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=20),
            on_click=self.process_video,
            disabled=True
        )
        
        self.progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee", visible=False)
        self.status_text = ft.Text("", color=ft.Colors.GREY_400)
        
        self.result_markdown = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        )
        
        self.save_btn = ft.ElevatedButton(
            "Save Events", icon=ft.Icons.SAVE, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, visible=False,
            on_click=self.open_save_dialog
        )

        self.results_container = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Detected Events", size=20, weight=ft.FontWeight.BOLD), self.save_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=self.result_markdown,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    bgcolor=ft.Colors.BLACK12,
                    expand=True
                )
            ]),
            visible=False,
            expand=True
        )

        self.controls = [
            ft.Text("Event Detection", size=30, weight=ft.FontWeight.BOLD),
            self.upload_area,
            ft.Row([self.browse_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.process_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Column([self.progress_bar, self.status_text], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            self.results_container
        ]

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._apply_selected_file(e.files[0].path, e.files[0].name)

    def _apply_selected_file(self, path: str, name: str):
        self.selected_file = path
        self.upload_area.content.controls[3].value = name
        self.upload_area.content.controls[3].color = ft.Colors.GREEN
        self.upload_area.update()
        self.process_btn.disabled = False
        self.process_btn.update()

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

    def _choose_file_macos(self):
        script = 'POSIX path of (choose file with prompt "Select a video file")'
        try:
            return subprocess.check_output(["osascript", "-e", script], text=True).strip()
        except subprocess.CalledProcessError:
            return None

    async def process_video(self, e):
        if not self.selected_file: return
        self.process_btn.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "Detecting events..."
        self.results_container.visible = False
        self.update()
        try:
            result_text, stats, elapsed = await self.agent_helper.analyze_video(self.selected_file, 'events')
            self.result_markdown.value = result_text
            self.results_container.visible = True
            self.save_btn.visible = True
            self.status_text.value = f"Completed in {elapsed:.1f}s | Cost: ${stats.estimated_cost:.4f}"
            self.status_text.color = ft.Colors.GREEN
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED
        self.process_btn.disabled = False
        self.progress_bar.visible = False
        self.update()

    def on_save_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._write_result(e.path)

    def _write_result(self, path: str):
        with open(path, 'w') as f:
            f.write(self.result_markdown.value or "")
        self.status_text.value = f"Saved to {path}"
        self.status_text.color = ft.Colors.GREEN
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
            return subprocess.check_output(["osascript", "-e", script], text=True).strip()
        except subprocess.CalledProcessError:
            return None

    def _show_snack(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
