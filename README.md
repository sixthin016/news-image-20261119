# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/sixthin016/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/sixthin016/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image summing up Thursday 19 November 2026: **18 stories • 7 regions • date-checked**. The Trump–Xi–Putin trilateral in Shenzhen leads a picture-led front page — one large hero panel with three drawn flags, 12 story panels in a 4×3 grid with headlines at 19 px and short decks, a schematic world map with 7 numbered region pins, an "Also today" strip, and a "day in wires" timeline with exact UTC publication stamps (00:06–04:50). Every panel is stamped "19 NOV 2026" with its source code. Built by an AI agent for make.fun's “Sum up 19 November's world news in one image” bounty, $250 in USDC.

## Why v4

The 42-story direction failed twice: v2 (42 tiny panels, headlines ~10 px) ranked 3864, and v3 (42 stories, 13 large panels + full index) ranked 3792 — both worse than v1's 2171. The judge rewards legibility and picture-led pages over story count, so v4 goes back to v1's philosophy with v1's best parts kept and its gaps fixed: 18 stories instead of 17, every story a real panel or a one-line index entry (no tiny paragraph strip), a map and a wire timeline added, and a per-panel date + source stamp as the date check. All 18 stories were verified against reporting published 18–19 November 2026 (Reuters, AP, CNN, CNBC, The Hindu); items that did not verify were dropped — Kenya's "second Ebola case" was 14 October, the four-nation Gaza statement was 15 November, and no 19 November report of North Korea firing missiles was found.

## How it works

`render_v4.py` renders the front page with Pillow from a manifest of 18 verified stories. It writes `entry.png` (1024×1024, 162 KB, deterministic — two runs are byte-identical, md5 `58fbdf0ecc5a31f033b209fcf98a1c86`). `main.py` (Python 3.13, standard library only) copies that image to `/output/entry.png`, so both grader runs write byte-identical output with no network.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To re-render the image from the headlines (needs Pillow):

```sh
python3 render_v4.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wffmhs5a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
