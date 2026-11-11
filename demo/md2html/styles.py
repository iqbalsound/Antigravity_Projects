"""Default clean CSS styling for standalone HTML documents."""

DEFAULT_CSS = """
:root {
  --bg-color: #ffffff;
  --text-color: #24292f;
  --heading-color: #1f2328;
  --link-color: #0969da;
  --link-hover-color: #1a7f37;
  --border-color: #d0d7de;
  --code-bg: #f6f8fa;
  --code-border: #e1e4e8;
  --quote-color: #57606a;
  --table-alt-bg: #f6f8fa;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #0d1117;
    --text-color: #c9d1d9;
    --heading-color: #f0f6fc;
    --link-color: #58a6ff;
    --link-hover-color: #3fb950;
    --border-color: #30363d;
    --code-bg: #161b22;
    --code-border: #30363d;
    --quote-color: #8b949e;
    --table-alt-bg: #161b22;
  }
}

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
  font-size: 16px;
  line-height: 1.65;
  color: var(--text-color);
  background-color: var(--bg-color);
  margin: 0;
  padding: 2.5rem 1.5rem;
}

.markdown-body {
  max-width: 840px;
  margin: 0 auto;
  word-wrap: break-word;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--heading-color);
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
}

h1 {
  font-size: 2rem;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-color);
}

h2 {
  font-size: 1.5rem;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-color);
}

h3 { font-size: 1.25rem; }
h4 { font-size: 1rem; }
h5 { font-size: 0.875rem; }
h6 { font-size: 0.85rem; color: var(--quote-color); }

p {
  margin-top: 0;
  margin-bottom: 1rem;
}

a {
  color: var(--link-color);
  text-decoration: none;
}

a:hover {
  color: var(--link-hover-color);
  text-decoration: underline;
}

strong {
  font-weight: 600;
}

hr {
  height: 0.25em;
  padding: 0;
  margin: 2rem 0;
  background-color: var(--border-color);
  border: 0;
}

blockquote {
  margin: 0 0 1rem 0;
  padding: 0 1rem;
  color: var(--quote-color);
  border-left: 0.25rem solid var(--border-color);
}

ul, ol {
  padding-left: 2rem;
  margin-top: 0;
  margin-bottom: 1rem;
}

li + li {
  margin-top: 0.25rem;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1rem;
  display: block;
  overflow-x: auto;
}

th, td {
  padding: 8px 14px;
  border: 1px solid var(--border-color);
  text-align: left;
}

th {
  background-color: var(--code-bg);
  font-weight: 600;
}

tr:nth-child(even) td {
  background-color: var(--table-alt-bg);
}

code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 85%;
  padding: 0.2em 0.4em;
  margin: 0;
  background-color: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 4px;
}

pre {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 85%;
  line-height: 1.45;
  padding: 1rem;
  overflow: auto;
  border-radius: 6px;
  background-color: var(--code-bg);
  border: 1px solid var(--code-border);
  margin-top: 0;
  margin-bottom: 1rem;
}

pre code {
  padding: 0;
  margin: 0;
  background: transparent;
  border: none;
  font-size: 100%;
  word-break: normal;
  white-space: pre;
}

img {
  max-width: 100%;
  height: auto;
  border-style: none;
}
""".strip()

