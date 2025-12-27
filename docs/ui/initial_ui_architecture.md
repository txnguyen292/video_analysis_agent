# Video Agent UI Architecture

This document outlines the design and implementation details of the graphical user interface (GUI) for the Video Understanding Agent.

## Overview
The UI is built using **Flet**, a framework that allows building interactive multi-platform apps in Python (powered by Flutter). The design prioritizes responsiveness, ease of use, and a modern dark-themed aesthetic.

## Architecture

### Directory Structure
The UI code is modularized within `ui/src/personal_assistant_ui/`:
```
ui/src/personal_assistant_ui/
├── app.py              # Application entry point and theme configuration
├── layout.py           # Main AppLayout component handling global navigation
├── agent_helper.py     # Bridge between UI and core Video Agent logic (Async)
└── views/              # Individual screens/pages
    ├── summarize.py    # Video Summarization view
    ├── chat.py         # Chat Q&A view
    ├── events.py       # Event Detection view
    ├── transcribe.py   # Transcription view
    └── settings.py     # Configuration settings
```

### Key Components

#### 1. Entry Point (`app.py`)
- Initializes the Flet `Page`.
- Sets global properties like Title, Theme Mode (Dark), and default Tint Color (Indigo).
- Mounts the `AppLayout`.

#### 2. Layout & Navigation (`layout.py`)
- **`AppLayout`**: A custom control inheriting from `ft.Row`.
- **NavigationRail**: A sidebar on the left for switching between views.
- **View Container**: A main content area that dynamically swaps controls based on the selected navigation index.
- **State Management**: Updates the `current_view` and calls `page.update()` to refresh the UI on navigation changes.

#### 3. Agent Integration (`agent_helper.py`)
- **Purpose**: Decouples the blocking Video Agent API calls from the UI thread.
- **Mechanism**: specific methods (`analyze_video`, `ask_question`, etc.) use `asyncio.to_thread` to run the heavy processing in a separate thread, keeping the UI responsive (e.g., updating progress bars).
- **Configuration**: Loads initial settings from `config.yaml`.

#### 4. Views (`views/*.py`)
Each view follows a consistent pattern:
- **FilePicker**: For selecting video files (`ft.FilePicker`).
- **Input Area**: Drag-and-drop zone or upload button.
- **Action Button**: Triggers the async agent operation.
- **Progress Indicators**: `ft.ProgressBar` and status text to inform the user.
- **Results Display**: `ft.Markdown` component to render the agent's output nicely.
- **Save Output**: A dedicated button to save the result text to a local file.

### Design Decisions

- **Asynchronous Processing**: Essential for Video Agent operations that can take minutes. Flet's async support is leveraged to ensure the window doesn't freeze.
- **Separate View Files**: Keeps code manageable and allows for independent maintenance of each feature's UI logic.
- **Shared Theme**: Theme colors are managed globally in `app.py` but can be updated at runtime via `SettingsView`.
- **Hot-Reload Ready**: The structure supports `flet run` for rapid development and testing.

## Future Improvements
- **Drag & Drop**: Native file drag-and-drop support (currently uses a click-to-browse trigger).
- **History**: Persisting session history for chat and summaries.
- **Real-time Streaming**: Streaming Gemini responses token-by-token if the API supports it.
