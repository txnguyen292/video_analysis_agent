# Personal Assistant Core

Core agent logic and CLI for video understanding workflows.

This package is designed to be published to PyPI in the future. The desktop UI lives in the `../ui` package.

## Run The CLI

From this folder:

```bash
uv sync
uv run personal-assistant summarize ../data/inputs/sample.mp4
```

Other tasks:

```bash
uv run personal-assistant ask ../data/inputs/sample.mp4 "What is the key message?"
uv run personal-assistant events ../data/inputs/sample.mp4
uv run personal-assistant transcribe ../data/inputs/sample.mp4
```

Use the repo-root `config.yaml` defaults:

```bash
uv run personal-assistant summarize
```

Use the core config template:

```bash
uv run personal-assistant summarize --config configs/config.yml
```

## Run With Python

From this folder:

```bash
python src/personal_assistant/main.py summarize ../data/inputs/sample.mp4
```

Or run as a module if the package is installed:

```bash
python -m personal_assistant.main summarize ../data/inputs/sample.mp4
```
