import flet as ft
from personal_assistant_ui import theme
from personal_assistant_ui.config import load_ui_config
from personal_assistant.main import load_config


class SettingsView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.spacing = 20
        
        self.theme_colors = theme.ACCENT_PRESETS
        ui_config = load_ui_config()
        core_config = load_config()
        default_model = ui_config.get("model") or core_config.get("model") or "gemini-3-flash"
        default_theme = ui_config.get("theme") or theme.CURRENT_ACCENT_NAME
        
        self.model_dropdown = ft.Dropdown(
            label="Gemini Model",
            value=default_model,
            options=[
                ft.dropdown.Option("gemini-3-flash"),
                ft.dropdown.Option("gemini-3-pro"),
                ft.dropdown.Option("gemini-1.5-pro"),
            ],
            width=300,
            bgcolor=theme.INPUT_BG,
            border_color=theme.BORDER,
            focused_border_color=theme.ACCENT,
            color=theme.TEXT_PRIMARY,
            label_style=ft.TextStyle(color=theme.TEXT_SECONDARY),
            on_change=self.save_settings
        )
        
        self.theme_dropdown = ft.Dropdown(
            label="Accent Color",
            value=default_theme,
            options=[ft.dropdown.Option(c) for c in self.theme_colors.keys()],
            width=300,
            bgcolor=theme.INPUT_BG,
            border_color=theme.BORDER,
            focused_border_color=theme.ACCENT,
            color=theme.TEXT_PRIMARY,
            label_style=ft.TextStyle(color=theme.TEXT_SECONDARY),
            on_change=self.change_theme
        )
        
        self.controls = [
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
            ft.Divider(color=theme.BORDER_SOFT),
            ft.Text("Agent Configuration", size=20, weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY),
            self.model_dropdown,
            ft.Divider(color=theme.BORDER_SOFT),
            ft.Text("Appearance", size=20, weight=ft.FontWeight.W_500, color=theme.TEXT_PRIMARY),
            self.theme_dropdown,
        ]

    def change_theme(self, e):
        color_name = self.theme_dropdown.value
        applied_name = theme.apply_accent(color_name)
        self.page.theme = ft.Theme(color_scheme_seed=theme.ACCENT)
        if hasattr(self.page, "rebuild_app"):
            selected_index = 4
            if hasattr(self.page, "app_layout"):
                selected_index = getattr(self.page.app_layout, "selected_index", 4)
            self.page.rebuild_app(selected_index=selected_index)
        else:
            self.page.update()
            
    def save_settings(self, e):
        # TODO: Persist to config.yaml
        pass
