from __future__ import annotations

import subprocess
from pathlib import Path


def _run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def _run_commands(commands: list[list[str]], cwd: Path) -> None:
    for command in commands:
        _run(command, cwd=cwd)


def _core_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_checks() -> None:
    root = _core_root()
    commands = [
        ["uv", "sync", "--extra", "dev", "--active"],
        ["uv", "run", "ruff", "check", "src"],
        ["uv", "run", "ruff", "format", "--check", "src"],
        ["uv", "run", "mypy", "src"],
        ["uv", "pip", "check"],
        ["uv", "run", "python", "-m", "compileall", "-q", "src"],
    ]
    _run_commands(commands, cwd=root)


def run_workspace_checks() -> None:
    root = _workspace_root()
    commands = [
        ["uv", "sync", "--extra", "dev", "--active"],
        ["uv", "run", "ruff", "check", "core/src", "ui/src"],
        ["uv", "run", "ruff", "format", "--check", "core/src", "ui/src"],
        ["uv", "run", "mypy", "core/src"],
        ["uv", "pip", "check"],
        ["uv", "run", "python", "-m", "compileall", "-q", "core/src", "ui/src"],
    ]
    _run_commands(commands, cwd=root)


if __name__ == "__main__":
    run_checks()
