import sys
from pathlib import Path

import mynotes.data as data_module


def test_app_dir_dev_mode():
    # In dev mode (not frozen), notes should live at the project root —
    # one level above the mynotes/ package directory.
    result = data_module._app_dir()
    expected = Path(data_module.__file__).resolve().parent.parent
    assert result == expected


def test_app_dir_frozen_mode(tmp_path, monkeypatch):
    # Simulate a PyInstaller frozen exe placed in tmp_path.
    fake_exe = tmp_path / "myNotes.exe"
    fake_exe.touch()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_exe))

    result = data_module._app_dir()

    assert result == tmp_path


def test_data_file_is_in_app_dir():
    # DATA_FILE must sit next to the exe (or project root in dev), never inside
    # the package directory itself.
    assert data_module.DATA_FILE.parent == data_module._app_dir()
