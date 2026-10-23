from docent.slugs import slugify, unique_slug


def test_basic():
    assert slugify("Mike Stallcup Training Materials") == "mike-stallcup-training-materials"


def test_punctuation_and_unicode():
    assert slugify("Stallcup, Space Food, R1, 26Feb26") == "stallcup-space-food-r1-26feb26"
    assert slugify("09 - Space Camp-« Graduates in Space") == "09-space-camp-graduates-in-space"
    assert slugify("Margrit von Braun & Us 1") == "margrit-von-braun-and-us-1"
    assert slugify("_a Sat V Tour - 9-15-2024 Rev 10B") == "a-sat-v-tour-9-15-2024-rev-10b"


def test_empty_falls_back():
    assert slugify("«»") == "item"


def test_unique():
    used = set()
    assert unique_slug("a", used) == "a"
    assert unique_slug("a", used) == "a-2"
    assert unique_slug("a", used) == "a-3"
