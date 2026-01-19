from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypeVar

import yaml
from dotenv import load_dotenv
from loguru import logger

T = TypeVar("T")

_ENV_LOADED = False


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


def _find_env_path() -> Path | None:
    for parent in (Path.cwd(), *Path.cwd().parents):
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    base = Path(__file__).resolve().parent
    for parent in (base, *base.parents):
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None


def load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = _find_env_path()
    if env_path:
        load_dotenv(dotenv_path=env_path, override=False)
    load_dotenv(override=False)
    _ENV_LOADED = True


def get_env(key: str, default: str | None = None) -> str | None:
    load_env()
    return os.getenv(key, default)


def get_redis_settings() -> tuple[str, int]:
    host = get_env("REDIS_HOST", "localhost") or "localhost"
    port_raw = get_env("REDIS_PORT", "6379") or "6379"
    try:
        port = int(port_raw)
    except ValueError:
        logger.warning(f"Invalid REDIS_PORT '{port_raw}', falling back to 6379")
        port = 6379
    return host, port


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
