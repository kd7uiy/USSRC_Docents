import shutil

import pytest

from docent import outputs


def test_removes_files_and_dirs(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "x.webp").write_text("x")
    (tmp_path / "f.webp").write_text("y")
    outputs.remove_outputs(tmp_path, ["d", "f.webp", "missing"])
    assert not (tmp_path / "d").exists() and not (tmp_path / "f.webp").exists()


def test_retries_when_file_is_locked(tmp_path, monkeypatch):
    (tmp_path / "d").mkdir()
    real, calls = shutil.rmtree, []

    def flaky(path, *a, **k):
        calls.append(path)
        if len(calls) == 1:
            raise PermissionError("locked by another process")
        real(path, *a, **k)

    monkeypatch.setattr(outputs.shutil, "rmtree", flaky)
    monkeypatch.setattr(outputs.time, "sleep", lambda s: None)
    outputs.remove_outputs(tmp_path, ["d"])
    assert len(calls) == 2 and not (tmp_path / "d").exists()


def test_gives_up_after_retries(tmp_path, monkeypatch):
    (tmp_path / "d").mkdir()
    monkeypatch.setattr(outputs.shutil, "rmtree", lambda *a, **k: (_ for _ in ()).throw(PermissionError("locked")))
    monkeypatch.setattr(outputs.time, "sleep", lambda s: None)
    with pytest.raises(PermissionError):
        outputs.remove_outputs(tmp_path, ["d"])


def test_removes_sections_of_deleted_folders(tmp_path):
    for d in ("kept", "kept/sub", "gone", "gone/sub"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "_index.md").write_text("x")
    (tmp_path / "kept" / "doc").mkdir()
    (tmp_path / "kept" / "doc" / "index.md").write_text("page bundle, not a section")
    removed = outputs.remove_stale_sections(tmp_path, {tmp_path, tmp_path / "kept", tmp_path / "kept" / "sub"})
    assert removed == ["gone"]
    assert not (tmp_path / "gone").exists()
    assert (tmp_path / "kept" / "sub" / "_index.md").exists() and (tmp_path / "kept" / "doc").exists()
