"""Command-line interface for md2html."""

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from md2html.converter import MarkdownConverter

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="Convert Markdown files into clean, modern, and semantic HTML.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input markdown file path, or '-' to read from standard input (default: -).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Destination path for HTML output (default: write to stdout).",
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Custom title for standalone HTML document (defaults to first H1 or filename).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-s",
        "--standalone",
        dest="standalone",
        action="store_true",
        default=True,
        help="Generate a complete HTML5 document with head, meta tags, and styles (default).",
    )
    mode_group.add_argument(
        "-f",
        "--fragment",
        dest="standalone",
        action="store_false",
        help="Generate only the HTML body fragment without html/head/body envelope.",
    )
    parser.add_argument(
        "--no-css",
        action="store_true",
        help="Do not embed default CSS styling in standalone mode.",
    )
    parser.add_argument(
        "--css",
        help="Path to a custom CSS file to include in standalone output.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Read custom CSS file if specified
    custom_css_content: Optional[str] = None
    if args.css:
        css_path = Path(args.css)
        if not css_path.exists():
            sys.stderr.write(f"Error: CSS file not found: {args.css}\n")
            return 1
        try:
            custom_css_content = css_path.read_text(encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Error reading CSS file: {e}\n")
            return 1

    # Read markdown content
    title = args.title
    if args.input == "-":
        if sys.stdin.isatty():
            # If nothing piped in and running interactively, show help
            parser.print_help(sys.stderr)
            return 0
        try:
            md_content = sys.stdin.read()
        except Exception as e:
            sys.stderr.write(f"Error reading from stdin: {e}\n")
            return 1
    else:
        in_path = Path(args.input)
        if not in_path.exists():
            sys.stderr.write(f"Error: Input file not found: {args.input}\n")
            return 1
        try:
            md_content = in_path.read_text(encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Error reading input file: {e}\n")
            return 1

    converter = MarkdownConverter(
        standalone=args.standalone,
        include_css=not args.no_css,
        custom_css=custom_css_content,
    )

    try:
        html_output = converter.convert(md_content, title=title)
    except Exception as e:
        sys.stderr.write(f"Conversion error: {e}\n")
        return 1

    # Write output
    if args.output:
        out_path = Path(args.output)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(html_output, encoding="utf-8")
        except Exception as e:
            sys.stderr.write(f"Error writing to output file {args.output}: {e}\n")
            return 1
    else:
        sys.stdout.write(html_output)
        if not html_output.endswith("\n"):
            sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

