"""
tests/test_converter_file.py — Tests for convert_file() and convert_directory()
Task done for PROMTOBIA
"""

import pytest
from pathlib import Path

from md2html.converter import PROMTOBIA_CREDIT, convert_directory, convert_file


# ── convert_file() ─────────────────────────────────────────────────────────────

class TestConvertFile:
    def test_creates_html_file(self, tmp_path):
        md_file = tmp_path / "sample.md"
        md_file.write_text("# Hello\n\nThis is a test.", encoding="utf-8")

        out_file = convert_file(md_file)
        assert out_file.exists()
        assert out_file.suffix == ".html"

    def test_default_output_path_sibling(self, tmp_path):
        md_file = tmp_path / "notes.md"
        md_file.write_text("# Notes", encoding="utf-8")

        out_file = convert_file(md_file)
        assert out_file == tmp_path / "notes.html"

    def test_output_contains_promtobia_banner(self, tmp_path):
        md_file = tmp_path / "doc.md"
        md_file.write_text("# Title\nContent here.", encoding="utf-8")

        out_file = convert_file(md_file)
        content = out_file.read_text(encoding="utf-8")
        assert PROMTOBIA_CREDIT in content

    def test_custom_output_path(self, tmp_path):
        md_file = tmp_path / "input.md"
        md_file.write_text("# Input", encoding="utf-8")
        custom_out = tmp_path / "subdir" / "output.html"

        out_file = convert_file(md_file, output_path=custom_out)
        assert out_file == custom_out
        assert custom_out.exists()

    def test_missing_input_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            convert_file(tmp_path / "ghost.md")

    def test_title_extracted_from_filename_when_no_heading(self, tmp_path):
        md_file = tmp_path / "my-report.md"
        md_file.write_text("Just plain text.", encoding="utf-8")

        out_file = convert_file(md_file)
        content = out_file.read_text(encoding="utf-8")
        assert "<title>my-report</title>" in content

    def test_custom_title_applied(self, tmp_path):
        md_file = tmp_path / "file.md"
        md_file.write_text("# Ignored Heading", encoding="utf-8")

        out_file = convert_file(md_file, title="Override Title")
        content = out_file.read_text(encoding="utf-8")
        assert "<title>Override Title</title>" in content

    def test_theme_dark_applied_to_file(self, tmp_path):
        md_file = tmp_path / "dark.md"
        md_file.write_text("# Dark mode doc", encoding="utf-8")

        out_file = convert_file(md_file, theme="dark")
        content = out_file.read_text(encoding="utf-8")
        assert 'data-theme="dark"' in content


# ── convert_directory() ────────────────────────────────────────────────────────

class TestConvertDirectory:
    def test_converts_all_md_files(self, tmp_path):
        (tmp_path / "a.md").write_text("# A", encoding="utf-8")
        (tmp_path / "b.md").write_text("# B", encoding="utf-8")
        (tmp_path / "c.md").write_text("# C", encoding="utf-8")

        results = convert_directory(tmp_path)
        assert len(results) == 3
        for path in results:
            assert path.suffix == ".html"
            assert path.exists()

    def test_empty_directory_returns_empty_list(self, tmp_path):
        results = convert_directory(tmp_path)
        assert results == []

    def test_non_md_files_ignored(self, tmp_path):
        (tmp_path / "readme.md").write_text("# Readme", encoding="utf-8")
        (tmp_path / "data.txt").write_text("plain text", encoding="utf-8")
        (tmp_path / "notes.rst").write_text("reStructuredText", encoding="utf-8")

        results = convert_directory(tmp_path)
        assert len(results) == 1

    def test_recursive_flag_includes_subdirs(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (tmp_path / "root.md").write_text("# Root", encoding="utf-8")
        (subdir / "nested.md").write_text("# Nested", encoding="utf-8")

        results = convert_directory(tmp_path, recursive=True)
        assert len(results) == 2

    def test_non_recursive_skips_subdirs(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (tmp_path / "root.md").write_text("# Root", encoding="utf-8")
        (subdir / "nested.md").write_text("# Nested", encoding="utf-8")

        results = convert_directory(tmp_path, recursive=False)
        assert len(results) == 1

    def test_custom_output_directory(self, tmp_path):
        src = tmp_path / "src"
        out = tmp_path / "out"
        src.mkdir()
        (src / "page.md").write_text("# Page", encoding="utf-8")

        results = convert_directory(src, output_dir=out)
        assert len(results) == 1
        assert results[0].parent == out

    def test_not_a_directory_raises(self, tmp_path):
        file_path = tmp_path / "file.md"
        file_path.write_text("# File", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            convert_directory(file_path)

    def test_all_outputs_contain_promtobia(self, tmp_path):
        (tmp_path / "x.md").write_text("# X", encoding="utf-8")
        (tmp_path / "y.md").write_text("# Y", encoding="utf-8")

        results = convert_directory(tmp_path)
        for path in results:
            content = path.read_text(encoding="utf-8")
            assert PROMTOBIA_CREDIT in content
