# Purple Lineage2M Multi-Account Automation

Automation tool for launching and managing multiple Lineage2M accounts through the NCSoft PURPLE launcher.

The project focuses on **reliability of UI automation**, handling unstable UI elements and detecting game windows that may appear without titles or with delayed initialization.

---

## Features

- Automatic main account launch
- Multi-account launch via PURPLE MultiPlay
- Reliable UnrealWindow detection
- UI Automation + Win32 fallback strategy
- Popup handling automation
- Automated in-game click sequences
- Stable window detection without relying only on titles
- Debug entry points for isolated testing

---

## Key engineering challenges solved

This project solves several typical UI automation problems:

- UI Automation elements sometimes returning invalid rectangles
- Game windows appearing without titles
- Delayed window creation
- Windows not becoming foreground automatically
- Multi-account launcher state synchronization
- Stable detection of newly launched game windows

---

## Tech stack

Python

Libraries:
- pywinauto
- pywin32

Technologies:
- Windows UI Automation
- Win32 API
- Desktop automation
- Process/window tracking logic

---

## Project structure
config.py — project configuration and timing constants
main.py — main orchestration logic
purple_control.py — PURPLE launcher interaction
game_window.py — game window detection and tracking
game_actions.py — actions performed inside game window
helpers.py — shared helper utilities
state_storage.py — persistent launch progress storage
debug_cases.py — isolated debug scenarios


---

## Design priorities

The project prioritizes:

1. Stability
2. Reliability
3. Maintainability
4. Simplicity of debugging

Speed optimization is secondary to stability.

---

## Architecture approach

The codebase is separated by responsibility:

Launcher control → PURPLE interaction  
Window tracking → Game window detection  
Game actions → In-game automation  
Orchestration → Scenario coordination  

This separation allows easier debugging and extension.

---

## Current status

Working automation script used for practical multi-account management.

Actively improving:
- architecture
- reliability
- modularity

---

## Possible future improvements

- Logging system
- Better retry strategies
- Screenshot capture on failures
- Configurable action sequences
- Account profiles
- Error recovery flows

---

## Disclaimer

This project is created for educational purposes and UI automation research.

---

## Author

Personal automation project focused on improving Python automation skills.

---

## Status

Personal learning project.
