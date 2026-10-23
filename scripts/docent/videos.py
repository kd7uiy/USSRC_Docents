"""Video registry: videos.csv maps each embedded deck video to a public or YouTube URL.

Unknown videos are extracted to temp/videos/ so they can be identified or uploaded, and
listed in videos.csv for the URL to be filled in. A url of "host" means the clip is
compressed and served from the site itself (only for short clips with no public source).
"""
import csv
import subprocess
import zipfile
from pathlib import Path

HOST = "host"
MAX_WIDTH = 1280
MAX_FPS = 30
FIELDS = ["deck", "slide", "media", "size_mb", "duration_s", "url", "notes"]


class VideoRegistry:
    def __init__(self, csv_path: Path, extract_dir: Path):
        self.csv_path = Path(csv_path)
        self.extract_dir = Path(extract_dir)
        self.rows = {}
        if self.csv_path.exists():
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.rows[(row["deck"], row["media"])] = row

    def link(self, deck_rel: str, deck_path: Path, slide: int, media: str):
        """Returns ("url", url), ("file", extracted_path) for hosted clips, or (None, None)."""
        key = (deck_rel, media)
        row = self.rows.get(key)
        if row is None:
            row = {"deck": deck_rel, "slide": str(slide), "media": media, "url": "", "notes": ""}
            row.update(self._extract(deck_path, deck_rel, media))
            self.rows[key] = row
        url = row["url"].strip()
        if url.lower() == HOST:
            self._extract(deck_path, deck_rel, media)
            return "file", self._dest(deck_rel, media)
        return ("url", url) if url else (None, None)

    def _dest(self, deck_rel: str, media: str) -> Path:
        return self.extract_dir / Path(deck_rel).stem / media

    def _extract(self, deck_path: Path, deck_rel: str, media: str) -> dict:
        dest = self._dest(deck_rel, media)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(deck_path) as z:
            info = z.getinfo(f"ppt/media/{media}")
            if not dest.exists():
                with z.open(info) as s, open(dest, "wb") as d:
                    while chunk := s.read(1 << 20):
                        d.write(chunk)
        return {"size_mb": f"{info.file_size / 2**20:.1f}", "duration_s": _duration(dest)}

    def save(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, FIELDS, extrasaction="ignore")
            w.writeheader()
            for key in sorted(self.rows):
                w.writerow(self.rows[key])


def _duration(path: Path) -> str:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", str(path)],
                             capture_output=True, text=True, check=True).stdout
        return f"{float(out):.0f}"
    except (OSError, subprocess.CalledProcessError, ValueError):
        return ""


def compress_video(src: Path, dst: Path) -> Path:
    """Web-friendly H.264 MP4: at most 1280 px wide and 30 fps, no audio, index at the front."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
                    "-vf", f"scale='min({MAX_WIDTH},iw)':-2,fps='min({MAX_FPS},source_fps)'",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
                    "-an", "-movflags", "+faststart", str(dst)], check=True)
    # Poster from a third of the way in: many clips open on a black frame
    seek = float(_duration(dst) or 0) / 3
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{seek:.2f}", "-i", str(dst),
                    "-frames:v", "1", "-c:v", "libwebp", "-quality", "75",
                    str(dst.with_suffix(".webp"))], check=True)
    return dst
