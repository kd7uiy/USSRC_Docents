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
