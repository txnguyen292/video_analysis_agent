# Video Understanding Agent

A powerful command-line interface (CLI) tool that leverages Google's **Gemini 3 Pro** multimodal models to analyze, understand, and extract insights from video content.

## Features

- **Summarization**: Generate concise, timestamped summaries of video content.
- **Q&A**: Ask specific questions about visual and audio elements in the video.
- **Event Detection**: Identify significant events and actions with precise timestamps.
- **Transcription & Diarization**: Transcribe audio and distinguish between different speakers.
- **Cost & Token Tracking**: Automatically tracks token usage and provides cost estimates for each operation.
- **Execution Timer**: Displays the total time taken for upload and processing.
- **Smart Output Management**: Automatically saves results to files, resolving directory paths using the input video's filename.
- **Configuration Support**: Use a `config.yaml` file to set default arguments and avoid repetitive typing.

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (for dependency management)
- A Google Cloud API Key with access to Gemini models.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd video_agent
    ```

2.  **Install dependencies:**
    This project uses `uv` for fast dependency management.
    ```bash
    uv sync
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory:
    ```bash
    touch .env
    ```
    Add your Google API key to `.env`:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

## Usage

You can run the agent using `uv run`:

```bash
uv run video-agent [COMMAND] [ARGS]
```

### Commands

#### 1. Summarize a Video
Generate a comprehensive summary of the video content.
```bash
uv run video-agent summarize path/to/video.mp4
```

#### 2. Ask Questions
Ask specific questions about what's happening in the video.
```bash
uv run video-agent ask path/to/video.mp4 "What is the speaker wearing?"
```

#### 3. Detect Events
List significant events with timestamps.
```bash
uv run video-agent events path/to/video.mp4
```

#### 4. Transcribe and Diarize
Get a timestamped transcript with speaker labels.
```bash
uv run video-agent transcribe path/to/video.mp4
```

#### 5. Graphical User Interface (GUI)
Launch the desktop application with hot-reloading:
```bash
uv run flet run src/video_agent/ui/app.py
```
This opens a window where you can drag-and-drop videos, chat, and save results.

### Options

- `--model`: Specify the Gemini model ID (default: `gemini-3-pro`).
- `--output` / `-o`: Save the output to a specific file or directory.
- `--config` / `-c`: Path to a custom YAML configuration file (default: `config.yaml`).

## Configuration

You can define default values for arguments in a `config.yaml` file to simplify your workflow. The CLI will automatically look for this file in the current directory.

**Example `config.yaml`:**
```yaml
# Default configuration
video_path: "data/my_speech.mp4"
model: "gemini-3-pro"
output: "results/"  # Will save as results/my_speech.md
```

With this config, you can simply run:
```bash
uv run video-agent summarize
```

### Smart Output Path Resolution

If the `--output` argument (or config value) is a directory (e.g., `outputs/`), the agent will automatically save the result as a Markdown file with the same name as the input video.

Example:
- Input: `data/meeting_recording.mp4`
- Output Arg: `results/`
- Result Saved To: `results/meeting_recording.md`

## Project Structure

```text
video_agent/
├── .env                  # API Credentials
├── config.yaml           # Optional configuration
├── pyproject.toml        # Project dependencies and metadata
├── README.md             # Project documentation
├── src/
│   └── video_agent/
│       ├── main.py       # CLI Entry Point
│       ├── client.py     # Gemini API Client
│       ├── agent.py      # Agent Logic & Prompts
│       └── usage.py      # Token & Cost Tracking
```
