import flet as ft
from video_agent.ui.views.summarize import SummarizeView
from video_agent.ui.views.chat import ChatView
from video_agent.ui.views.events import EventsView
from video_agent.ui.views.transcribe import TranscribeView
from video_agent.ui.views.settings import SettingsView

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        
        # Current active view
        self.current_view = SummarizeView(self.page)
        self.view_container = ft.Container(
            content=self.current_view,
            expand=True,
            padding=20,
            bgcolor="grey200",
        )

        # Sidebar navigation
        self.sidebar = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.SUMMARIZE_OUTLINED, 
                    selected_icon=ft.Icons.SUMMARIZE, 
                    label="Summarize"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.CHAT_BUBBLE_OUTLINE, 
                    selected_icon=ft.Icons.CHAT_BUBBLE, 
                    label="Chat"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.EVENT_NOTE_OUTLINED, 
                    selected_icon=ft.Icons.EVENT_NOTE, 
                    label="Events"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.RECORD_VOICE_OVER_OUTLINED, 
                    selected_icon=ft.Icons.RECORD_VOICE_OVER, 
                    label="Transcribe"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED, 
                    selected_icon=ft.Icons.SETTINGS, 
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change,
        )

        self.controls = [self.sidebar, self.view_container]

    def on_nav_change(self, e):
        index = e.control.selected_index
        view = None
        
        if index == 0:
            view = SummarizeView(self.page)
        elif index == 1:
            view = ChatView(self.page)
        elif index == 2:
            view = EventsView(self.page)
        elif index == 3:
            view = TranscribeView(self.page)
        elif index == 4:
            view = SettingsView(self.page)
        
        if view:
            self.current_view = view
            self.view_container.content = view
            self.page.update()
