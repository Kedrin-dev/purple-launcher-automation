import time

from config import (
    OPTIONAL_DELAY_BEFORE,
    OPTIONAL_DELAY_BETWEEN,
    OPTIONAL_ENABLED,
    OPTIONAL_POINTS,
    POPUP_CLICK_INTERVAL,
    POPUP_INITIAL_DELAY,
    POPUP_TRY_SECONDS,
    REQUIRED_DELAY_BEFORE,
    REQUIRED_DELAY_BETWEEN,
    REQUIRED_POINTS,
    RX_CLOSE,
    RY_CLOSE,
)
from helpers import log


def click_in_window_by_ratio(win, rx: float, ry: float) -> None:
    rect = win.rectangle()
    x = int(rect.left + rect.width() * rx)
    y = int(rect.top + rect.height() * ry)
    win.click_input(coords=(x - rect.left, y - rect.top))


def try_click_point(win, rx, ry, tries=2, interval=0.25) -> bool:
    for _ in range(tries):
        try:
            click_in_window_by_ratio(win, rx, ry)
            return True
        except Exception:
            time.sleep(interval)
    return False


def close_popup_if_appears(game_win) -> None:
    try:
        game_win.set_focus()
    except Exception:
        pass

    time.sleep(POPUP_INITIAL_DELAY)

    end_t = time.time() + POPUP_TRY_SECONDS
    while time.time() < end_t:
        try:
            click_in_window_by_ratio(game_win, RX_CLOSE, RY_CLOSE)
        except Exception:
            pass
        time.sleep(POPUP_CLICK_INTERVAL)


def click_sequence(game_win, do_optional=OPTIONAL_ENABLED) -> None:
    try:
        game_win.set_focus()
    except Exception:
        pass

    if do_optional:
        log("Жду перед optional кликами...")
        time.sleep(OPTIONAL_DELAY_BEFORE)

        log("Делаю optional клики...")
        for i, (rx, ry) in enumerate(OPTIONAL_POINTS, start=1):
            ok = try_click_point(game_win, rx, ry, tries=2, interval=0.3)
            log(f"Optional click {i}: {'OK' if ok else 'SKIP'}")
            time.sleep(OPTIONAL_DELAY_BETWEEN)
    else:
        log("Optional клики пропущены")

    log("Жду перед обязательными кликами...")
    time.sleep(REQUIRED_DELAY_BEFORE)

    log("Делаю обязательные клики...")
    for i, (rx, ry) in enumerate(REQUIRED_POINTS, start=1):
        ok = try_click_point(game_win, rx, ry, tries=5, interval=0.3)
        log(f"Required click {i}: {'OK' if ok else 'FAIL'}")
        time.sleep(REQUIRED_DELAY_BETWEEN)


def post_launch_actions(game_win) -> None:
    try:
        game_win.set_focus()
    except Exception:
        pass

    try:
        title = (game_win.window_text() or "").strip()
    except Exception:
        title = ""

    log(f"Окно игры: {title}")
    log("Пробую закрыть попап...")
    close_popup_if_appears(game_win)
    log("Делаю клики...")
    click_sequence(game_win, do_optional=True)