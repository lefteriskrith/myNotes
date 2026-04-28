from note_utils import filter_visible_notes, move_note


def make_note(id: str, title: str, tag: str = "General", content: str = "") -> dict:
    return {"id": id, "tag": tag, "title": title, "content": content}


def test_move_note_up_reorders_display_list():
    notes = [
        make_note("1", "A"),
        make_note("2", "B"),
        make_note("3", "C"),
    ]

    moved = move_note(notes, "2", "up", "General", "")

    assert moved is True
    assert [note["id"] for note in notes] == ["1", "3", "2"]
    assert [note["id"] for note in filter_visible_notes(notes, "General", "")] == ["2", "3", "1"]


def test_move_topmost_note_up_is_noop():
    notes = [
        make_note("1", "A"),
        make_note("2", "B"),
        make_note("3", "C"),
    ]

    moved = move_note(notes, "3", "up", "General", "")

    assert moved is False
    assert [note["id"] for note in notes] == ["1", "2", "3"]


def test_move_note_down_with_query_filters_scope():
    notes = [
        make_note("1", "A", content="keep"),
        make_note("2", "B", content="keep"),
        make_note("3", "C", content="skip"),
    ]

    moved = move_note(notes, "2", "down", "General", "keep")

    assert moved is True
    assert [note["id"] for note in notes] == ["2", "1", "3"]
    assert [note["id"] for note in filter_visible_notes(notes, "General", "keep")] == ["1", "2"]
