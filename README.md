# USSRC Docents

Static site (Hugo + Geekdoc) built from the docent training materials in `NASA Docents/`.
The raw documents are **not** in Git. Only the converted pages and WebP images under `content/` are.

## Updating content (Windows, this machine)

Requirements: Microsoft PowerPoint (for slide export), Python venv in `.venv`, `pandoc` and `ffmpeg` on PATH.

```powershell
.\.venv\Scripts\python scripts\build_content.py "NASA Docents"
.\.venv\Scripts\python -m pytest tests
hugo server --port 1320
```

- Only new or changed files are converted. Hashes are kept in `content-manifest.json`, and deleted source files have their pages removed.
- `--only "<part of path>"` converts matching files only. `--force` reconverts regardless of hashes.
- Folders become menu sections, and documents become pages: `.pptx` becomes slides with speaker notes, `.docx` becomes a web page, `.pdf` becomes page images with searchable text. Images in a folder become that folder's photo gallery.

## Videos

Each video embedded in a PowerPoint deck is listed in `videos.csv` and extracted to `temp/videos/`. The `url` column decides how a slide shows it:

- a public or unlisted YouTube URL: the slide links to it (preferred)
- `host`: the clip is compressed (≤1280 px, ≤30 fps, no audio) and played on the slide. Use this only for short clips with no public source.
- empty: the slide says "Video not yet linked"

After editing `videos.csv`, rerun with `--force --only "<deck name>"`.

## Publishing

Push to `main`. GitHub Actions builds and deploys to GitHub Pages (Settings → Pages → Source: GitHub Actions).
The site is unlisted: `robots.txt` disallows all crawlers and every page has `noindex`.
