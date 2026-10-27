"""Deleting generated outputs, tolerant of brief Windows file locks (e.g. hugo server, a browser)."""
import shutil
import time
from pathlib import Path

ATTEMPTS = 5


def remove_outputs(root: Path, outputs):
    for rel in outputs:
        target = Path(root) / rel
        for attempt in range(ATTEMPTS):
            try:
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
                break
            except PermissionError:
                if attempt == ATTEMPTS - 1:
                    raise
                time.sleep(1 + attempt)


def remove_stale_sections(content: Path, keep):
    """Delete section folders (those with _index.md) whose source folder no longer exists.

    Returns the removed sections as paths relative to content, shallowest first."""
    content, keep = Path(content), {Path(k) for k in keep}
    removed = []
    for index in sorted(content.rglob("_index.md")):
        section = index.parent
        # A removed parent already took its subsections with it.
        if section in keep or not index.exists():
            continue
        rel = section.relative_to(content).as_posix()
        remove_outputs(content, [rel])
        removed.append(rel)
    return removed
