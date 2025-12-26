from __future__ import annotations

import subprocess
from pathlib import Path


def _run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def _core_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_checks() -> None:
    root = _core_root()
    _run(["uv", "sync", "--extra", "dev", "--active"], cwd=root)
    _run(["uv", "run", "ruff", "check", "src"], cwd=root)
    _run(["uv", "run", "ruff", "format", "--check", "src"], cwd=root)
    _run(["uv", "run", "mypy", "src"], cwd=root)
    _run(["uv", "run", "python", "-m", "pip", "check"], cwd=root)
    _run(["uv", "run", "python", "-m", "compileall", "-q", "src"], cwd=root)


def run_workspace_checks() -> None:
    root = _workspace_root()
    _run(["uv", "sync", "--extra", "dev", "--active"], cwd=root)
    _run(["uv", "run", "ruff", "check", "core/src", "ui/src"], cwd=root)
    _run(["uv", "run", "ruff", "format", "--check", "core/src", "ui/src"], cwd=root)
    _run(["uv", "run", "mypy", "core/src"], cwd=root)
    _run(["uv", "run", "python", "-m", "pip", "check"], cwd=root)
    _run(
        ["uv", "run", "python", "-m", "compileall", "-q", "core/src", "ui/src"],
        cwd=root,
    )


if __name__ == "__main__":
    run_checks()
