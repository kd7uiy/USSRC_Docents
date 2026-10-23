"""Raster conversion: anything Pillow can open (incl. HEIC, TIFF, EMF/WMF) -> WebP without metadata."""
from pathlib import Path

from PIL import Image, ImageOps, WmfImagePlugin  # noqa: F401  (registers EMF/WMF)
from pillow_heif import register_heif_opener

register_heif_opener()
Image.MAX_IMAGE_PIXELS = None

VECTOR_DPI = 200


def open_image(src: Path) -> Image.Image:
    img = Image.open(src)
    if img.format == "WMF":  # Pillow reports EMF and WMF as WMF; render at a useful resolution
        img.load(dpi=VECTOR_DPI)
    return img


def to_webp(src: Path, dst: Path, max_px: int = 1920, quality: int = 80) -> Path:
    img = open_image(src)
    img = ImageOps.exif_transpose(img)
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() or "transparency" in img.info else "RGB")
    dst.parent.mkdir(parents=True, exist_ok=True)
    # No exif/icc passed -> metadata stripped
    img.save(dst, "WEBP", quality=quality, method=6)
    return dst
