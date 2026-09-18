#!/usr/bin/env python3
"""Axs dilinin calistiricisi.  Kullanim:  ton main.axs"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.realpath(__file__))))

# Windows konsolunda Turkce karakterler bozulmasin
if sys.platform == "win32":
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

from axslang.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
