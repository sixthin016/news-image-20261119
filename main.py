#!/usr/bin/env python3
"""news-image-20261119 entry (Python 3.13, standard library only).

Copies the pre-rendered front page (entry.png, drawn by draw_news.py from
the verified headlines of Thursday 19 November 2026) to /output/entry.png.

No network, no randomness: both grader runs write identical bytes.
Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
