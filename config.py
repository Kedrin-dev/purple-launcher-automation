from pathlib import Path

PURPLE_TITLE = "PURPLE"

# Game window signature
GAME_TITLE_KEY = "Lineage2M l "
GAME_CLASS = "UnrealWindow"
GAME_WAIT_TIMEOUT = 180  # seconds

# Твои эмпирические тайминги
POPUP_INITIAL_DELAY = 20
POPUP_TRY_SECONDS = 4.0
POPUP_CLICK_INTERVAL = 0.6

OPTIONAL_ENABLED = True
OPTIONAL_DELAY_BEFORE = 5
OPTIONAL_DELAY_BETWEEN = 1.0

REQUIRED_DELAY_BEFORE = 10
REQUIRED_DELAY_BETWEEN = 1.2

# Popup close "X" (relative coords in game window)
RX_CLOSE = 0.8781
RY_CLOSE = 0.7711

# In-game click points
OPTIONAL_POINTS = [
    (0.9012, 0.7789),
    (0.8219, 0.2333),
]

REQUIRED_POINTS = [
    (0.8094, 0.5089),
    (0.0381, 0.5978),
    (0.5038, 0.5133),
]

# Purple UIA ids
BTN_PLAY_MAIN = ("PlayButton", "Button")
BTN_OPEN_MULTI = ("BtnOpenMultiAccount", "Button")
MULTIPLAY_VIEW = ("MultiPlayView", "Custom")
GEAR_IN_MULTIPLAY = ("AccountManagementButton", "Button")

BTN_GAME_RUN_ID = "BtnGameRun"
BTN_GAME_RUNNING_ID = "BtnGameRunning"

CHECKBOX_AUTOID = "MultiAccountListCheckBox"
OK_TITLES = {"ok", "ок"}

PANEL_OPEN_TIMEOUT = 12
GEAR_OPEN_TIMEOUT = 12
RETRY_GEAR_OPEN = 4

STATE_FILE = Path("multi_idx.txt")
CHECKBOX_DIRECTION = "topdown"  # or "bottomup"

FOCUS_SLEEP = 0.2
FAST_POLL_SECONDS = 3.0
FAST_POLL_INTERVAL = 0.08
SLOW_POLL_INTERVAL = 0.25
APPLY_POLL_INTERVAL = 0.15

DEBUG = True