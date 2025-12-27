import flet as ft

# Base background colors and gradients for the app shell.
BG_COLOR = "#0B0F17"
BG_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=["#1A2230", "#0B0F17"],
)
GLOW_GRADIENT = ft.RadialGradient(
    center=ft.alignment.top_left,
    radius=1.2,
    colors=["#33405C80", "#00000000"],
    stops=[0.0, 1.0],
)

# Surface colors for panels, cards, and inputs.
PANEL_BG = "#80131B27"
CARD_BG = "#99172232"
CARD_BG_SOLID = "#141C28"
RESULT_BG = "#CC0F1624"
INPUT_BG = "#162033"
BUTTON_SECONDARY_BG = "#1A2434"
BUTTON_DISABLED_BG = "#263247"

# Borders and separators.
BORDER = "#2A3A52"
BORDER_SOFT = "#1F2A3B"

# Text hierarchy colors.
TEXT_PRIMARY = "#E7EDF7"
TEXT_SECONDARY = "#B4C0D4"
TEXT_MUTED = "#7C8AA3"
TEXT_DIM = "#5E6B82"

# Accent presets control highlight and CTA colors.
DEFAULT_ACCENT_NAME = "Blue"
ACCENT_PRESETS = {
    "Indigo": {
        "accent": "#7C8CFF",
        "accent_soft": "#3A3F6D",
        "button_primary_bg": "#5C6BFF",
        "drop_border": "#5F6CA3",
    },
    "Blue": {
        "accent": "#6EA8FF",
        "accent_soft": "#345280",
        "button_primary_bg": "#4F86FF",
        "drop_border": "#5A7DB3",
    },
    "Teal": {
        "accent": "#5FD2C5",
        "accent_soft": "#2E5B5E",
        "button_primary_bg": "#2FBFAE",
        "drop_border": "#4A9FA0",
    },
    "Green": {
        "accent": "#7FE3A1",
        "accent_soft": "#2F5A43",
        "button_primary_bg": "#4BCB7A",
        "drop_border": "#4F8F6B",
    },
    "Purple": {
        "accent": "#B08CFF",
        "accent_soft": "#3F3358",
        "button_primary_bg": "#8B5CF6",
        "drop_border": "#6F5AA0",
    },
    "Orange": {
        "accent": "#F2B66E",
        "accent_soft": "#5B4331",
        "button_primary_bg": "#E58B3E",
        "drop_border": "#9C6D44",
    },
    "Pink": {
        "accent": "#FF9BC9",
        "accent_soft": "#5B3A4A",
        "button_primary_bg": "#F46AA3",
        "drop_border": "#9A5B76",
    },
}

# Active accent values (mutable via apply_accent).
CURRENT_ACCENT_NAME = DEFAULT_ACCENT_NAME
ACCENT = ACCENT_PRESETS[DEFAULT_ACCENT_NAME]["accent"]
ACCENT_SOFT = ACCENT_PRESETS[DEFAULT_ACCENT_NAME]["accent_soft"]
BUTTON_PRIMARY_BG = ACCENT_PRESETS[DEFAULT_ACCENT_NAME]["button_primary_bg"]
DROP_BORDER = ACCENT_PRESETS[DEFAULT_ACCENT_NAME]["drop_border"]

# Status colors for success/warning/error states.
SUCCESS = "#7FE3A1"
WARNING = "#F4C676"
DANGER = "#FF8B8B"

# Navigation colors.
NAV_BG = "#80101924"
NAV_INDICATOR = "#2A3952"
NAV_ICON = "#A1AEC4"
NAV_ICON_SELECTED = "#E7EDF7"


def apply_accent(name: str) -> str:
    # Updates the active accent variables used throughout the UI.
    preset = ACCENT_PRESETS.get(name)
    if not preset:
        return DEFAULT_ACCENT_NAME
    global ACCENT, ACCENT_SOFT, BUTTON_PRIMARY_BG, DROP_BORDER, CURRENT_ACCENT_NAME
    ACCENT = preset["accent"]
    ACCENT_SOFT = preset["accent_soft"]
    BUTTON_PRIMARY_BG = preset["button_primary_bg"]
    DROP_BORDER = preset["drop_border"]
    CURRENT_ACCENT_NAME = name
    return name


def markdown_style() -> ft.MarkdownStyleSheet:
    return ft.MarkdownStyleSheet(
        p_text_style=ft.TextStyle(color=TEXT_PRIMARY, size=14),
        a_text_style=ft.TextStyle(color=ACCENT),
        h1_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=22, weight=ft.FontWeight.BOLD
        ),
        h2_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.BOLD
        ),
        h3_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.BOLD
        ),
        h4_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=15, weight=ft.FontWeight.BOLD
        ),
        h5_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.BOLD
        ),
        h6_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.BOLD
        ),
        code_text_style=ft.TextStyle(color=TEXT_PRIMARY),
        blockquote_text_style=ft.TextStyle(color=TEXT_SECONDARY),
        list_bullet_text_style=ft.TextStyle(color=TEXT_PRIMARY),
        table_head_text_style=ft.TextStyle(
            color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD
        ),
        table_body_text_style=ft.TextStyle(color=TEXT_SECONDARY),
    )
