import time
from pathlib import Path

import typer
import yaml
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from loguru import logger
from personal_assistant.client import GeminiVideoClient
from personal_assistant.agent import VideoAgent
import os

app = typer.Typer(help="Video Understanding Agent CLI")
console = Console()


def get_agent(model_id: str):
    # Map friendly names to actual API IDs
    if model_id == "gemini-3-pro":
        model_id = "gemini-3-pro-preview"
    elif model_id == "gemini-3-flash":
        model_id = "gemini-3-flash-preview"

    client = GeminiVideoClient(model_id=model_id)
    return VideoAgent(client)

from personal_assistant.usage import UsageTracker

def display_response(
    response, client, title, style, elapsed_time: float, output_path: str | None = None
):
    console.print(Panel(response.text, title=title, border_style=style))

    if output_path:
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(response.text, encoding="utf-8")
            console.print(f"\n[bold green]Output saved to: {path}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]Failed to save output: {e}[/bold red]")

    stats = UsageTracker.extract_usage(response, client.model_id)

    table = Table(title="Token Usage & Cost", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Input Tokens", f"{stats.prompt_token_count:,}")
    table.add_row("Output Tokens", f"{stats.candidates_token_count:,}")
    table.add_row("Total Tokens", f"{stats.total_token_count:,}")
    table.add_row("Estimated Cost", f"${stats.estimated_cost:.4f}")
    table.add_row("Execution Time", f"{elapsed_time:.2f}s")

    console.print(table)

import yaml

def _locate_config(path: str) -> Path | None:
    config_path = Path(path)
    if config_path.is_absolute():
        return config_path if config_path.exists() else None
    if config_path.exists():
        return config_path
    for parent in (Path.cwd(), *Path.cwd().parents):
        candidate = parent / path
        if candidate.exists():
            return candidate
    base = Path(__file__).resolve().parent
    for parent in (base, *base.parents):
        candidate = parent / path
        if candidate.exists():
            return candidate
    return None

def load_config(path: str = "config.yaml"):
    config_path = _locate_config(path)
    if config_path:
        try:
            return yaml.safe_load(config_path.read_text()) or {}
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    return {}


def resolve_arg(arg_name, cli_value, config_value, default_value=None):
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default_value


def resolve_output_path(output_arg: str, video_path: str) -> str | None:
    """
    Resolves the final output path.
    If output_arg is a directory (or has no extension), appends the video filename with .md extension.
    """
    if not output_arg:
        return None

    out_path = Path(output_arg)
    video_stem = Path(video_path).stem

    # If path exists and is a dir, or if it doesn't exist but has no suffix (likely a dir)
    if out_path.is_dir() or (not out_path.exists() and not out_path.suffix):
        # It's a directory
        return str(out_path / f"{video_stem}.md")

    return str(out_path)


@app.command()
def summarize(
    video_path: str = typer.Argument(None, help="Path to the video file"),
    model: str = typer.Option(None, help="Gemini model ID (default: gemini-3-flash)"),
    output: str = typer.Option(None, "--output", "-o", help="Save output to a file"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
):
    """Generate a summary of the video."""
    config = load_config(config_path)

    video_path = resolve_arg("video_path", video_path, config.get("video_path"))
    if not video_path:
        console.print("[red]Error: Missing argument 'video_path'.[/red]")
        raise typer.Exit(code=1)
        
    model = resolve_arg("model", model, config.get("model"), "gemini-3-flash")
    output = resolve_arg("output", output, config.get("output"))
    final_output = resolve_output_path(output, video_path)

    agent = get_agent(model)
    with console.status("[bold green]Uploading video..."):
        try:
            start_time = time.perf_counter()
            video_file = agent.client.upload_video(video_path, console=console)
            response = agent.get_summary(video_file)
            elapsed_time = time.perf_counter() - start_time
            display_response(
                response, agent.client, "Video Summary", "blue", elapsed_time, final_output
            )
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def ask(
    video_path: str = typer.Argument(None, help="Path to the video file"),
    question: str = typer.Argument(None, help="Question about the video"),
    model: str = typer.Option(None, help="Gemini model ID"),
    output: str = typer.Option(None, "--output", "-o", help="Save output to a file"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
):
    """Ask a question about the video."""
    config = load_config(config_path)

    video_path = resolve_arg("video_path", video_path, config.get("video_path"))
    if not video_path:
        console.print("[red]Error: Missing argument 'video_path'.[/red]")
        raise typer.Exit(code=1)

    # Question is almost always dynamic, but could be in config for repetitive tasks
    question = resolve_arg("question", question, config.get("question"))
    if not question:
        console.print("[red]Error: Missing argument 'question'.[/red]")
        raise typer.Exit(code=1)

    model = resolve_arg("model", model, config.get("model"), "gemini-3-flash")
    output = resolve_arg("output", output, config.get("output"))
    final_output = resolve_output_path(output, video_path)

    agent = get_agent(model)
    with console.status("[bold green]Uploading video..."):
        try:
            start_time = time.perf_counter()
            video_file = agent.client.upload_video(video_path, console=console)
            response = agent.ask_question(video_file, question)
            elapsed_time = time.perf_counter() - start_time
            display_response(response, agent.client, "Answer", "green", elapsed_time, final_output)
        except Exception as e:
            logger.error(f"Error during Q&A: {e}")
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def events(
    video_path: str = typer.Argument(None, help="Path to the video file"),
    model: str = typer.Option(None, help="Gemini model ID"),
    output: str = typer.Option(None, "--output", "-o", help="Save output to a file"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
):
    """Detect events in the video."""
    config = load_config(config_path)

    video_path = resolve_arg("video_path", video_path, config.get("video_path"))
    if not video_path:
        console.print("[red]Error: Missing argument 'video_path'.[/red]")
        raise typer.Exit(code=1)
        
    model = resolve_arg("model", model, config.get("model"), "gemini-3-flash")
    output = resolve_arg("output", output, config.get("output"))
    final_output = resolve_output_path(output, video_path)

    agent = get_agent(model)
    with console.status("[bold green]Uploading video..."):
        try:
            start_time = time.perf_counter()
            video_file = agent.client.upload_video(video_path, console=console)
            response = agent.detect_events(video_file)
            elapsed_time = time.perf_counter() - start_time
            display_response(
                response, agent.client, "Detected Events", "magenta", elapsed_time, final_output
            )
        except Exception as e:
            logger.error(f"Error during event detection: {e}")
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def transcribe(
    video_path: str = typer.Argument(None, help="Path to the video file"),
    model: str = typer.Option(None, help="Gemini model ID"),
    output: str = typer.Option(None, "--output", "-o", help="Save output to a file"),
    config_path: str = typer.Option("config.yaml", "--config", "-c", help="Path to config file"),
):
    """Transcribe and diarize the video audio."""
    config = load_config(config_path)

    video_path = resolve_arg("video_path", video_path, config.get("video_path"))
    if not video_path:
        console.print("[red]Error: Missing argument 'video_path'.[/red]")
        raise typer.Exit(code=1)
        
    model = resolve_arg("model", model, config.get("model"), "gemini-3-flash")
    output = resolve_arg("output", output, config.get("output"))
    final_output = resolve_output_path(output, video_path)

    agent = get_agent(model)
    with console.status("[bold green]Uploading video..."):
        try:
            start_time = time.perf_counter()
            video_file = agent.client.upload_video(video_path, console=console)
            response = agent.transcribe_and_diarize(video_file)
            elapsed_time = time.perf_counter() - start_time
            display_response(
                response, agent.client, "Diarized Transcript", "cyan", elapsed_time, final_output
            )
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    app()
