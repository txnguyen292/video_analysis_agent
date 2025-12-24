import flet as ft
from video_agent.ui import theme
from video_agent.ui.views.summarize import SummarizeView
from video_agent.ui.views.chat import ChatView
from video_agent.ui.views.events import EventsView
from video_agent.ui.views.transcribe import TranscribeView
from video_agent.ui.views.settings import SettingsView

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, selected_index: int = 0):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 16
        self.selected_index = selected_index if selected_index in range(5) else 0
        self._view_classes = [
            SummarizeView,
            ChatView,
            EventsView,
            TranscribeView,
            SettingsView,
        ]
        
        # Current active view
        self.current_view = self._view_classes[self.selected_index](self.page)
        self.view_container = ft.Container(
            content=self.current_view,
            expand=True,
            padding=24,
            bgcolor=theme.PANEL_BG,
            border=ft.border.all(1, theme.BORDER),
            border_radius=18,
        )

        # Sidebar navigation
        self.sidebar = ft.NavigationRail(
            selected_index=self.selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            bgcolor="transparent",
            indicator_color=theme.NAV_INDICATOR,
            indicator_shape=ft.RoundedRectangleBorder(radius=12),
            selected_label_text_style=ft.TextStyle(
                color=theme.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600,
                size=12,
            ),
            unselected_label_text_style=ft.TextStyle(
                color=theme.TEXT_SECONDARY,
                size=12,
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.SUMMARIZE_OUTLINED, color=theme.NAV_ICON),
                    selected_icon=ft.Icon(ft.Icons.SUMMARIZE, color=theme.NAV_ICON_SELECTED),
                    label="Summarize"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=theme.NAV_ICON),
                    selected_icon=ft.Icon(ft.Icons.CHAT_BUBBLE, color=theme.NAV_ICON_SELECTED),
                    label="Chat"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, color=theme.NAV_ICON),
                    selected_icon=ft.Icon(ft.Icons.EVENT_NOTE, color=theme.NAV_ICON_SELECTED),
                    label="Events"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.RECORD_VOICE_OVER_OUTLINED, color=theme.NAV_ICON),
                    selected_icon=ft.Icon(ft.Icons.RECORD_VOICE_OVER, color=theme.NAV_ICON_SELECTED),
                    label="Transcribe"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=theme.NAV_ICON),
                    selected_icon=ft.Icon(ft.Icons.SETTINGS, color=theme.NAV_ICON_SELECTED),
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change,
        )

        self.sidebar_container = ft.Container(
            content=self.sidebar,
            padding=12,
            bgcolor=theme.NAV_BG,
            border=ft.border.all(1, theme.BORDER),
            border_radius=18,
        )

        self.controls = [self.sidebar_container, self.view_container]

    def on_nav_change(self, e):
        index = e.control.selected_index
        if index < 0 or index >= len(self._view_classes):
            return
        self.selected_index = index
        view = self._view_classes[index](self.page)
        self.current_view = view
        self.view_container.content = view
        self.page.update()
