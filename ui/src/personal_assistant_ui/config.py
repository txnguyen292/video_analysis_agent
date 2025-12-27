from pathlib import Path

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


def load_ui_config(path: str = "configs/config.yml") -> dict:
    config_path = _locate_config(path)
    if not config_path:
        return {}
    try:
        return yaml.safe_load(config_path.read_text()) or {}
    except Exception:
        return {}
