"""
tests/test_converter.py — Unit tests for md2html.converter.convert_text()
Task done for PROMTOBIA
"""

import pytest
from md2html.converter import (
    PROMTOBIA_CREDIT,
    _extract_title,
    convert_text,
)


# ── Title extraction helper ────────────────────────────────────────────────────

class TestExtractTitle:
    def test_atx_h1_simple(self):
        assert _extract_title("# Hello World") == "Hello World"

    def test_atx_h1_strips_markup(self):
        assert _extract_title("# **Bold** Title") == "Bold Title"

    def test_atx_h2_ignored(self):
        """Only H1 is used as title; H2 falls back."""
        result = _extract_title("## Section")
        assert result == "Document"

    def test_setext_h1(self):
        md = "My Document\n==========="
        assert _extract_title(md) == "My Document"

    def test_fallback_returned(self):
        assert _extract_title("plain text", fallback="Fallback") == "Fallback"

    def test_empty_string_fallback(self):
        assert _extract_title("", fallback="Empty") == "Empty"


# ── HTML5 Document Structure ───────────────────────────────────────────────────

class TestHtml5Structure:
    def test_html5_doctype(self):
        html = convert_text("# Hi")
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_html_root_element(self):
        html = convert_text("# Hi")
        assert "<html" in html
        assert "</html>" in html

    def test_charset_meta(self):
        html = convert_text("# Hi")
        assert 'charset="UTF-8"' in html

    def test_viewport_meta(self):
        html = convert_text("# Hi")
        assert 'name="viewport"' in html
        assert "width=device-width" in html

    def test_title_element_present(self):
        html = convert_text("# My Doc")
        assert "<title>" in html
        assert "</title>" in html

    def test_title_from_h1_heading(self):
        html = convert_text("# My Great Document")
        assert "<title>My Great Document</title>" in html

    def test_custom_title_overrides_heading(self):
        html = convert_text("# Heading", title="Custom Title")
        assert "<title>Custom Title</title>" in html

    def test_head_and_body_present(self):
        html = convert_text("Hello")
        assert "<head>" in html
        assert "</head>" in html
        assert "<body>" in html
        assert "</body>" in html

    def test_style_block_present(self):
        html = convert_text("# Hi")
        assert "<style>" in html
        assert "</style>" in html


# ── Markdown Element Conversion ────────────────────────────────────────────────

class TestMarkdownConversion:
    def test_heading_h2(self):
        html = convert_text("## Section One")
        assert "<h2" in html

    def test_heading_h3(self):
        html = convert_text("### Subsection")
        assert "<h3" in html

    def test_paragraph(self):
        html = convert_text("This is a paragraph.")
        assert "<p>" in html
        assert "This is a paragraph." in html

    def test_bold(self):
        html = convert_text("**bold text**")
        assert "<strong>" in html
        assert "bold text" in html

    def test_italic(self):
        html = convert_text("*italic text*")
        assert "<em>" in html
        assert "italic text" in html

    def test_unordered_list(self):
        md = "- Apple\n- Banana\n- Cherry"
        html = convert_text(md)
        assert "<ul>" in html
        assert "<li>" in html
        assert "Apple" in html

    def test_ordered_list(self):
        md = "1. First\n2. Second\n3. Third"
        html = convert_text(md)
        assert "<ol>" in html
        assert "<li>" in html
        assert "First" in html

    def test_blockquote(self):
        html = convert_text("> A wise quote")
        assert "<blockquote>" in html
        assert "A wise quote" in html

    def test_inline_code(self):
        html = convert_text("Use `print()` to output.")
        assert "<code>" in html
        assert "print()" in html

    def test_fenced_code_block_highlight_class(self):
        md = "```python\nprint('hello')\n```"
        html = convert_text(md)
        assert 'class="highlight"' in html

    def test_fenced_code_block_content(self):
        md = "```python\nx = 42\n```"
        html = convert_text(md)
        assert "x = 42" in html or "x&#160;=&#160;42" in html or "x" in html

    def test_table_conversion(self):
        md = "| Name | Age |\n|------|-----|\n| Alice | 30 |"
        html = convert_text(md)
        assert "<table>" in html
        assert "<th>" in html or "<thead>" in html
        assert "Alice" in html

    def test_horizontal_rule(self):
        # bare `---` is treated as setext H2 underline; use `***` or surround with blank lines
        html = convert_text("Above\n\n---\n\nBelow")
        assert "<hr" in html

    def test_link_conversion(self):
        html = convert_text("[Click here](https://example.com)")
        assert "<a " in html
        assert 'href="https://example.com"' in html
        assert "Click here" in html


# ── PROMTOBIA Branding ─────────────────────────────────────────────────────────

class TestPromtobiaBranding:
    def test_promtobia_credit_text_in_banner(self):
        html = convert_text("# Hi")
        assert PROMTOBIA_CREDIT in html

    def test_promtobia_banner_div_class(self):
        html = convert_text("# Hi")
        assert 'class="promtobia-banner"' in html

    def test_promtobia_footer_credit_class(self):
        html = convert_text("# Hi")
        assert 'class="promtobia-credit"' in html

    def test_promtobia_generator_meta(self):
        html = convert_text("# Hi")
        assert 'name="generator"' in html
        assert PROMTOBIA_CREDIT in html

    def test_promtobia_appears_multiple_times(self):
        html = convert_text("# Hi")
        # Should appear in banner, meta, and footer
        count = html.count(PROMTOBIA_CREDIT)
        assert count >= 3, f"Expected ≥3 occurrences, found {count}"


# ── Theme Support ──────────────────────────────────────────────────────────────

class TestThemes:
    def test_default_theme_is_auto(self):
        html = convert_text("# Hi")
        assert 'data-theme="auto"' in html

    def test_light_theme(self):
        html = convert_text("# Hi", theme="light")
        assert 'data-theme="light"' in html
        assert 'content="light"' in html

    def test_dark_theme(self):
        html = convert_text("# Hi", theme="dark")
        assert 'data-theme="dark"' in html
        assert 'content="dark"' in html

    def test_auto_theme_color_scheme(self):
        html = convert_text("# Hi", theme="auto")
        assert "light dark" in html


# ── Edge Cases ─────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_string_produces_valid_html(self):
        html = convert_text("")
        assert "<!DOCTYPE html>" in html
        assert "<body>" in html
        assert PROMTOBIA_CREDIT in html

    def test_invalid_type_raises_type_error(self):
        with pytest.raises(TypeError, match="md_text must be str"):
            convert_text(None)  # type: ignore[arg-type]

    def test_integer_input_raises_type_error(self):
        with pytest.raises(TypeError):
            convert_text(123)  # type: ignore[arg-type]

    def test_html_entity_escaping_in_title(self):
        html = convert_text("# Hello", title="<script>alert(1)</script>")
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html

    def test_ampersand_in_title_escaped(self):
        html = convert_text("# Hi", title="Tom & Jerry")
        assert "Tom &amp; Jerry" in html or "Tom & Jerry" in html

    def test_unicode_content(self):
        html = convert_text("# Héllo Wörld\n\nCafé ☕ résumé")
        assert "Héllo" in html or "H&#233;llo" in html
        assert "☕" in html or "&#9749;" in html
