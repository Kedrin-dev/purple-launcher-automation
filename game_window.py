import time
from typing import Dict, List, Optional, Tuple

import win32con
import win32gui
from pywinauto import Desktop

from config import GAME_CLASS, GAME_TITLE_KEY, GAME_WAIT_TIMEOUT
from helpers import log


def force_foreground(hwnd: int) -> None:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass


def wrap_hwnd_uia(hwnd: int):
    try:
        w = Desktop(backend="uia").window(handle=hwnd)
        _ = w.window_text()
        return w
    except Exception:
        return None


def wrap_hwnd_win32(hwnd: int):
    try:
        w = Desktop(backend="win32").window(handle=hwnd)
        _ = w.window_text()
        return w
    except Exception:
        return None


def wrap_hwnd_any(hwnd: int):
    w = wrap_hwnd_uia(hwnd)
    if w is not None:
        return w
    return wrap_hwnd_win32(hwnd)


def enum_unreal_windows_win32(include_invisible: bool = True) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []

    def enum_cb(hwnd, _):
        try:
            if not include_invisible and not win32gui.IsWindowVisible(hwnd):
                return
            cls = win32gui.GetClassName(hwnd) or ""
            if cls != GAME_CLASS:
                return
            title = (win32gui.GetWindowText(hwnd) or "").strip()
            out.append((hwnd, title))
        except Exception:
            return

    win32gui.EnumWindows(enum_cb, None)
    return out


def list_game_windows_uia() -> List[Tuple[int, str]]:
    d = Desktop(backend="uia")
    out: List[Tuple[int, str]] = []

    for w in d.windows():
        try:
            title = (w.window_text() or "").strip()
        except Exception:
            continue

        if not title or GAME_TITLE_KEY not in title:
            continue

        try:
            cls = w.element_info.class_name
        except Exception:
            cls = ""

        if cls and cls != GAME_CLASS:
            continue

        try:
            out.append((w.handle, title))
        except Exception:
            pass

    return out


def list_game_windows_win32_by_title() -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []

    def enum_cb(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = (win32gui.GetWindowText(hwnd) or "").strip()
            if not title or GAME_TITLE_KEY not in title:
                return
            out.append((hwnd, title))
        except Exception:
            return

    win32gui.EnumWindows(enum_cb, None)
    return out


def list_all_game_windows_titles() -> List[Tuple[int, str]]:
    seen: Dict[int, str] = {}

    try:
        for hwnd, title in list_game_windows_uia():
            seen[hwnd] = title
    except Exception:
        pass

    try:
        for hwnd, title in list_game_windows_win32_by_title():
            seen[hwnd] = title
    except Exception:
        pass

    return [(h, seen[h]) for h in seen]


def any_game_window_visible() -> Optional[Tuple[int, str]]:
    wins = list_all_game_windows_titles()
    return wins[0] if wins else None


def snapshot_game_windows():
    before_unreal_list = enum_unreal_windows_win32(include_invisible=True)
    before_unreal = {h: t for h, t in before_unreal_list}
    before_titles = {h: t for h, t in list_all_game_windows_titles()}
    return before_unreal, before_titles


def wait_main_game_foreground(timeout=GAME_WAIT_TIMEOUT):
    end_t = time.time() + timeout

    while time.time() < end_t:
        hwnd = win32gui.GetForegroundWindow()
        w = wrap_hwnd_any(hwnd)
        if w is not None:
            try:
                title = (w.window_text() or "").strip()
            except Exception:
                title = ""
            if title and GAME_TITLE_KEY in title:
                return w

        wins = list_all_game_windows_titles()
        if wins:
            hwnd2, _ = wins[0]
            force_foreground(hwnd2)
            time.sleep(0.15)
            w2 = wrap_hwnd_any(hwnd2)
            if w2 is not None:
                return w2

        time.sleep(0.25)

    raise TimeoutError("Основное окно игры не стало активным/не найдено за таймаут.")


def wait_game_after_additional_launch(
    before_unreal: Dict[int, str],
    before_titles: Dict[int, str],
    target_exact_title: Optional[str],
    timeout=GAME_WAIT_TIMEOUT,
):
    end_t = time.time() + timeout

    while time.time() < end_t:
        hwnd_fg = win32gui.GetForegroundWindow()
        w_fg = wrap_hwnd_any(hwnd_fg)
        if w_fg is not None:
            try:
                t_fg = (w_fg.window_text() or "").strip()
            except Exception:
                t_fg = ""
            if t_fg and GAME_TITLE_KEY in t_fg:
                return w_fg

        unreal_now_list = enum_unreal_windows_win32(include_invisible=True)
        unreal_now: Dict[int, str] = {h: title for h, title in unreal_now_list}

        if target_exact_title:
            for h, title in unreal_now.items():
                if title.strip() == target_exact_title:
                    force_foreground(h)
                    time.sleep(0.2)
                    w = wrap_hwnd_any(h)
                    if w is not None:
                        return w

            for h, title in list_all_game_windows_titles():
                if title.strip() == target_exact_title:
                    force_foreground(h)
                    time.sleep(0.2)
                    w = wrap_hwnd_any(h)
                    if w is not None:
                        return w

        new_hwnds = [h for h in unreal_now.keys() if h not in before_unreal]
        if new_hwnds:
            h = new_hwnds[0]
            force_foreground(h)
            time.sleep(0.2)
            w = wrap_hwnd_any(h)
            if w is not None:
                return w

        for h, title_now in unreal_now.items():
            title_before = before_unreal.get(h, "")
            if (title_now or "") != (title_before or ""):
                if title_now and GAME_TITLE_KEY in title_now:
                    force_foreground(h)
                    time.sleep(0.2)
                    w = wrap_hwnd_any(h)
                    if w is not None:
                        return w

        titles_now = {h: title for h, title in list_all_game_windows_titles()}
        for h, title_now in titles_now.items():
            title_before = before_titles.get(h, "")
            if title_now != title_before:
                force_foreground(h)
                time.sleep(0.2)
                w = wrap_hwnd_any(h)
                if w is not None:
                    return w

        time.sleep(0.25)

    try:
        snap = enum_unreal_windows_win32(include_invisible=True)
        log("DEBUG: UnrealWindow snapshot at timeout:")
        for h, t in snap:
            log(f"  hwnd={h} title={t!r}")
    except Exception:
        pass

    raise TimeoutError("Окно игры не стало активным и не найдено по UnrealWindow+title за таймаут.")