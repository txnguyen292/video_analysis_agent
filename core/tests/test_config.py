from __future__ import annotations

from pathlib import Path

import pytest

from personal_assistant import config as config_module


@pytest.mark.unit
def test_locate_config_absolute_path(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("model: gemini-3-flash\n", encoding="utf-8")

    found = config_module._locate_config(str(config_path))

    assert found is not None
    assert found.resolve() == config_path.resolve()


@pytest.mark.unit
def test_locate_config_relative_searches_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("model: gemini-3-pro\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    found = config_module._locate_config("config.yaml")

    assert found is not None
    assert found.resolve() == config_path.resolve()


@pytest.mark.unit
def test_load_config_returns_empty_when_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    data = config_module.load_config("missing.yaml")

    assert data == {}


@pytest.mark.unit
def test_load_config_parses_yaml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("model: gemini-3-flash\noutput: results/\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    data = config_module.load_config("config.yaml")

    assert data["model"] == "gemini-3-flash"
    assert data["output"] == "results/"


@pytest.mark.unit
def test_resolve_arg_prefers_cli_value() -> None:
    assert config_module.resolve_arg("model", "cli", "config", "default") == "cli"


@pytest.mark.unit
def test_resolve_arg_falls_back_to_config() -> None:
    assert config_module.resolve_arg("model", None, "config", "default") == "config"


@pytest.mark.unit
def test_resolve_arg_falls_back_to_default() -> None:
    assert config_module.resolve_arg("model", None, None, "default") == "default"


@pytest.mark.unit
def test_resolve_output_path_returns_none_for_missing_output() -> None:
    assert config_module.resolve_output_path(None, "video.mp4") is None


@pytest.mark.unit
def test_resolve_output_path_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "results"
    output_dir.mkdir()

    resolved = config_module.resolve_output_path(str(output_dir), "video.mp4")

    assert resolved == str(output_dir / "video.md")


@pytest.mark.unit
def test_resolve_output_path_nonexistent_dir(tmp_path: Path) -> None:
    output_dir = tmp_path / "results"

    resolved = config_module.resolve_output_path(str(output_dir), "video.mp4")

    assert resolved == str(output_dir / "video.md")


@pytest.mark.unit
def test_resolve_output_path_file(tmp_path: Path) -> None:
    output_file = tmp_path / "custom.md"

    resolved = config_module.resolve_output_path(str(output_file), "video.mp4")

    assert resolved == str(output_file)
