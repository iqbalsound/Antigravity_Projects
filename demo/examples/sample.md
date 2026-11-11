# Clean Markdown to HTML

This is a demonstration of converting **Markdown** into *clean, modern, and accessible* HTML.

## Key Features

- **Semantic HTML5**: Clean headings, sections, and tags.
- **Embedded Responsive CSS**: Looks great on both desktop and mobile.
- **Dark Mode Support**: Automatically switches based on system preferences.
- **Table & Code Block Support**: Pre-styled for optimal readability.

## Code Example

Here is a quick Python snippet demonstrating usage:

```python
from md2html import convert_file

# Convert a markdown file to standalone HTML
html = convert_file("document.md", output_path="document.html")
print("Conversion complete!")
```

## Feature Comparison

| Feature | Fragment Mode | Standalone Mode |
| :--- | :---: | :---: |
| HTML5 Doctype | No | Yes |
| Meta Viewport & Charset | No | Yes |
| Embedded CSS | No | Yes |
| Ready for Browser Viewing | No | Yes |
| Embeddable in Existing Pages | Yes | No |

## Blockquote

> "Simplicity is prerequisite for reliability."
> — *Edsger W. Dijkstra*

---

*Generated cleanly with `md2html`.*

