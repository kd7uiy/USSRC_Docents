"""Fails if converted content would exceed GitHub Pages-friendly limits."""
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1] / "content"
MAX_FILE = 5 * 1024 * 1024
MAX_TOTAL = 250 * 1024 * 1024


def test_size_budget():
    files = [p for p in CONTENT.rglob("*") if p.is_file()]
    big = [(p, p.stat().st_size) for p in files if p.stat().st_size > MAX_FILE]
    assert not big, f"files over 5 MB: {big}"
    total = sum(p.stat().st_size for p in files)
    assert total <= MAX_TOTAL, f"content is {total / 2**20:.0f} MB"
