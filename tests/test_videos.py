import shutil
import subprocess
import zipfile

import pytest

from docent.videos import VideoRegistry, compress_video

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not on PATH")


def make_clip(path, size="1920x1080", seconds=2):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"testsrc=size={size}:rate=60:duration={seconds}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)


def make_deck(tmp_path, clip):
    deck = tmp_path / "deck.pptx"
    with zipfile.ZipFile(deck, "w") as z:
        z.write(clip, "ppt/media/media1.mp4")
    return deck


@needs_ffmpeg
def test_host_marker_returns_local_file(tmp_path):
    clip = tmp_path / "c.mp4"
    make_clip(clip)
    deck = make_deck(tmp_path, clip)
    csv_path = tmp_path / "videos.csv"
    csv_path.write_text("deck,slide,media,size_mb,duration_s,url,notes\n"
                        "deck.pptx,3,media1.mp4,1,2,host,\n", encoding="utf-8")
    reg = VideoRegistry(csv_path, tmp_path / "extract")
    kind, value = reg.link("deck.pptx", deck, 3, "media1.mp4")
    assert kind == "file"
    assert value.exists() and value.name == "media1.mp4"


def test_url_and_missing(tmp_path):
    csv_path = tmp_path / "videos.csv"
    csv_path.write_text("deck,slide,media,size_mb,duration_s,url,notes\n"
                        "deck.pptx,3,media1.mp4,1,2,https://example.org/v,\n", encoding="utf-8")
    reg = VideoRegistry(csv_path, tmp_path / "extract")
    assert reg.link("deck.pptx", None, 3, "media1.mp4") == ("url", "https://example.org/v")


@needs_ffmpeg
def test_compress_caps_size_fps_and_drops_audio(tmp_path):
    clip = tmp_path / "big.mp4"
    make_clip(clip)
    out = compress_video(clip, tmp_path / "out" / "v.mp4")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_type,width,height,r_frame_rate", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True, check=True).stdout.split()
    assert probe == ["1280,720,30/1,video"] or probe == ["video,1280,720,30/1"]
    head = out.read_bytes()[:64]
    assert b"moov" in out.read_bytes()[:200_000]  # faststart: index near the start
    assert head[4:8] == b"ftyp"


@needs_ffmpeg
def test_poster_written_next_to_video(tmp_path):
    clip = tmp_path / "c.mp4"
    make_clip(clip, seconds=3)
    out = compress_video(clip, tmp_path / "out" / "v.mp4")
    poster = out.with_suffix(".webp")
    assert poster.exists() and poster.stat().st_size > 0
