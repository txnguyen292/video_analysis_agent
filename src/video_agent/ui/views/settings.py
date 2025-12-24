import flet as ft


class SettingsView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.spacing = 20
        
        self.theme_colors = {
            "Indigo": ft.Colors.INDIGO,
            "Blue": ft.Colors.BLUE,
            "Teal": ft.Colors.TEAL,
            "Green": ft.Colors.GREEN,
            "Purple": ft.Colors.PURPLE,
            "Orange": ft.Colors.ORANGE,
            "Pink": ft.Colors.PINK,
        }
        
        self.model_dropdown = ft.Dropdown(
            label="Gemini Model",
            value="gemini-3-pro",
            options=[
                ft.dropdown.Option("gemini-3-pro"),
                ft.dropdown.Option("gemini-3-flash"),
                ft.dropdown.Option("gemini-1.5-pro"),
            ],
            width=300,
            on_change=self.save_settings
        )
        
        self.theme_dropdown = ft.Dropdown(
            label="Accent Color",
            value="Indigo",
            options=[ft.dropdown.Option(c) for c in self.theme_colors.keys()],
            width=300,
            on_change=self.change_theme
        )
        
        self.controls = [
            ft.Text("Settings", size=30, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Agent Configuration", size=20, weight=ft.FontWeight.W_500),
            self.model_dropdown,
            ft.Divider(),
            ft.Text("Appearance", size=20, weight=ft.FontWeight.W_500),
            self.theme_dropdown,
        ]

    def change_theme(self, e):
        color_name = self.theme_dropdown.value
        if color_name in self.theme_colors:
            self.page.theme = ft.Theme(color_scheme_seed=self.theme_colors[color_name])
            self.page.update()
            
    def save_settings(self, e):
        # TODO: Persist to config.yaml
        pass
