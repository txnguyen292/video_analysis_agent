import flet as ft
from video_agent.ui.layout import AppLayout
from video_agent.ui import theme

def app_main(page: ft.Page):
    page.title = "Video Understanding Agent"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    page.bgcolor = theme.BG_COLOR
    page.theme = ft.Theme(color_scheme_seed=theme.ACCENT)

    app = AppLayout(page)
    page.app_layout = app
    app_container = ft.Container(expand=True, padding=24, content=app)
    page.app_container = app_container

    def rebuild_app(selected_index=None):
        index = selected_index
        if index is None and hasattr(page, "app_layout"):
            index = getattr(page.app_layout, "selected_index", 0)
        app_layout = AppLayout(page, selected_index=index or 0)
        page.app_layout = app_layout
        page.app_container.content = app_layout
        page.update()

    page.rebuild_app = rebuild_app
    root = ft.Stack(
        [
            ft.Container(expand=True, gradient=theme.BG_GRADIENT),
            ft.Container(expand=True, gradient=theme.GLOW_GRADIENT, opacity=0.6),
            app_container,
        ],
        expand=True,
    )
    page.add(root)
    page.update()

def main():
    ft.app(target=app_main)

if __name__ == "__main__":
    main()
