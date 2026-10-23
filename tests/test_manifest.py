from docent.manifest import Manifest


def test_roundtrip_and_skip(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("one")
    m = Manifest(tmp_path / "m.json")
    h = m.hash_file(src)
    assert not m.is_current("a.txt", h)
    m.record("a.txt", h, ["content/a"])
    m.save()

    m2 = Manifest(tmp_path / "m.json")
    assert m2.is_current("a.txt", h)
    src.write_text("two")
    assert not m2.is_current("a.txt", m2.hash_file(src))


def test_removed_sources(tmp_path):
    m = Manifest(tmp_path / "m.json")
    m.record("gone.pptx", "x", ["content/gone"])
    m.record("kept.pptx", "y", ["content/kept"])
    assert m.removed({"kept.pptx"}) == {"gone.pptx": ["content/gone"]}
