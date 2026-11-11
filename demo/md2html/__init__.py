"""md2html - Convert Markdown files to clean, modern, and semantic HTML."""

from md2html.converter import (
    DEFAULT_EXTENSIONS,
    MarkdownConverter,
    convert_file,
    convert_markdown,
    extract_title,
    wrap_standalone_html,
)
from md2html.styles import DEFAULT_CSS

__version__ = "0.1.0"
__all__ = [
    "MarkdownConverter",
    "convert_markdown",
    "convert_file",
    "extract_title",
    "wrap_standalone_html",
    "DEFAULT_CSS",
    "DEFAULT_EXTENSIONS",
    "__version__",
]

