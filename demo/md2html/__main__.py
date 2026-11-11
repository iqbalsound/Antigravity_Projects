"""Support running package directly via `python3 -m md2html`."""

import sys
from md2html.cli import main

if __name__ == "__main__":
    sys.exit(main())

