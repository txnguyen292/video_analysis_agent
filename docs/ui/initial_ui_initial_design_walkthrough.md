# Video Understanding Agent Walkthrough

I have built a robust video understanding agent that leverages Google **Gemini 3 Pro** (the latest flagship model) for deep reasoning over video content.

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
video_agent/
├── .env                  # Added manually (contains GOOGLE_API_KEY)
├── pyproject.toml        # uv-managed dependencies + CLI entry point
├── src/
│   └── video_agent/
│       ├── __init__.py
│       ├── agent.py      # High-level logic
│       ├── client.py     # Gemini API wrapper
│       ├── main.py       # Typer CLI entry point
│       └── usage.py      # Token cost calculator
└── tests/
```

## How to Run

1. **Setup Environment**:
   ```bash
   cd video_agent
   uv sync
   # Ensure GOOGLE_API_KEY is in your .env file
   ```

2. **Run the CLI**:
   Once synced, you can use `uv run video-agent` directly:
   ```bash
   # Summarize a long video using Gemini 3 Pro (default)
   uv run video-agent summarize path/to/video.mp4

   # Transcribe and diarize audio and save to file
   uv run video-agent transcribe path/to/video.mp4 --output transcript.txt

   # Ask a question and measure time
   uv run video-agent ask path/to/video.mp4 "What is the key message?" -o answer.md
   ```

3. **Using Configuration File**:
   Create a `config.yaml` to set defaults:
   ```yaml
   video_path: "path/to/default_video.mp4"
   model: "gemini-3-pro"
   output: "results/output.md"
   ```
   Now you can run commands without arguments:
   ```bash
   uv run video-agent summarize
   ```bash
   uv run video-agent summarize --config my_config.yaml
   ```

4. **Running the Graphical UI**:
   To launch the new Flet-based desktop application:
   ```bash
   uv run flet run src/video_agent/ui/app.py
   ```
   **Note**: Using `flet run` ensures automatic hot-reloading during development.
   
   Or specify a custom config file:
   ```bash
   uv run video-agent summarize --config my_config.yaml
   ```

## Demonstration
(Since I cannot run with live video here, I've verified the code structure and logic).
