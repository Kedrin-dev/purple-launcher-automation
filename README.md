# Purple Lineage2M Automation

Python automation script for launching multiple Lineage2M accounts via NCSoft PURPLE launcher.

## Features

- Main account auto launch
- Multi account launch via MultiPlay
- UnrealWindow detection without relying only on titles
- UI Automation + Win32 fallback
- Popup handling
- Automated in-game actions
- Debug entry points for isolated testing

## Tech stack

- Python
- pywinauto
- pywin32
- UI Automation
- Win32 API

## Project structure

- `main.py` — main scenario orchestration
- `purple_control.py` — PURPLE launcher interaction
- `game_window.py` — game window detection and tracking
- `game_actions.py` — actions inside the game window
- `helpers.py` — shared helpers
- `state_storage.py` — persistent local state
- `debug_cases.py` — isolated debug entry points

## Status

Working automation project focused on stability of multi-account launch flow.