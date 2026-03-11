import time

from config import DEBUG


def log(msg: str) -> None:
    if DEBUG:
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")


def safe_invoke_or_click(ctrl) -> bool:
    try:
        ctrl.wrapper_object().invoke()
        return True
    except Exception:
        try:
            ctrl.click_input()
            return True
        except Exception:
            return False


def get_automation_id(w) -> str:
    try:
        return getattr(w.element_info, "automation_id", "") or ""
    except Exception:
        return ""


def get_control_type(w) -> str:
    try:
        return w.element_info.control_type
    except Exception:
        return ""


def is_really_visible(el) -> bool:
    """
    UIA sometimes returns ghost elements with rect=(0,0,0,0).
    """
    try:
        if hasattr(el, "is_visible") and not el.is_visible():
            return False
        r = el.rectangle()
        return (r.right - r.left) > 5 and (r.bottom - r.top) > 5
    except Exception:
        return False