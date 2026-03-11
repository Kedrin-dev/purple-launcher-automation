from config import CHECKBOX_DIRECTION, GAME_TITLE_KEY, GAME_WAIT_TIMEOUT
from game_actions import post_launch_actions
from game_window import (
    any_game_window_visible,
    force_foreground,
    snapshot_game_windows,
    wait_game_after_additional_launch,
    wait_main_game_foreground,
    wrap_hwnd_any,
)
from helpers import log
from purple_control import (
    click_ok_in_panel,
    ensure_multi_panel_open,
    focus_purple,
    get_checkboxes,
    get_selected_account_name_from_multiplay,
    open_checkbox_panel_via_gear,
    press_play_in_purple,
    set_only_one_checkbox,
    try_press_additional_run_button,
    wait_additional_launch_started,
    wait_multiplay_applied,
)
from state_storage import load_index, save_index


def launch_one_additional_current() -> bool:
    before_unreal, before_titles = snapshot_game_windows()

    acc = get_selected_account_name_from_multiplay()
    if acc:
        log(f"Текущий выбранный аккаунт в мульти-панели: {acc!r}")
        target_exact_title = f"{GAME_TITLE_KEY}{acc}".strip()
    else:
        log("Имя выбранного аккаунта не распознано (ок).")
        target_exact_title = None

    pressed = try_press_additional_run_button()
    if not pressed:
        return False

    started = wait_additional_launch_started(timeout=25)
    log(f"Старт по статусам Purple: {'ДА' if started else 'НЕТ/НЕ ЯВНО'}")

    try:
        game_win = wait_game_after_additional_launch(
            before_unreal=before_unreal,
            before_titles=before_titles,
            target_exact_title=target_exact_title,
            timeout=GAME_WAIT_TIMEOUT,
        )
    except TimeoutError as e:
        log(f"⚠️ Не смог найти/активировать окно игры после запуска: {e}")
        focus_purple()
        ensure_multi_panel_open()
        return False

    post_launch_actions(game_win)
    focus_purple()
    ensure_multi_panel_open()
    return True


def launch_all_additional_accounts() -> None:
    log("=== Шаг 4: доп. аккаунты ===")
    ensure_multi_panel_open()

    panel = open_checkbox_panel_via_gear()
    total = len(get_checkboxes(panel))
    log(f"Всего чекбоксов (аккаунтов): {total}")

    try:
        click_ok_in_panel(panel)
    except Exception:
        pass

    if total == 0:
        log("0 чекбоксов -> доп. аккаунтов нет.")
        return

    start_idx = load_index()

    if CHECKBOX_DIRECTION == "bottomup":
        order = list(range(total - 1, -1, -1))
        if 0 <= start_idx < len(order):
            order = order[start_idx:]
    else:
        order = list(range(start_idx, total))

    for step, idx in enumerate(order, start=1):
        log(f"--- Выбираю чекбокс idx={idx} ({step}/{len(order)}) ---")
        save_index(idx)

        panel = open_checkbox_panel_via_gear()
        ok = set_only_one_checkbox(panel, idx)
        if not ok:
            log("Чекбокс не выставился надёжно -> следующий")
            continue

        log("Жду, пока Purple применит выбор чекбокса...")
        applied = wait_multiplay_applied(timeout=12)
        log(f"Применение выбора: {'OK' if applied else 'TIMEOUT'}")

        launched = launch_one_additional_current()
        if launched:
            log(f"Аккаунт idx={idx} запущен и обработан ✅ -> следующий")
        else:
            log(f"Аккаунт idx={idx}: не удалось запустить (или уже запущен) -> следующий")

    save_index(0)
    log("Доп. аккаунты обработаны ✅")


def main():
    existing = any_game_window_visible()
    if existing:
        hwnd, title = existing
        log(f"Игра уже запущена/видна: {title} -> пропускаю Play")
        force_foreground(hwnd)
        game = wrap_hwnd_any(hwnd)
        if game is None:
            game = wait_main_game_foreground(timeout=GAME_WAIT_TIMEOUT)
    else:
        log("1) Запускаю основной аккаунт (Play)...")
        press_play_in_purple()

        log("2) Жду, пока окно игры станет активным (основной аккаунт)...")
        game = wait_main_game_foreground(timeout=GAME_WAIT_TIMEOUT)

    log("3) Основной аккаунт: пост-действия...")
    post_launch_actions(game)

    log("4) Доп. аккаунты через шестерёнку (по одному)...")
    launch_all_additional_accounts()

    log("Готово ✅")


if __name__ == "__main__":
    main()