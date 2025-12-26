# Personal Assistant UI

Flet-based desktop UI for the Personal Assistant core package.

This package depends on the core agent in `../core`.

## Run The UI

From this folder:

```bash
uv sync
uv run personal-assistant-ui
```

Hot reload during development:

```bash
uv run flet run src/personal_assistant_ui/app.py
```

Use the UI config template (for future settings persistence):

```bash
cat configs/config.yml
```

The UI reads `configs/config.yml` automatically on startup for theme/model defaults.

## Run With Python

From this folder:

```bash
python src/personal_assistant_ui/app.py
```

Or run as a module if the package is installed:

```bash
python -m personal_assistant_ui.app
```
