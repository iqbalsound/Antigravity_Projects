"""
tests/test_cli.py — Tests for the md2html CLI (md2html.cli)
Task done for PROMTOBIA
"""

import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run the CLI via subprocess and return the CompletedProcess result."""
    return subprocess.run(
        [sys.executable, "-m", "md2html.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd or "/home/iqbal/Antigravity_Projects/Task-3A",
    )


class TestCLIBasic:
    def test_help_exits_zero(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout

    def test_version_flag(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_missing_file_nonzero_exit(self, tmp_path):
        result = run_cli(str(tmp_path / "nonexistent.md"))
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


class TestCLISingleFile:
    def test_converts_single_md_file(self, tmp_path):
        md_file = tmp_path / "hello.md"
        md_file.write_text("# Hello World\n\nThis is a test.", encoding="utf-8")

        result = run_cli(str(md_file))
        assert result.returncode == 0
        out_html = tmp_path / "hello.html"
        assert out_html.exists()

    def test_output_flag_custom_path(self, tmp_path):
        md_file = tmp_path / "input.md"
        md_file.write_text("# Input", encoding="utf-8")
        out_file = tmp_path / "custom_output.html"

        result = run_cli(str(md_file), "-o", str(out_file))
        assert result.returncode == 0
        assert out_file.exists()

    def test_title_flag_applied(self, tmp_path):
        md_file = tmp_path / "doc.md"
        md_file.write_text("# Original Heading", encoding="utf-8")

        result = run_cli(str(md_file), "--title", "My Custom Title")
        assert result.returncode == 0

        out_html = tmp_path / "doc.html"
        content = out_html.read_text(encoding="utf-8")
        assert "<title>My Custom Title</title>" in content

    def test_theme_dark_flag(self, tmp_path):
        md_file = tmp_path / "dark.md"
        md_file.write_text("# Dark Theme Doc", encoding="utf-8")

        result = run_cli(str(md_file), "--theme", "dark")
        assert result.returncode == 0

        out_html = tmp_path / "dark.html"
        content = out_html.read_text(encoding="utf-8")
        assert 'data-theme="dark"' in content

    def test_stdout_mentions_promtobia(self, tmp_path):
        md_file = tmp_path / "note.md"
        md_file.write_text("# Note", encoding="utf-8")

        result = run_cli(str(md_file))
        assert result.returncode == 0
        assert "PROMTOBIA" in result.stdout
