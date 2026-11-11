"""
cli.py - Command-line interface for md2html.
Task done for PROMTOBIA
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

from .converter import convert_directory, convert_file, PROMTOBIA_CREDIT


def _open_in_browser(path: Path) -> None:
    """Open an HTML file in the system default web browser."""
    uri = path.resolve().as_uri()
    try:
        webbrowser.open(uri)
    except Exception:
        # Fallback for headless environments
        for cmd in ("xdg-open", "open", "start"):
            try:
                subprocess.Popen([cmd, str(path.resolve())],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                break
            except FileNotFoundError:
                continue


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m md2html.cli",
        description=(
            "md2html — Convert Markdown files to clean HTML5 documents.\n"
            f"  {PROMTOBIA_CREDIT}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m md2html.cli README.md\n"
            "  python -m md2html.cli notes.md -o build/notes.html --open\n"
            "  python -m md2html.cli docs/ -o build/ --recursive\n"
            "  python -m md2html.cli page.md --title 'My Page' --theme dark"
        ),
    )

    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to a .md file or a directory containing .md files.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        default=None,
        help=(
            "Destination .html file or directory. "
            "Defaults to the same location as INPUT with a .html extension."
        ),
    )
    parser.add_argument(
        "-t", "--title",
        metavar="TITLE",
        default=None,
        help="Custom document <title>. Defaults to the first # heading.",
    )
    parser.add_argument(
        "--theme",
        choices=["light", "dark", "auto"],
        default="auto",
        help="Colour theme for the HTML output (default: auto).",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        default=False,
        help="When INPUT is a directory, also process subdirectories.",
    )
    parser.add_argument(
        "-b", "--open",
        action="store_true",
        dest="open_browser",
        default=False,
        help="Open the generated HTML file(s) in the default web browser.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns an integer exit code (0 = success)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)

    # ── Directory mode ──────────────────────────────────────────────────────
    if input_path.is_dir():
        try:
            output_files = convert_directory(
                input_path,
                output_dir=args.output,
                theme=args.theme,
                recursive=args.recursive,
            )
        except (NotADirectoryError, PermissionError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        if not output_files:
            print(
                f"Warning: No .md files found in '{input_path}'.",
                file=sys.stderr,
            )
            return 0

        for out_file in output_files:
            print(f"  ✔  {out_file}")
            if args.open_browser:
                _open_in_browser(out_file)

        print(f"\n{len(output_files)} file(s) converted. {PROMTOBIA_CREDIT}")
        return 0

    # ── Single-file mode ────────────────────────────────────────────────────
    if not input_path.exists():
        print(f"Error: File not found: '{input_path}'", file=sys.stderr)
        return 2

    if not input_path.is_file():
        print(f"Error: '{input_path}' is not a file or directory.", file=sys.stderr)
        return 2

    try:
        out_file = convert_file(
            input_path,
            output_path=args.output,
            title=args.title,
            theme=args.theme,
        )
    except (FileNotFoundError, ValueError, PermissionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"  ✔  {out_file}")
    print(f"\nConversion complete. {PROMTOBIA_CREDIT}")

    if args.open_browser:
        _open_in_browser(out_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
