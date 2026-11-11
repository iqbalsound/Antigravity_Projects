"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_markdown() -> str:
    return """# Welcome to Demo

This is a test paragraph with **bold** text and *italic* text.

## Features

- Fast
- Clean
- Semantic

```python
def hello():
    return "world"
```

| Col 1 | Col 2 |
|---|---|
| A | B |

> A wise quote
"""

