from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from personal_assistant import devtools


@pytest.mark.unit
def test_run_checks_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], Path]] = []

    def fake_run(command: list[str], cwd: Path) -> None:
        calls.append((command, cwd))

    monkeypatch.setattr(devtools, "_run", fake_run)
    monkeypatch.setattr(devtools, "_core_root", lambda: Path("/core"))

    devtools.run_checks()

    assert calls == [
        (["uv", "sync", "--extra", "dev", "--active"], Path("/core")),
        (["uv", "run", "ruff", "check", "src"], Path("/core")),
        (["uv", "run", "ruff", "format", "--check", "src"], Path("/core")),
        (["uv", "run", "mypy", "src"], Path("/core")),
        (["uv", "pip", "check"], Path("/core")),
        (["uv", "run", "python", "-m", "compileall", "-q", "src"], Path("/core")),
    ]


@pytest.mark.unit
def test_run_workspace_checks_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], Path]] = []

    def fake_run(command: list[str], cwd: Path) -> None:
        calls.append((command, cwd))

    monkeypatch.setattr(devtools, "_run", fake_run)
    monkeypatch.setattr(devtools, "_workspace_root", lambda: Path("/workspace"))

    devtools.run_workspace_checks()

    assert calls == [
        (["uv", "sync", "--extra", "dev", "--active"], Path("/workspace")),
        (["uv", "run", "ruff", "check", "core/src", "ui/src"], Path("/workspace")),
        (["uv", "run", "ruff", "format", "--check", "core/src", "ui/src"], Path("/workspace")),
        (["uv", "run", "mypy", "core/src"], Path("/workspace")),
        (["uv", "pip", "check"], Path("/workspace")),
        (
            [
                "uv",
                "run",
                "python",
                "-m",
                "compileall",
                "-q",
                "core/src",
                "ui/src",
            ],
            Path("/workspace"),
        ),
    ]
