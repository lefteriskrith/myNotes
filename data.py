import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "notes_data.json"


def load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"tags": ["General"], "notes": []}


def save(data: dict) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
