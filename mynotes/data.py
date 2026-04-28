import sys
import json
from pathlib import Path


def _app_dir() -> Path:
    # When running as a frozen exe, __file__ points to a temp extraction dir,
    # so we use sys.executable to find where the exe actually lives.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    # In dev mode, store notes at the project root (one level above this package).
    return Path(__file__).resolve().parent.parent


DATA_FILE = _app_dir() / "notes_data.json"


def load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"tags": ["General"], "notes": []}


def save(data: dict) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
