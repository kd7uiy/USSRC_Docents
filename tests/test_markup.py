from docent.markup import front_matter, shortcode_text, rewrite_media_links


def test_shortcode_text_neutralises_delimiters():
    assert "{{<" not in shortcode_text("see {{< x >}} and {{% y %}}")
    assert "{{" not in shortcode_text("{{ .Title }}")


def test_front_matter_quotes_titles():
    fm = front_matter({"title": "Stallcup, Space Food: R1", "weight": 3})
    assert fm.startswith("---\n") and fm.endswith("---\n\n")
    assert "title: 'Stallcup, Space Food: R1'" in fm


def test_rewrite_media_links():
    md = ('![](C:/tmp/x/media/image1.emf)\n'
          '<img src="C:/tmp/x/media/image22.png" style="width:6in" />')
    out = rewrite_media_links(md, {"image1.emf": "images/image1.webp",
                                   "image22.png": "images/image22.webp"})
    assert "![](images/image1.webp)" in out
    assert 'src="images/image22.webp"' in out
    assert "style=" not in out
