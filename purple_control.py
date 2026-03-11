import time
from typing import List, Optional

import win32con
import win32gui
from pywinauto import Desktop

from config import (
    APPLY_POLL_INTERVAL,
    BTN_GAME_RUN_ID,
    BTN_GAME_RUNNING_ID,
    BTN_OPEN_MULTI,
    BTN_PLAY_MAIN,
    CHECKBOX_AUTOID,
    FAST_POLL_INTERVAL,
    FAST_POLL_SECONDS,
    FOCUS_SLEEP,
    GEAR_IN_MULTIPLAY,
    GEAR_OPEN_TIMEOUT,
    MULTIPLAY_VIEW,
    OK_TITLES,
    PANEL_OPEN_TIMEOUT,
    PURPLE_TITLE,
    RETRY_GEAR_OPEN,
    SLOW_POLL_INTERVAL,
)
from helpers import (
    get_automation_id,
    get_control_type,
    is_really_visible,
    log,
    safe_invoke_or_click,
)


def get_purple():
    purple = Desktop(backend="uia").window(title=PURPLE_TITLE)
    purple.wait("visible", timeout=30)
    return purple


def focus_purple():
    purple = get_purple()

    try:
        purple.restore()
    except Exception:
        pass

    try:
        hwnd = purple.handle
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass

    try:
        purple.set_focus()
    except Exception:
        pass

    time.sleep(FOCUS_SLEEP)
    return purple


def press_play_in_purple() -> None:
    purple = focus_purple()

    for _ in range(3):
        try:
            play_btn = purple.child_window(
                auto_id=BTN_PLAY_MAIN[0],
                control_type=BTN_PLAY_MAIN[1],
            )
            if play_btn.exists() and play_btn.is_visible():
                log("Нашёл PlayButton по auto_id -> жму")
                safe_invoke_or_click(play_btn)
                return
        except Exception:
            pass
        time.sleep(0.5)

    log("PlayButton по auto_id не найден/не видим -> ищу по тексту...")
    keywords = ("play", "запуск", "запустить", "start")
    candidates = []

    try:
        for el in purple.descendants():
            if get_control_type(el) != "Button":
                continue
            if not is_really_visible(el):
                continue

            t = (el.window_text() or "").strip()
            if not t:
                continue

            tl = t.lower()
            if any(k in tl for k in keywords):
                candidates.append(el)
    except Exception:
        pass

    if candidates:
        def area(btn):
            r = btn.rectangle()
            return (r.right - r.left) * (r.bottom - r.top)

        candidates.sort(key=area, reverse=True)
        btn = candidates[0]
        log(f"Нажимаю Play по тексту: {(btn.window_text() or '').strip()!r}")
        safe_invoke_or_click(btn)
        return

    raise TimeoutError("Не удалось найти кнопку Play в PURPLE.")


def is_multi_panel_open(purple) -> bool:
    try:
        mp = purple.child_window(
            auto_id=MULTIPLAY_VIEW[0],
            control_type=MULTIPLAY_VIEW[1],
        )
        return mp.exists() and mp.is_visible()
    except Exception:
        return False


def ensure_multi_panel_open():
    purple = focus_purple()

    if is_multi_panel_open(purple):
        log("Мульти-панель уже открыта.")
        return purple

    log("Открываю мульти-панель...")
    btn = purple.child_window(
        auto_id=BTN_OPEN_MULTI[0],
        control_type=BTN_OPEN_MULTI[1],
    )
    btn.wait("exists visible", timeout=10)

    if not safe_invoke_or_click(btn):
        raise RuntimeError("Не смог нажать BtnOpenMultiAccount")

    t_fast = time.time() + FAST_POLL_SECONDS
    while time.time() < t_fast:
        if is_multi_panel_open(purple):
            log("Мульти-панель открылась ✅")
            time.sleep(0.2)
            return purple
        time.sleep(FAST_POLL_INTERVAL)

    end_t = time.time() + max(0.0, PANEL_OPEN_TIMEOUT - FAST_POLL_SECONDS)
    while time.time() < end_t:
        if is_multi_panel_open(purple):
            log("Мульти-панель открылась ✅")
            time.sleep(0.2)
            return purple
        time.sleep(SLOW_POLL_INTERVAL)

    raise RuntimeError("Мульти-панель не открылась за таймаут.")


def find_button_in_multiplay(mp, wanted_auto_id: str):
    try:
        for el in mp.descendants():
            if get_control_type(el) == "Button" and get_automation_id(el) == wanted_auto_id:
                return el
    except Exception:
        pass
    return None


def try_press_additional_run_button() -> bool:
    purple = ensure_multi_panel_open()
    mp = purple.child_window(
        auto_id=MULTIPLAY_VIEW[0],
        control_type=MULTIPLAY_VIEW[1],
    )
    mp.wait("exists visible", timeout=12)

    run_btn = find_button_in_multiplay(mp, BTN_GAME_RUN_ID)
    running_btn = find_button_in_multiplay(mp, BTN_GAME_RUNNING_ID)

    if run_btn is not None and is_really_visible(run_btn):
        log("BtnGameRun ВИДИМ -> запускаю доп. аккаунт")
        safe_invoke_or_click(run_btn)
        return True

    if running_btn is not None and is_really_visible(running_btn):
        log("BtnGameRunning ВИДИМ -> доп. аккаунт уже запущен")
        return False

    log("Не вижу видимого BtnGameRun/BtnGameRunning")
    return False


def get_selected_account_name_from_multiplay() -> Optional[str]:
    purple = ensure_multi_panel_open()
    mp = purple.child_window(
        auto_id=MULTIPLAY_VIEW[0],
        control_type=MULTIPLAY_VIEW[1],
    )

    try:
        mp.wait("exists visible", timeout=8)
    except Exception:
        return None

    bad_phrases = {
        "многоаккаунтная учетная запись",
        "запуск игры",
        "запущено",
        "нет аккаунтов для игры.",
        "нет аккаунтов для игры",
        "технические работы",
        "подготовка...",
        "подготовка",
        "обновляется",
        "проверка файлов",
        "проверка...",
        "файл применяется",
        "восстановление файла",
        "пауза",
        "отмена",
        "игра закрывается",
        "подготовка к запуску игры",
        "производится установка",
    }

    candidates: List[str] = []
    try:
        for el in mp.descendants():
            if get_control_type(el) != "Text":
                continue
            t = (el.window_text() or "").strip()
            if not t:
                continue
            tl = t.lower()
            if tl in bad_phrases:
                continue
            if len(t) > 24:
                continue
            candidates.append(t)
    except Exception:
        pass

    if not candidates:
        return None

    candidates.sort(key=lambda s: (len(s), s))
    return candidates[0]


def has_ok_button(container) -> bool:
    try:
        for el in container.descendants():
            if get_control_type(el) == "Button":
                t = (el.window_text() or "").strip().lower()
                if t in OK_TITLES:
                    return True
    except Exception:
        pass
    return False


def get_checkboxes(container):
    out = []
    try:
        for el in container.descendants():
            if get_control_type(el) == "CheckBox" and get_automation_id(el) == CHECKBOX_AUTOID:
                out.append(el)
    except Exception:
        pass
    return out


def find_checkbox_panel_in_purple(purple):
    containers = purple.descendants(control_type="Pane") + purple.descendants(control_type="Custom")

    best = None
    best_area = None

    for c in containers:
        try:
            if not has_ok_button(c):
                continue

            cbs = get_checkboxes(c)
            if len(cbs) < 1:
                continue

            r = c.rectangle()
            area = (r.right - r.left) * (r.bottom - r.top)
            if best is None or area < best_area:
                best = c
                best_area = area
        except Exception:
            continue

    return best


def click_ok_in_panel(panel) -> None:
    try:
        for el in panel.descendants():
            if get_control_type(el) == "Button":
                t = (el.window_text() or "").strip().lower()
                if t in OK_TITLES:
                    safe_invoke_or_click(el)
                    time.sleep(0.3)
                    return
    except Exception:
        pass
    raise RuntimeError("Не нашёл кнопку OK/ОК в панели чекбоксов")


def wait_checkbox_panel(timeout=GEAR_OPEN_TIMEOUT):
    end_t = time.time() + timeout

    t_fast = time.time() + min(FAST_POLL_SECONDS, timeout)
    while time.time() < t_fast:
        purple = get_purple()
        panel = find_checkbox_panel_in_purple(purple)
        if panel is not None:
            return panel
        time.sleep(FAST_POLL_INTERVAL)

    while time.time() < end_t:
        purple = get_purple()
        panel = find_checkbox_panel_in_purple(purple)
        if panel is not None:
            return panel
        time.sleep(SLOW_POLL_INTERVAL)

    return None


def open_checkbox_panel_via_gear():
    ensure_multi_panel_open()
    purple = focus_purple()

    mp = purple.child_window(
        auto_id=MULTIPLAY_VIEW[0],
        control_type=MULTIPLAY_VIEW[1],
    )
    mp.wait("exists visible", timeout=8)

    gear = mp.child_window(
        auto_id=GEAR_IN_MULTIPLAY[0],
        control_type=GEAR_IN_MULTIPLAY[1],
    )
    gear.wait("exists visible", timeout=6)

    for attempt in range(1, RETRY_GEAR_OPEN + 1):
        log(f"Открываю шестерёнку (попытка {attempt}/{RETRY_GEAR_OPEN})...")
        safe_invoke_or_click(gear)

        panel = wait_checkbox_panel(timeout=GEAR_OPEN_TIMEOUT)
        if panel is not None:
            log("Панель чекбоксов открылась ✅")
            return panel

        log("Панель чекбоксов не появилась — пробую ещё раз...")

    raise RuntimeError("Не удалось открыть панель чекбоксов после клика по шестерёнке.")


def wait_multiplay_applied(timeout=12) -> bool:
    ensure_multi_panel_open()
    purple = get_purple()

    end_t = time.time() + timeout
    while time.time() < end_t:
        try:
            mp = purple.child_window(
                auto_id=MULTIPLAY_VIEW[0],
                control_type=MULTIPLAY_VIEW[1],
            )
            if not (mp.exists() and mp.is_visible()):
                time.sleep(APPLY_POLL_INTERVAL)
                continue
        except Exception:
            time.sleep(APPLY_POLL_INTERVAL)
            continue

        run_btn = find_button_in_multiplay(mp, BTN_GAME_RUN_ID)
        running_btn = find_button_in_multiplay(mp, BTN_GAME_RUNNING_ID)

        if run_btn is not None and is_really_visible(run_btn):
            return True
        if running_btn is not None and is_really_visible(running_btn):
            return True

        time.sleep(APPLY_POLL_INTERVAL)

    return False


def set_only_one_checkbox(panel, idx: int) -> bool:
    cbs = get_checkboxes(panel)
    log(f"Найдено чекбоксов: {len(cbs)}")

    if not cbs:
        log("Чекбоксов 0 -> пропуск.")
        return False

    if idx < 0 or idx >= len(cbs):
        log(f"idx={idx} вне диапазона 0..{len(cbs)-1} -> пропуск.")
        return False

    for cb in cbs:
        for _ in range(2):
            try:
                if hasattr(cb, "get_toggle_state") and cb.get_toggle_state() == 1:
                    cb.click_input()
                    time.sleep(0.06)
            except Exception:
                pass

    target = cbs[idx]
    for attempt in range(1, 5):
        try:
            target.click_input()
        except Exception:
            pass
        time.sleep(0.10)

        try:
            if hasattr(target, "get_toggle_state"):
                st = target.get_toggle_state()
                log(f"Проверка чекбокса idx={idx}: toggle_state={st} (попытка {attempt}/4)")
                if st == 1:
                    break
        except Exception:
            log(f"toggle_state не прочитался (попытка {attempt}/4)")

    try:
        if hasattr(target, "get_toggle_state") and target.get_toggle_state() != 1:
            log(f"Не удалось гарантированно включить чекбокс idx={idx} -> SKIP")
            try:
                click_ok_in_panel(panel)
            except Exception:
                pass
            return False
    except Exception:
        pass

    log("Нажимаю ОК в панели чекбоксов...")
    click_ok_in_panel(panel)
    return True


def wait_additional_launch_started(timeout=25) -> bool:
    ensure_multi_panel_open()
    purple = get_purple()
    mp = purple.child_window(
        auto_id=MULTIPLAY_VIEW[0],
        control_type=MULTIPLAY_VIEW[1],
    )

    keywords = (
        "подготовка",
        "проверка",
        "обновля",
        "файл применяется",
        "подготовка к запуску",
        "производится установка",
        "игра закрывается",
        "технические работы",
    )

    end_t = time.time() + timeout
    while time.time() < end_t:
        run_btn = find_button_in_multiplay(mp, BTN_GAME_RUN_ID)
        if run_btn is None or not is_really_visible(run_btn):
            return True

        try:
            for el in mp.descendants():
                if (
                    get_control_type(el) == "Button"
                    and get_automation_id(el) == "BtnDisabled"
                    and is_really_visible(el)
                ):
                    return True
        except Exception:
            pass

        try:
            for el in mp.descendants():
                txt = (el.window_text() or "").strip().lower()
                if not txt:
                    continue
                if any(k in txt for k in keywords):
                    return True
        except Exception:
            pass

        time.sleep(0.25)

    return False