# Architecture: USSRC Docents Document Library

*Revised 2026-10-23. Replaces the original GitHub Pages + LibreOffice draft.*

## 1. Overview

A zero-cost, public-but-unlisted static site that mirrors the folder tree of `NASA Docents/`.
Conversion runs **locally on Windows**. The raw documents never enter Git. Converted Markdown and WebP do, and GitHub Actions builds them with Hugo and deploys to GitHub Pages.

```
NASA Docents/ (raw, git-ignored, 1.6 GB)
   │  scripts/build_content.py  (Windows: PowerPoint COM, pandoc, PyMuPDF, Pillow)
   ▼
content/ (Markdown + WebP page bundles, committed, target < 250 MB)
   │  git push → GitHub Actions → hugo --gc --minify
   ▼
GitHub Pages (public repo USSRC_Docents, noindex + robots Disallow)
```

## 2. Stack

| Layer | Choice | Why |
|---|---|---|
| Generator | Hugo 0.164 (standard edition is enough) | Fast; theme assets are prebuilt |
| Theme | Geekdoc v4.1.4, **vendored release tarball** in `themes/hugo-geekdoc` | Collapsible tree nav, full-text search, mobile. The git repo would need an npm build |
| PPTX | PowerPoint COM `Slide.Export` (1600 px) → WebP q80; python-pptx for notes and video detection | Exact rendering; Office is installed |
| DOCX | pandoc → GFM; media → WebP (EMF rendered by Pillow at 200 dpi) | Native, searchable pages |
| PDF | PyMuPDF renders pages → WebP, `get_text()` under each page | Consistent with slides, searchable, no downloadable PDF |
| Images | Pillow + pillow-heif: EXIF-rotate, strip metadata, max 1920 px, WebP q80, 480 px thumbnails | Photo gallery |
| Video | Not hosted. `videos.csv` maps each embedded video to a public/YouTube URL | Videos were ~1.18 GB of the decks |
| Hosting | GitHub Pages via Actions | $0 |

## 3. Layout

```
content/
  _index.md                         # hand-written landing page
  <folder-slug>/_index.md           # generated: title = original folder name, toc-tree and/or gallery
  <folder-slug>/<doc-slug>/index.md # page bundle per document
                     slides/ | pages/ | images/   # WebP resources
  <folder-slug>/images/, thumbs/    # gallery images for that folder
layouts/
  robots.txt                        # Disallow: /
  partials/head/custom.html         # noindex meta, docent.css, lightbox.js
  shortcodes/slide.html             # slide or PDF page + notes/text (+ video link)
  shortcodes/gallery.html           # thumbnail grid, captions from resource params
static/css/docent.css, static/js/lightbox.js
scripts/build_content.py            # orchestrator (incremental via content-manifest.json)
scripts/docent/*.py                 # slugs, manifest, images, pptx/docx/pdf converters, videos
tests/                              # pytest, incl. size budget (≤5 MB/file, ≤250 MB total)
videos.csv                          # deck video → URL registry (committed)
```

URLs use clean slugs (`/mike-stallcup-training-materials/stallcup-jwst-10mar25-1/`). Menu titles keep the original names, and the menu is ordered by source filename.

## 4. Pipeline rules

- Incremental: the sha256 of each source is stored in `content-manifest.json`. Changed sources have their old outputs removed before reconversion, and deleted sources have their outputs removed.
- Text inside slide notes, PDF text and DOCX bodies is neutralized so `{{` can never be read as a Hugo shortcode.
- A per-file failure is logged and skipped. The run exits non-zero and lists the failures.

## 5. Visibility

`robots.txt` disallows everything, every page carries `<meta name="robots" content="noindex, nofollow">`, and sitemap/RSS/taxonomies are disabled. The repo itself is public, so the converted content is readable on GitHub.

## 6. Deploy

`.github/workflows/deploy.yml` installs Hugo 0.164.0, runs `hugo --gc --minify` with the Pages base URL, and deploys with `actions/deploy-pages`. In the repo settings: Pages → Source: GitHub Actions.
