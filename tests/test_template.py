from helpers import TEMPLATE


def test_template_keeps_upstream_attribution():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "% Author : Jake Gutierrez" in text
    assert "% Based off of: https://github.com/sb2nov/resume" in text
    assert "% License : MIT" in text


def test_template_uses_the_widened_margins():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert r"\addtolength{\textwidth}{1.5in}" in text
    assert r"\addtolength{\textheight}{1.5in}" in text


def test_template_keeps_the_ats_unicode_lines():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "\n\\input{glyphtounicode}" in text
    assert "\n\\pdfgentounicode=1" in text
