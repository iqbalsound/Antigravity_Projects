"""Unit tests for the markdown converter module."""

import pytest
from md2html.converter import (
    MarkdownConverter,
    convert_file,
    convert_markdown,
    extract_title,
    wrap_standalone_html,
)
from md2html.styles import DEFAULT_CSS


class TestTitleExtraction:
    def test_atx_header(self):
        md = "# My Document Title\nSome content"
        assert extract_title(md) == "My Document Title"

    def test_atx_header_with_trailing_hashes(self):
        md = "# Header With Hashes ###\nSome content"
        assert extract_title(md) == "Header With Hashes"

    def test_setext_header(self):
        md = "Setext Main Title\n============\nSome content"
        assert extract_title(md) == "Setext Main Title"

    def test_no_h1_returns_none(self):
        md = "## Subtitle\nParagraph without main header"
        assert extract_title(md) is None

    def test_empty_string_returns_none(self):
        assert extract_title("") is None


class TestWrapStandaloneHtml:
    def test_structure(self):
        body = "<p>Hello World</p>"
        html_doc = wrap_standalone_html(body, title="Test Title", css="body { color: red; }")
        assert "<!DOCTYPE html>" in html_doc
        assert '<html lang="en">' in html_doc
        assert '<meta charset="utf-8">' in html_doc
        assert '<meta name="viewport"' in html_doc
        assert "<title>Test Title</title>" in html_doc
        assert "<style>\nbody { color: red; }\n  </style>" in html_doc
        assert '<main class="markdown-body">\n<p>Hello World</p>\n  </main>' in html_doc

    def test_escapes_special_characters_in_title(self):
        html_doc = wrap_standalone_html("<p>Text</p>", title="Rock & Roll <5> ")
        assert "<title>Rock &amp; Roll &lt;5&gt; </title>" in html_doc

    def test_no_css(self):
        html_doc = wrap_standalone_html("<p>Text</p>", title="Title", css=None)
        assert "<style>" not in html_doc


class TestConverterBasic:
    def test_convert_markdown_fragment(self):
        md = "This is **bold** and *italic*."
        html = convert_markdown(md, standalone=False)
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<!DOCTYPE html>" not in html

    def test_convert_headings(self):
        md = "# Heading 1\n## Heading 2\n### Heading 3"
        html = convert_markdown(md, standalone=False)
        assert ">Heading 1</h1>" in html
        assert "<h1" in html
        assert ">Heading 2</h2>" in html
        assert "<h2" in html
        assert ">Heading 3</h3>" in html
        assert "<h3" in html

    def test_convert_lists(self):
        md = "- Item 1\n- Item 2\n\n1. Numbered 1\n2. Numbered 2"
        html = convert_markdown(md, standalone=False)
        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<ol>" in html
        assert "<li>Numbered 1</li>" in html

    def test_convert_fenced_code(self):
        md = "```python\ndef test():\n    return 42\n```"
        html = convert_markdown(md, standalone=False)
        assert "<pre>" in html
        assert "code" in html
        assert "def test():" in html

    def test_convert_table(self):
        md = "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |"
        html = convert_markdown(md, standalone=False)
        assert "<table>" in html
        assert "<thead>" in html
        assert "<th>Header 1</th>" in html
        assert "<tbody>" in html
        assert "<td>Cell 1</td>" in html

    def test_convert_blockquote(self):
        md = "> Quotation goes here"
        html = convert_markdown(md, standalone=False)
        assert "<blockquote>" in html
        assert "Quotation goes here" in html


class TestConverterStandalone:
    def test_standalone_with_default_css(self, sample_markdown):
        html = convert_markdown(sample_markdown, standalone=True)
        assert "<!DOCTYPE html>" in html
        assert "<title>Welcome to Demo</title>" in html
        assert "<style>" in html
        assert ".markdown-body" in html
        assert ">Welcome to Demo</h1>" in html

    def test_standalone_title_override(self, sample_markdown):
        html = convert_markdown(sample_markdown, standalone=True, title="Custom Document Title")
        assert "<title>Custom Document Title</title>" in html

    def test_standalone_no_css(self, sample_markdown):
        html = convert_markdown(sample_markdown, standalone=True, include_css=False)
        assert "<!DOCTYPE html>" in html
        assert "<style>" not in html

    def test_standalone_custom_css(self, sample_markdown):
        custom = ".custom-class { color: green; }"
        html = convert_markdown(sample_markdown, standalone=True, include_css=True, custom_css=custom)
        assert custom in html
        assert ".markdown-body" in html


class TestConvertFile:
    def test_convert_file_success(self, tmp_path, sample_markdown):
        in_file = tmp_path / "test.md"
        out_file = tmp_path / "out" / "test.html"
        in_file.write_text(sample_markdown, encoding="utf-8")

        result_html = convert_file(in_file, output_path=out_file)

        assert out_file.exists()
        assert out_file.read_text(encoding="utf-8") == result_html
        assert "<title>Welcome to Demo</title>" in result_html
        assert "<strong>bold</strong>" in result_html

    def test_convert_file_nonexistent_raises(self, tmp_path):
        missing = tmp_path / "missing.md"
        with pytest.raises(FileNotFoundError):
            convert_file(missing)
