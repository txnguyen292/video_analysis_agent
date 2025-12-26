from __future__ import annotations

import subprocess
from pathlib import Path


def _run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def _ui_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_checks() -> None:
    root = _ui_root()
    _run(["uv", "sync", "--extra", "dev", "--active"], cwd=root)
    _run(["uv", "run", "ruff", "check", "src"], cwd=root)
    _run(["uv", "run", "ruff", "format", "--check", "src"], cwd=root)
    _run(["uv", "run", "mypy", "--ignore-missing-imports", "src"], cwd=root)
    _run(["uv", "run", "python", "-m", "pip", "check"], cwd=root)
    _run(["uv", "run", "python", "-m", "compileall", "-q", "src"], cwd=root)


if __name__ == "__main__":
    run_checks()
