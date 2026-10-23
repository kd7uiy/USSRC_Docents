"""Convert the source document tree into Hugo content.

Usage: python scripts/build_content.py "NASA Docents" [--only SUBSTRING] [--force]

Each source folder becomes a section (content/<slug>/_index.md). Documents become page
bundles beside it; images in a folder become that folder's gallery. Unchanged files are
skipped using content-manifest.json; outputs of deleted sources are removed.
"""
import argparse
import shutil
import sys
import traceback
from pathlib import Path

from docent import docx_convert, pdf_convert, pptx_convert
from docent.images import to_webp
from docent.manifest import Manifest
from docent.markup import front_matter
from docent.slugs import slugify, unique_slug
from docent.videos import VideoRegistry

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".gif", ".webp"}
DOC_CONVERTERS = {".pptx": "pptx", ".docx": "docx", ".pdf": "pdf"}


def plan_folder(folder: Path):
    """Deterministic slugs for a folder's children: (subdirs, docs, images) as (path, slug)."""
    used = {"images", "thumbs"}
    subdirs, docs, images = [], [], []
    for p in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if p.name.startswith(("~$", ".")):
            continue
        if p.is_dir():
            subdirs.append((p, unique_slug(slugify(p.name), used)))
        elif p.suffix.lower() in DOC_CONVERTERS:
            docs.append((p, unique_slug(slugify(p.stem), used)))
    img_used = set()
    for p in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            images.append((p, unique_slug(slugify(p.stem), img_used)))
    return subdirs, docs, images


def remove_outputs(outputs):
    for rel in outputs:
        target = ROOT / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--only", help="convert only sources whose path contains this text")
    ap.add_argument("--force", action="store_true", help="ignore the manifest and reconvert")
    args = ap.parse_args()

    source = Path(args.source).resolve()
    manifest = Manifest(ROOT / "content-manifest.json")
    videos = VideoRegistry(ROOT / "videos.csv", ROOT / "temp" / "videos")
    present, failures = set(), []

    def process(src: Path, kind: str, run, outputs):
        rel = src.relative_to(source).as_posix()
        present.add(rel)
        if args.only and args.only.lower() not in rel.lower():
            return
        digest = manifest.hash_file(src)
        if manifest.is_current(rel, digest) and not args.force:
            return
        print(f"[{kind}] {rel}", flush=True)
        old = manifest.entries.get(rel, {}).get("outputs", [])
        remove_outputs(old)
        try:
            run()
            manifest.record(rel, digest, outputs)
            manifest.save()
        except Exception:
            failures.append(rel)
            traceback.print_exc()
            remove_outputs(outputs)
            manifest.forget(rel)

    def walk(folder: Path, out: Path, title: str, weight: int, is_root=False):
        out.mkdir(parents=True, exist_ok=True)
        subdirs, docs, images = plan_folder(folder)

        for i, (src, slug) in enumerate(docs):
            bundle = out / slug
            kind = DOC_CONVERTERS[src.suffix.lower()]
            w = (i + 1) * 10
            if kind == "pptx":
                run = lambda s=src, b=bundle, w=w: pptx_convert.convert(
                    s, b, s.stem, w,
                    lambda deck, n, media: videos.link(deck.relative_to(source).as_posix(), deck, n, media))
            elif kind == "docx":
                run = lambda s=src, b=bundle, w=w: docx_convert.convert(s, b, s.stem, w)
            else:
                run = lambda s=src, b=bundle, w=w: pdf_convert.convert(s, b, s.stem, w)
            process(src, kind, run, [bundle.relative_to(ROOT).as_posix()])

        resources = []
        for src, slug in images:
            full, thumb = out / "images" / f"{slug}.webp", out / "thumbs" / f"{slug}.webp"
            def run(s=src, f=full, t=thumb):
                to_webp(s, f, max_px=1920)
                to_webp(f, t, max_px=480, quality=70)
            process(src, "image", run, [p.relative_to(ROOT).as_posix() for p in (full, thumb)])
            resources.append({"src": f"images/{slug}.webp", "params": {"caption": src.stem}})

        index = out / "_index.md"
        if not is_root:
            fm = {"title": title, "weight": weight, "geekdocCollapseSection": True}
            if resources:
                fm["resources"] = resources
            body = "{{< toc-tree >}}\n" if docs or subdirs else ""
            body += "\n{{< gallery >}}\n" if resources else ""
            index.write_text(front_matter(fm) + body, "utf-8")

        for i, (src, slug) in enumerate(subdirs):
            walk(src, out / slug, src.name, (i + 1) * 10)

    walk(source, CONTENT, "", 0, is_root=True)

    for rel, outputs in manifest.removed(present).items():
        print(f"[removed] {rel}")
        remove_outputs(outputs)
        manifest.forget(rel)
    manifest.save()
    videos.save()

    if failures:
        print(f"\nFAILED ({len(failures)}):\n  " + "\n  ".join(failures))
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()
