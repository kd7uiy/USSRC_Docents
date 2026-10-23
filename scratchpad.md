# Scratchpad — USSRC Docents site build (2026-10-23)

Plan: C:\Users\tuvas\.claude\plans\review-architecture-md-for-a-atomic-rabbit.md

- [x] Install pandoc + ffmpeg (winget, user scope), venv + requirements
- [x] Scaffold Hugo, vendor Geekdoc v4.1.4 release into themes/
- [x] hugo.toml, noindex/robots, slide/gallery shortcodes, lightbox
- [x] Tests (pytest) + conversion modules in scripts/docent
- [x] Sample conversion of each type, verified in browser (desktop + mobile)
- [x] Full conversion run (5m23s, 0 failures, 1.6 GB -> 68 MB)
- [x] Video source research -> videos.csv (5 linked, 3 need YouTube upload)
- [ ] User review of converted pages (esp. Luke Talley DOCX layout)
- [x] git init (main) — not committed yet
- [ ] First commit; user creates GitHub repo USSRC_Docents and pushes
- [ ] (Optional) fill in <USERNAME> in hugo.toml — CI passes the real Pages URL via --baseURL

## Failures / notes
- Port 1313 is used by another local Hugo project (Belt Hauler); preview uses 1320.
