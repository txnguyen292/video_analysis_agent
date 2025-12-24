import flet as ft
from video_agent.ui.layout import AppLayout

def app_main(page: ft.Page):
    page.title = "Video Understanding Agent"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # Default Theme Color (customizable)
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    
    app = AppLayout(page)
    page.add(app)
    page.update()

def main():
    ft.app(target=app_main)

if __name__ == "__main__":
    main()
