# md2html

A Python application and CLI that converts Markdown files to clean, modern, and semantic HTML.

## Features

- **Semantic HTML5**: Clean structure with proper doctype, meta viewport, title, and article wrapper.
- **Embedded Responsive CSS**: Minimalist typography, code highlighting styling, tables, blockquotes, and automatic dark mode support (`prefers-color-scheme`).
- **Flexible Modes**:
  - **Standalone** (default): Full HTML document ready to open in any web browser.
  - **Fragment** (`--fragment` / `-f`): Raw body HTML suitable for embedding inside existing layouts or web applications.
- **Title Extraction**: Automatically extracts the document title from the first `# Heading` (or falls back to the file name), with support for explicit title overrides.
- **Rich Markdown Extensions**: Tables, fenced code blocks, smart typography, and list enhancements.
- **Piping Support**: Accepts input from files or standard input (`stdin`), outputs to files or standard output (`stdout`).

## Installation

```bash
pip install .
```

Or install in development/editable mode:

```bash
pip install -e .
```

## CLI Usage

### Basic Conversion

Convert a markdown file to a standalone HTML file:

```bash
python3 -m md2html input.md -o output.html
```

Or using the installed command:

```bash
md2html input.md -o output.html
```

### Pipe via Stdin / Stdout

```bash
cat input.md | python3 -m md2html > output.html
```

### HTML Fragment (No HTML/Head/Body Wrapper)

```bash
python3 -m md2html input.md -f -o fragment.html
```

### Custom Document Title

```bash
python3 -m md2html input.md -t "My Custom Title" -o output.html
```

### Custom CSS

Inject your own stylesheet into the HTML document:

```bash
python3 -m md2html input.md --css custom.css -o output.html
```

Or disable embedded styling entirely:

```bash
python3 -m md2html input.md --no-css -o output.html
```

## Python API Usage

```python
from md2html import convert_file, convert_markdown

# Convert Markdown string to standalone HTML
html = convert_markdown("# Hello World\nThis is **clean** HTML.")

# Convert Markdown string to an HTML fragment
fragment = convert_markdown("Just *content*", standalone=False)

# Convert Markdown file to an output HTML file
convert_file("document.md", output_path="document.html")
```

## Running Unit Tests

Run the test suite with `pytest`:

```bash
pytest
```

