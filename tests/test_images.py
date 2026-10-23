from pathlib import Path

from PIL import Image

from docent.images import to_webp

FIXTURES = Path(__file__).parent / "fixtures"


def test_jpeg_resized_oriented_and_stripped(tmp_path):
    src = tmp_path / "big.jpg"
    img = Image.new("RGB", (4000, 1000), "red")
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 CW on display
    exif[0x010F] = "SecretCam"
    img.save(src, exif=exif)

    dst = tmp_path / "out.webp"
    to_webp(src, dst, max_px=1920)
    out = Image.open(dst)
    assert out.format == "WEBP"
    assert out.size == (480, 1920)  # rotated, then fit inside 1920
    assert not out.getexif()


def test_small_image_not_upscaled(tmp_path):
    src = tmp_path / "s.png"
    Image.new("RGBA", (300, 200), (0, 0, 255, 128)).save(src)
    dst = tmp_path / "s.webp"
    to_webp(src, dst, max_px=1920)
    assert Image.open(dst).size == (300, 200)


def test_emf_rendered(tmp_path):
    dst = tmp_path / "e.webp"
    to_webp(FIXTURES / "small.emf", dst, max_px=1600)
    out = Image.open(dst)
    assert out.width > 500  # rendered at high dpi, not the 72dpi placeholder
