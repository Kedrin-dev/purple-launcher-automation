from game_actions import post_launch_actions
from game_window import snapshot_game_windows, wait_game_after_additional_launch
from purple_control import (
    ensure_multi_panel_open,
    focus_purple,
    get_purple,
    open_checkbox_panel_via_gear,
    set_only_one_checkbox,
    try_press_additional_run_button,
)


def debug_open_multiplay():
    ensure_multi_panel_open()
    print("OK: MultiPlay opened")


def debug_open_checkbox_panel():
    panel = open_checkbox_panel_via_gear()
    print("OK: checkbox panel opened =", panel is not None)


def debug_select_checkbox(idx=0):
    panel = open_checkbox_panel_via_gear()
    ok = set_only_one_checkbox(panel, idx)
    print(f"checkbox idx={idx} -> {ok}")


def debug_press_run():
    focus_purple()
    ensure_multi_panel_open()
    ok = try_press_additional_run_button()
    print("press run result:", ok)


def debug_wait_new_game_window():
    before_unreal, before_titles = snapshot_game_windows()
    input("Сейчас вручную запусти окно игры и нажми Enter...")
    w = wait_game_after_additional_launch(
        before_unreal=before_unreal,
        before_titles=before_titles,
        target_exact_title=None,
        timeout=60,
    )
    print("FOUND WINDOW:", w, "TITLE:", w.window_text())


def debug_post_actions_foreground():
    import win32gui
    from game_window import wrap_hwnd_any

    hwnd = win32gui.GetForegroundWindow()
    w = wrap_hwnd_any(hwnd)
    if w is None:
        raise RuntimeError("Не удалось обернуть foreground окно")

    post_launch_actions(w)
    print("post actions done")


if __name__ == "__main__":
    # Раскомментируй нужный тест
    # debug_open_multiplay()
    # debug_open_checkbox_panel()
    # debug_select_checkbox(0)
    # debug_press_run()
    # debug_wait_new_game_window()
    # debug_post_actions_foreground()
    pass