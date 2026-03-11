from config import STATE_FILE


def load_index() -> int:
    try:
        return int(STATE_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def save_index(i: int) -> None:
    STATE_FILE.write_text(str(i), encoding="utf-8")