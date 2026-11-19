#!/usr/bin/env python3
"""Publish the committed front page for news-image-20261119 (v6).

The picture itself lives in the repository as entry.png — it was drawn
offline by render_v6.py, so grading needs no network access, no fonts
at run time and no random numbers. All this entry point has to do is
place an exact copy of those bytes where the grader looks for them,
and refuse to report success if the copy came out implausibly tiny.

Usage:
    MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
"""

import os
import shutil
import sys
from pathlib import Path

IMAGE = "entry.png"
FALLBACK_DIR = "/output"
MIN_PLAUSIBLE_BYTES = 1000


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _destination() -> Path:
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    return Path(chosen) / IMAGE


def _publish() -> int:
    src = _repo_root() / IMAGE
    dst = _destination()
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open("rb") as incoming, dst.open("wb") as outgoing:
        shutil.copyfileobj(incoming, outgoing, length=1 << 16)
    size = dst.stat().st_size
    if size < MIN_PLAUSIBLE_BYTES:
        print(f"refusing to claim success: {dst} is only {size} bytes",
              file=sys.stderr)
        return 1
    print(f"copied {IMAGE} ({size} bytes) to {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(_publish())
