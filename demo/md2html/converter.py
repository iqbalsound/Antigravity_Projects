"""Core Markdown to clean HTML conversion module."""

import html
import re
from pathlib import Path
from typing import List, Optional

import markdown
from md2html.styles import DEFAULT_CSS

DEFAULT_EXTENSIONS = [
    "fenced_code",
    "tables",
    "toc",
    "sane_lists",
    "nl2br",
    "smarty",
]


def extract_title(markdown_text: str) -> Optional[str]:
    """Extract document title from the first H1 header in markdown text."""
    lines = markdown_text.splitlines()
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # ATX header: # Title
        if line_stripped.startswith("#") and not line_stripped.startswith("##"):
            title = re.sub(r"^#\s*", "", line_stripped)
            # Remove trailing closing hashes if present
            title = re.sub(r"\s*#+$", "", title)
            return title.strip()
        # Setext header: Title followed by ===
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and set(next_line) == {"="} and len(next_line) >= 2:
                return line_stripped
    return None


def wrap_standalone_html(
    body_html: str,
    title: str = "Document",
    css: Optional[str] = None,
) -> str:
    """Wrap HTML body content into a full semantic HTML5 document."""
    escaped_title = html.escape(title)
    css_block = f"  <style>\n{css}\n  </style>\n" if css else ""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"  <title>{escaped_title}</title>\n"
        f"{css_block}"
        "</head>\n"
        "<body>\n"
        '  <main class="markdown-body">\n'
        f"{body_html}\n"
        "  </main>\n"
        "</body>\n"
        "</html>"
    )


class MarkdownConverter:
    """Configurable Markdown to clean HTML converter."""

    def __init__(
        self,
        extensions: Optional[List[str]] = None,
        standalone: bool = True,
        include_css: bool = True,
        custom_css: Optional[str] = None,
        default_title: str = "Document",
    ):
        self.extensions = extensions if extensions is not None else list(DEFAULT_EXTENSIONS)
        self.standalone = standalone
        self.include_css = include_css
        self.custom_css = custom_css
        self.default_title = default_title
        self._md = markdown.Markdown(extensions=self.extensions)

    def convert(self, text: str, title: Optional[str] = None) -> str:
        """Convert a Markdown string to clean HTML.
        
        Args:
            text: Markdown input string.
            title: Optional override for the document <title>.
            
        Returns:
            Clean HTML string.
        """
        # Reset markdown internal parser state for fresh conversion
        self._md.reset()
        body_html = self._md.convert(text)

        if not self.standalone:
            return body_html

        doc_title = title or extract_title(text) or self.default_title

        # Determine CSS to embed
        css_content: Optional[str] = None
        if self.include_css:
            css_content = DEFAULT_CSS
            if self.custom_css:
                css_content = f"{DEFAULT_CSS}\n\n/* Custom CSS */\n{self.custom_css}"
        elif self.custom_css:
            css_content = self.custom_css

        return wrap_standalone_html(body_html, title=doc_title, css=css_content)

    def convert_file(
        self,
        input_path: str | Path,
        output_path: Optional[str | Path] = None,
        title: Optional[str] = None,
    ) -> str:
        """Convert a Markdown file to clean HTML.
        
        Args:
            input_path: Path to the input markdown file.
            output_path: Optional destination path. If provided, writes HTML there.
            title: Optional override for document title.
            
        Returns:
            The generated HTML string.
        """
        in_path = Path(input_path)
        if not in_path.exists():
            raise FileNotFoundError(f"Input file not found: {in_path}")

        text = in_path.read_text(encoding="utf-8")
        # Default title to file stem if not found in header
        file_title = title or extract_title(text) or in_path.stem.replace("_", " ").title()
        html_output = self.convert(text, title=file_title)

        if output_path is not None:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(html_output, encoding="utf-8")

        return html_output


def convert_markdown(
    text: str,
    standalone: bool = True,
    include_css: bool = True,
    custom_css: Optional[str] = None,
    title: Optional[str] = None,
    extensions: Optional[List[str]] = None,
) -> str:
    """Convenience helper to convert a Markdown string to HTML."""
    converter = MarkdownConverter(
        extensions=extensions,
        standalone=standalone,
        include_css=include_css,
        custom_css=custom_css,
    )
    return converter.convert(text, title=title)


def convert_file(
    input_path: str | Path,
    output_path: Optional[str | Path] = None,
    standalone: bool = True,
    include_css: bool = True,
    custom_css: Optional[str] = None,
    title: Optional[str] = None,
    extensions: Optional[List[str]] = None,
) -> str:
    """Convenience helper to convert a Markdown file to HTML."""
    converter = MarkdownConverter(
        extensions=extensions,
        standalone=standalone,
        include_css=include_css,
        custom_css=custom_css,
    )
    return converter.convert_file(input_path, output_path=output_path, title=title)

