"""
styles.py - CSS styles for clean HTML output.
Task done for PROMTOBIA
"""

from pygments.formatters import HtmlFormatter


def get_pygments_css() -> str:
    """Return CSS for Pygments syntax highlighting."""
    formatter = HtmlFormatter(style="friendly")
    return formatter.get_style_defs(".highlight")


def get_main_css() -> str:
    """Return the main responsive CSS stylesheet."""
    return """
/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:          #ffffff;
  --surface:     #f7f8fa;
  --border:      #e1e4e8;
  --text:        #24292f;
  --text-muted:  #57606a;
  --accent:      #0969da;
  --accent-dark: #0550ae;
  --code-bg:     #f6f8fa;
  --promtobia:   #6e40c9;
  --promtobia-bg:#f3eeff;
  --shadow:      0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.08);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg:          #0d1117;
    --surface:     #161b22;
    --border:      #30363d;
    --text:        #e6edf3;
    --text-muted:  #8b949e;
    --accent:      #58a6ff;
    --accent-dark: #79c0ff;
    --code-bg:     #161b22;
    --promtobia:   #c0a0ff;
    --promtobia-bg:#1f1535;
    --shadow:      0 1px 3px rgba(0,0,0,.4);
  }
}

html { font-size: 16px; scroll-behavior: smooth; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── PROMTOBIA Banner ──────────────────────────────────────── */
.promtobia-banner {
  background: linear-gradient(135deg, var(--promtobia) 0%, #9b6dff 100%);
  color: #ffffff;
  text-align: center;
  padding: 10px 24px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  box-shadow: var(--shadow);
}

.promtobia-banner span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.promtobia-banner .badge-icon { font-size: 1rem; }

/* ── Layout ────────────────────────────────────────────────── */
header.page-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 20px 24px;
}

header.page-header .title-row {
  max-width: 860px;
  margin: 0 auto;
}

header.page-header h1.doc-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text);
}

main {
  flex: 1;
  max-width: 860px;
  width: 100%;
  margin: 40px auto;
  padding: 0 24px 60px;
}

/* ── Typography ────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.6em;
  margin-bottom: 0.5em;
  font-weight: 700;
  line-height: 1.3;
  color: var(--text);
}

h1 { font-size: 2rem;   border-bottom: 2px solid var(--border); padding-bottom: 0.3em; }
h2 { font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25em; }
h3 { font-size: 1.25rem; }
h4 { font-size: 1.1rem; }
h5 { font-size: 1rem; }
h6 { font-size: 0.9rem; color: var(--text-muted); }

p { margin-bottom: 1em; }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; color: var(--accent-dark); }

strong { font-weight: 700; }
em     { font-style: italic; }

/* ── Lists ─────────────────────────────────────────────────── */
ul, ol { margin: 0.5em 0 1em 1.5em; }
li { margin-bottom: 0.3em; }
li > ul, li > ol { margin-top: 0.3em; }

/* Task lists */
input[type="checkbox"] { margin-right: 6px; accent-color: var(--promtobia); }

/* ── Blockquotes ───────────────────────────────────────────── */
blockquote {
  border-left: 4px solid var(--accent);
  margin: 1.2em 0;
  padding: 0.6em 1.2em;
  background: var(--surface);
  border-radius: 0 6px 6px 0;
  color: var(--text-muted);
}

blockquote p:last-child { margin-bottom: 0; }

/* ── Inline Code ───────────────────────────────────────────── */
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.875em;
  background: var(--code-bg);
  color: #cf222e;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  border: 1px solid var(--border);
}

@media (prefers-color-scheme: dark) {
  code { color: #ff7b72; }
}

/* ── Code Blocks (Pygments) ────────────────────────────────── */
.highlight {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  margin: 1.2em 0;
  box-shadow: var(--shadow);
}

.highlight pre {
  margin: 0;
  padding: 1em 1.2em;
  overflow-x: auto;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

pre code {
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: 1em;
}

/* ── Tables ────────────────────────────────────────────────── */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  font-size: 0.95rem;
  box-shadow: var(--shadow);
  border-radius: 8px;
  overflow: hidden;
}

thead { background: var(--surface); }

th, td {
  border: 1px solid var(--border);
  padding: 10px 16px;
  text-align: left;
}

th { font-weight: 700; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }

tbody tr:nth-child(even) { background: var(--surface); }
tbody tr:hover { background: var(--promtobia-bg); }

/* ── Horizontal Rule ───────────────────────────────────────── */
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }

/* ── Images ────────────────────────────────────────────────── */
img { max-width: 100%; height: auto; border-radius: 8px; box-shadow: var(--shadow); }

/* ── Footer ────────────────────────────────────────────────── */
footer.page-footer {
  background: var(--surface);
  border-top: 1px solid var(--border);
  text-align: center;
  padding: 20px 24px;
  font-size: 0.82rem;
  color: var(--text-muted);
}

footer.page-footer .promtobia-credit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--promtobia-bg);
  color: var(--promtobia);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.8rem;
  margin-top: 6px;
}

/* ── Responsive ────────────────────────────────────────────── */
@media (max-width: 600px) {
  main { padding: 0 14px 40px; }
  h1 { font-size: 1.5rem; }
  table { font-size: 0.85rem; }
  th, td { padding: 7px 10px; }
}
"""


def get_full_css() -> str:
    """Return combined main CSS + Pygments syntax highlighting CSS."""
    return get_main_css() + "\n/* Pygments Syntax Highlighting */\n" + get_pygments_css()
