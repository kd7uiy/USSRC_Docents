"""Word document -> Markdown page bundle via pandoc, with embedded media converted to WebP."""
import re
import subprocess
import tempfile
from pathlib import Path

from .images import to_webp
from .markup import front_matter, rewrite_media_links

DOC_IMAGE_MAX = 1600


def convert(src: Path, bundle: Path, title: str, weight: int) -> int:
    (bundle / "images").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        md = subprocess.run(
            ["pandoc", str(src), "--from=docx", "--to=gfm", "--wrap=none",
             f"--extract-media={tmp}"],
            check=True, capture_output=True, text=True, encoding="utf-8").stdout
        mapping = {}
        for media in sorted(Path(tmp, "media").glob("*")):
            out = Path("images") / (media.stem + ".webp")
            to_webp(media, bundle / out, max_px=DOC_IMAGE_MAX)
            mapping[media.name] = out.as_posix()
    md = rewrite_media_links(md, mapping)
    md = md.replace("{{", "{​{")  # never let document text look like a Hugo shortcode
    md = re.sub(r"\n{3,}", "\n\n", md)
    body = front_matter({"title": title, "weight": weight, "docentType": "document"}) + md
    (bundle / "index.md").write_text(body, "utf-8")
    return len(mapping)
