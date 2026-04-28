from __future__ import annotations

from typing import Iterable


def filter_visible_notes(raw_notes: Iterable[dict], selected_tag: str, query: str = "") -> list[dict]:
    query = (query or "").lower()
    return [
        note for note in reversed(list(raw_notes))
        if note.get("tag") == selected_tag
        and (
            not query
            or query in note.get("title", "").lower()
            or query in note.get("content", "").lower()
        )
    ]


def _move_before(notes: list[dict], note: dict, target: dict) -> bool:
    if note is target or note == target:
        return False
    notes.remove(note)
    notes.insert(notes.index(target), note)
    return True


def _move_after(notes: list[dict], note: dict, target: dict) -> bool:
    if note is target or note == target:
        return False
    notes.remove(note)
    notes.insert(notes.index(target) + 1, note)
    return True


def move_note(notes: list[dict], note_id: str, direction: str, selected_tag: str, query: str = "") -> bool:
    visible = filter_visible_notes(notes, selected_tag, query)
    note = next((n for n in visible if n.get("id") == note_id), None)
    if note is None:
        return False

    idx = visible.index(note)
    if direction == "up" and idx > 0:
        return _move_after(notes, note, visible[idx - 1])
    if direction == "down" and idx < len(visible) - 1:
        return _move_before(notes, note, visible[idx + 1])
    return False
