import mynotes.data as data
from mynotes.note_utils import filter_visible_notes


def test_data_save_and_load_roundtrip(tmp_path, monkeypatch):
    sample = {
        "tags": ["General"],
        "notes": [
            {"id": "1", "tag": "General", "title": "Hello", "content": "world"}
        ],
    }
    data_file = tmp_path / "notes_data.json"
    monkeypatch.setattr(data, "DATA_FILE", data_file)

    data.save(sample)
    loaded = data.load()

    assert loaded == sample


def test_filter_visible_notes_respects_tag_and_query():
    notes = [
        {"id": "1", "tag": "General", "title": "Hello", "content": "World"},
        {"id": "2", "tag": "Work", "title": "Meeting", "content": "Agenda"},
    ]

    visible = filter_visible_notes(notes, "General", "world")
    assert len(visible) == 1
    assert visible[0]["id"] == "1"
