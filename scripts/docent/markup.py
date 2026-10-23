"""Helpers for writing Hugo Markdown safely."""
import re

import yaml


def front_matter(data: dict) -> str:
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{body}---\n\n"


def shortcode_text(text: str) -> str:
    """Plain text that is safe inside a shortcode body (no Hugo template/shortcode delimiters)."""
    return text.replace("{{", "{​{").replace("}}", "}​}").strip()


_MEDIA = re.compile(r"""(?P<pre>!\[[^\]]*\]\(|src=")(?P<path>[^)"]*?/media/(?P<name>[^/)"]+))(?P<post>[)"])""")
_STYLE = re.compile(r'\s+style="[^"]*"')


def rewrite_media_links(md: str, mapping: dict) -> str:
    """Point pandoc's extracted-media paths at converted bundle images and drop fixed sizes."""
    def repl(m):
        new = mapping.get(m.group("name"))
        return f"{m.group('pre')}{new}{m.group('post')}" if new else m.group(0)

    md = _MEDIA.sub(repl, md)
    return _STYLE.sub("", md)
