# Video Understanding Agent Walkthrough

I have built a robust video understanding agent that leverages Google's **Gemini 3** family (defaulting to **Gemini 3 Flash**) for deep reasoning over video content.

## Features
- **Native Video Processing**: Uploads videos to Gemini's Files API for analysis.
- **Polished CLI**: Built with `typer` and `rich` for a premium terminal experience.
- **Detailed Logging**: Uses `loguru` for clear progress tracking.
- **YAML Configuration**: Load default arguments from a `config.yaml` file to simplify repetitive runs.
- **Smart Output Path**: Automatically names output files based on the input video if a directory is provided.
- **Execution Timer**: Tracks and displays the total duration of each operation.
- **Output Saving**: Save command outputs to a file using the `--output` or `-o` flag.
- **Token Usage & Cost**: Automatically tracks token usage and estimates costs for each operation.
- **Versatile Tasking**: Supports summarization, specific questions, and event detection.

## Project Structure
```text
personal_assistant/
├── .env                  # Added manually (contains GOOGLE_API_KEY)
├── core/
│   ├── pyproject.toml    # Core dependencies + CLI entry point
│   └── src/personal_assistant/
│       ├── __init__.py
│       ├── agent.py      # High-level logic
│       ├── client.py     # Gemini API wrapper
│       ├── main.py       # Typer CLI entry point
│       └── usage.py      # Token cost calculator
├── ui/
│   ├── pyproject.toml    # UI dependencies + Flet entry point
│   └── src/personal_assistant_ui/
│       ├── app.py
│       ├── layout.py
│       └── views/
└── tests/
```

## How to Run

1. **Setup Environment**:
   ```bash
   cd personal_assistant/core
   uv sync
   # Ensure GOOGLE_API_KEY is in your .env file
   ```

2. **Run the CLI**:
   Once synced, you can use `uv run personal-assistant` directly:
   ```bash
   # Summarize a long video using Gemini 3 Flash (default)
   uv run personal-assistant summarize path/to/video.mp4

   # Transcribe and diarize audio and save to file
   uv run personal-assistant transcribe path/to/video.mp4 --output transcript.txt

   # Ask a question and measure time
   uv run personal-assistant ask path/to/video.mp4 "What is the key message?" -o answer.md
   ```

3. **Using Configuration File**:
   Create a `config.yaml` to set defaults:
   ```yaml
   video_path: "path/to/default_video.mp4"
   model: "gemini-3-flash"
   output: "results/output.md"
   ```
   Now you can run commands without arguments:
   ```bash
   uv run personal-assistant summarize
   uv run personal-assistant summarize --config my_config.yaml
   ```

4. **Running the Graphical UI**:
   To launch the new Flet-based desktop application:
   ```bash
   cd ../ui
   uv run flet run src/personal_assistant_ui/app.py
   ```
   **Note**: Using `flet run` ensures automatic hot-reloading during development.
   
   Or specify a custom config file:
   ```bash
   uv run personal-assistant summarize --config my_config.yaml
   ```

## Demonstration
(Since I cannot run with live video here, I've verified the code structure and logic).
