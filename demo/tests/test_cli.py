"""Unit tests for the md2html CLI."""

import io
from pathlib import Path
import pytest
from md2html.cli import main


def test_cli_file_to_file(tmp_path, sample_markdown):
    in_file = tmp_path / "input.md"
    out_file = tmp_path / "output.html"
    in_file.write_text(sample_markdown, encoding="utf-8")

    exit_code = main([str(in_file), "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<title>Welcome to Demo</title>" in content


def test_cli_file_to_stdout(tmp_path, sample_markdown, capsys):
    in_file = tmp_path / "input.md"
    in_file.write_text(sample_markdown, encoding="utf-8")

    exit_code = main([str(in_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<!DOCTYPE html>" in captured.out
    assert "<strong>bold</strong>" in captured.out


def test_cli_stdin_to_stdout(monkeypatch, capsys):
    test_input = "# Heading from Stdin\n\nContent here."
    monkeypatch.setattr("sys.stdin", io.StringIO(test_input))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    exit_code = main(["-"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<title>Heading from Stdin</title>" in captured.out
    assert "<p>Content here.</p>" in captured.out


def test_cli_fragment_mode(tmp_path, capsys):
    in_file = tmp_path / "input.md"
    in_file.write_text("Hello **fragment**", encoding="utf-8")

    exit_code = main([str(in_file), "--fragment"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<!DOCTYPE html>" not in captured.out
    assert "<p>Hello <strong>fragment</strong></p>" in captured.out


def test_cli_custom_title(tmp_path, capsys):
    in_file = tmp_path / "input.md"
    in_file.write_text("# Original Title\nText", encoding="utf-8")

    exit_code = main([str(in_file), "--title", "Overridden Title"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<title>Overridden Title</title>" in captured.out


def test_cli_no_css(tmp_path, capsys):
    in_file = tmp_path / "input.md"
    in_file.write_text("# Doc\nText", encoding="utf-8")

    exit_code = main([str(in_file), "--no-css"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "<style>" not in captured.out


def test_cli_custom_css(tmp_path, capsys):
    in_file = tmp_path / "input.md"
    css_file = tmp_path / "custom.css"
    in_file.write_text("# Doc\nText", encoding="utf-8")
    css_file.write_text(".custom-rule { font-size: 20px; }", encoding="utf-8")

    exit_code = main([str(in_file), "--css", str(css_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert ".custom-rule { font-size: 20px; }" in captured.out


def test_cli_missing_input_file(tmp_path, capsys):
    missing_file = tmp_path / "nonexistent.md"
    exit_code = main([str(missing_file)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Input file not found" in captured.err


def test_cli_missing_css_file(tmp_path, capsys):
    in_file = tmp_path / "input.md"
    in_file.write_text("# Doc\nText", encoding="utf-8")
    missing_css = tmp_path / "missing.css"

    exit_code = main([str(in_file), "--css", str(missing_css)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: CSS file not found" in captured.err


def test_cli_interactive_tty_shows_help(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    exit_code = main(["-"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage: md2html" in captured.err

