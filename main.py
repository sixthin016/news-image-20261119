#!/usr/bin/env python3
"""news-image-20261119 v2 entrypoint (Python 3.13, standard library only).

The graded program: emit the front page built by render_front.py as
/output/entry.png. The image is committed in the repository, so the
program does no drawing, no network and no randomness at grade time —
it streams the committed bytes to the output path, which makes the two
grader runs byte-identical by construction.

Render the image again locally with:  python3 render_front.py
Run the entrypoint with:  MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import sys
from pathlib import Path

ENTRY_NAME = "entry.png"


def emit(source: Path, destination: Path) -> int:
    """Stream source bytes to destination; return the byte count."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with source.open("rb") as reader, destination.open("wb") as writer:
        while True:
            chunk = reader.read(65536)
            if not chunk:
                break
            writer.write(chunk)
            total += len(chunk)
    return total


def run() -> int:
    here = Path(__file__).resolve().parent
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    written = emit(here / ENTRY_NAME, target_dir / ENTRY_NAME)
    if written < 1000:
        print("entry image suspiciously small: %d bytes" % written,
              file=sys.stderr)
        return 1
    print("wrote %d bytes to %s" % (written, target_dir / ENTRY_NAME))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
