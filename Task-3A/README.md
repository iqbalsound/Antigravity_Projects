# md2html

> **Task done for PROMTOBIA** — A Python app that converts Markdown files to clean, styled HTML5 documents.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/tests-pytest-green)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## Features

- 📄 Converts `.md` files to standalone, styled HTML5 documents
- ⚡ **PROMTOBIA branding** — top banner + footer badge on every generated page
- 🎨 Clean, modern responsive CSS with automatic dark/light/auto theme
- 🖌️ Syntax-highlighted code blocks (via Pygments `friendly` theme)
- 📊 GitHub-flavored tables, task lists, footnotes, definition lists
- 🌐 CLI tool with batch directory conversion and browser auto-open (`--open`)
- ✅ Full `pytest` test suite (39+ tests)

---

## Project Structure

```
Task-3A/
├── md2html/
│   ├── __init__.py        # Package metadata
│   ├── converter.py       # Core conversion engine
│   ├── styles.py          # CSS + Pygments theme
│   └── cli.py             # Command-line interface
├── tests/
│   ├── test_converter.py       # 25 unit tests for convert_text()
│   ├── test_converter_file.py  # 8 tests for convert_file/directory()
│   └── test_cli.py             # 6 CLI integration tests
├── examples/
│   ├── showcase.md        # Rich demo Markdown file
│   └── showcase.html      # Pre-generated HTML output
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# Clone or navigate to the project directory
cd Task-3A

# Install dependencies (all already available system-wide)
pip install -r requirements.txt
```

**Dependencies:** `Markdown >= 3.4`, `Pygments >= 2.14`, `pytest >= 7.0`

---

## Usage

### Python API

```python
from md2html.converter import convert_text, convert_file, convert_directory

# Convert a string
html = convert_text("# Hello World\n\nThis is **markdown**.")

# Convert a file
output_path = convert_file("notes.md")                    # → notes.html
output_path = convert_file("notes.md", theme="dark")      # dark theme
output_path = convert_file("notes.md", title="My Notes")  # custom title

# Convert all .md files in a directory
paths = convert_directory("docs/", output_dir="build/", recursive=True)
```

### Command-Line Interface

```bash
# Single file
python -m md2html.cli README.md

# Custom output path
python -m md2html.cli notes.md -o build/notes.html

# Open in browser immediately
python -m md2html.cli notes.md --open

# Custom title and dark theme
python -m md2html.cli page.md --title "My Page" --theme dark

# Convert entire directory (recursively)
python -m md2html.cli docs/ -o build/ --recursive

# Help
python -m md2html.cli --help
```

---

## Running Tests

```bash
# Run all tests with verbose output
pytest -v

# Run with short traceback
pytest -v --tb=short

# Run a specific test file
pytest tests/test_converter.py -v

# Run a specific test class
pytest tests/test_converter.py::TestPromtobiaBranding -v
```

---

## PROMTOBIA Branding

Every generated HTML file includes the **"Task done for PROMTOBIA"** attribution in three places:

1. **Top banner** — purple gradient bar at the very top of every page
2. **`<meta name="generator">`** — machine-readable attribution in the `<head>`
3. **Footer badge** — pill-shaped credit badge at the bottom of every page

---

## Themes

| Value | Description |
|-------|-------------|
| `auto` | Follows system dark/light mode preference (default) |
| `light` | Force light mode |
| `dark` | Force dark mode |

---

*md2html · Task done for PROMTOBIA ⚡*
