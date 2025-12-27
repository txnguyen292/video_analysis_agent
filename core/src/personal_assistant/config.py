from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from loguru import logger

T = TypeVar("T")


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


def load_config(path: str = "config.yaml") -> dict[str, Any]:
    config_path = _locate_config(path)
    if config_path:
        try:
            return yaml.safe_load(config_path.read_text()) or {}
        except Exception as exc:
            logger.warning(f"Failed to load config from {config_path}: {exc}")
    return {}


def resolve_arg(
    arg_name: str,
    cli_value: T | None,
    config_value: T | None,
    default_value: T | None = None,
) -> T | None:
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default_value


def resolve_output_path(output_arg: str | None, video_path: str) -> str | None:
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
