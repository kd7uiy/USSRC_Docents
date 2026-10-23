"""URL slugs for folder and file names."""
import re
import unicodedata


def slugify(name: str) -> str:
    text = name.replace("&", " and ")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "item"


def unique_slug(slug: str, used: set) -> str:
    """Return slug, or slug-2, slug-3... if already taken; records the result in used."""
    candidate, n = slug, 2
    while candidate in used:
        candidate, n = f"{slug}-{n}", n + 1
    used.add(candidate)
    return candidate
