"""Tracks which source files were converted, by content hash, so reruns are incremental."""
import hashlib
import json
from pathlib import Path


class Manifest:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.entries = json.loads(self.path.read_text("utf-8")) if self.path.exists() else {}

    @staticmethod
    def hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def is_current(self, rel: str, digest: str) -> bool:
        return self.entries.get(rel, {}).get("sha256") == digest

    def record(self, rel: str, digest: str, outputs: list):
        self.entries[rel] = {"sha256": digest, "outputs": sorted(outputs)}

    def removed(self, present: set) -> dict:
        """Entries whose source no longer exists -> their outputs."""
        return {rel: e["outputs"] for rel, e in self.entries.items() if rel not in present}

    def forget(self, rel: str):
        self.entries.pop(rel, None)

    def save(self):
        self.path.write_text(json.dumps(self.entries, indent=1, sort_keys=True), "utf-8")
