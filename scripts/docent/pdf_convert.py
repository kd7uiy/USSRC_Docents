"""PDF -> page bundle of page WebPs with the extracted text under each page (for search)."""
from pathlib import Path

import pymupdf as fitz
from PIL import Image

from .markup import front_matter, shortcode_text

PAGE_WIDTH = 1600


def convert(src: Path, bundle: Path, title: str, weight: int) -> int:
    (bundle / "pages").mkdir(parents=True, exist_ok=True)
    parts = [front_matter({"title": title, "weight": weight, "docentType": "pdf"})]
    with fitz.open(src) as doc:
        for i, page in enumerate(doc, start=1):
            zoom = min(PAGE_WIDTH / page.rect.width, 200 / 72)  # cap at 200 dpi for small pages
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img.save(bundle / "pages" / f"page-{i:03d}.webp", "WEBP", quality=80, method=6)
            text = shortcode_text(page.get_text("text"))
            parts.append(f'{{{{< slide label="Page" n="{i}" img="pages/page-{i:03d}.webp" collapse="true" >}}}}\n'
                         f"{text}\n{{{{< /slide >}}}}\n\n")
        n = doc.page_count
    (bundle / "index.md").write_text("".join(parts), "utf-8")
    return n
