# Long-term memory

- 2026-10-23: Geekdoc is vendored from the release tarball (prebuilt assets), not a git submodule — the source repo needs an npm build. Update by re-downloading `hugo-geekdoc.tar.gz` into themes/hugo-geekdoc.
- 2026-10-23: Pillow renders EMF/WMF natively on Windows (`img.load(dpi=200)`); the Luke Talley DOCX diagrams are EMF-wrapped photos. Conversion must run on Windows (also needed for PowerPoint COM slide export).
- 2026-10-23: Most PPTX size is embedded video (~1.18 GB). Videos are never hosted; `videos.csv` maps (deck, media) -> URL and is read on every run.
- 2026-10-23: Geekdoc search indexes `.Plain`, so shortcode output (slide notes, PDF page text) is searchable.
- 2026-10-23: pandoc and ffmpeg are installed via winget at user scope; add `%LOCALAPPDATA%\Pandoc` and `%LOCALAPPDATA%\Microsoft\WinGet\Links` to PATH in shells started before install.
- 2026-10-23: `videos.csv` url = "host" compresses a clip into the deck bundle (videos/slide-NNN.mp4 + .webp poster from 1/3 in; first frames are often black). Used only for short clips with no public source.
- 2026-10-23: On Windows, the running hugo server/browser can lock output files during reconversion. Removal now retries, and the manifest entry is forgotten before old outputs are deleted, so a crash never leaves a half-deleted bundle marked current.
