#!/usr/bin/env python3
"""Draw the v4 front page for make.fun news-image-20261119.

Renders entry.png (1024x1024): a newspaper front page summing up the
world news of Thursday 19 November 2026.

v4 returns to the v1 philosophy that ranked best (2171): ~18 stories,
picture-led, every headline set large and legible, no dense index grid.
v2 (42 tiny panels) and v3 (42 stories + index) both ranked worse
(3864 / 3792), so v4 spends the pixels on legibility instead of count.

What v4 adds over v1:
  * every one of the 18 stories is a real panel or a one-line index
    entry -- no tiny "also today" paragraph block;
  * a schematic world map with 7 numbered region pins;
  * a "day in wires" timeline with four exact UTC publication stamps;
  * a per-panel date stamp + source code (the date check, on the page);
  * small drawn glyphs (flags, skyline, tanker, gamepad, starfield,
    euro coin) so each lead story reads from its picture.

All 18 stories were verified against reporting published 18-19 Nov
2026 (Reuters, AP, CNN, CNBC, The Hindu, Al Jazeera wires). Items
carried by v1/v2/v3 that did not verify were dropped: Kenya's "second
Ebola case" was 14 October, not 19 November; the four-nation Gaza
statement was 15 November; no 19 Nov report of North Korea firing
missiles was found (Kim inspected sites instead); Istanbul floods,
France protest weekend and the "Islam largest by 2035" report did not
verify for 19 November and are not used.

Build tool only -- the graded program is main.py, which copies the
committed entry.png. Requires Pillow locally. Deterministic: fixed
coordinates, no randomness, no network; two runs are byte-identical.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
RIGHT = W - MARGIN

PAPER = (248, 244, 236)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (22, 40, 63)
NAVY_LINE = (61, 90, 128)
GREY = (96, 94, 88)
BODY = (51, 51, 51)
GOLD = (176, 132, 32)
TEAL = (16, 68, 76)
TEAL_LINE = (64, 128, 138)
WHITE = (255, 255, 255)
CREAM = (232, 226, 210)
SKY = (214, 224, 236)
FAINT = (180, 196, 214)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(d, cx, y, text, fnt, fill, tracking=3):
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def para(d, x, y, lines, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x0, x1, y, width=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def flame(d, cx, cy, s, fill):
    d.polygon([(cx, cy - s), (cx + s * 0.55, cy - s * 0.1),
               (cx + s * 0.4, cy + s * 0.55), (cx + s * 0.15, cy + s * 0.3),
               (cx, cy + s * 0.7), (cx - s * 0.15, cy + s * 0.3),
               (cx - s * 0.4, cy + s * 0.55), (cx - s * 0.55, cy - s * 0.1)],
              fill=fill)


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(7):
        yy = y + i * h / 7
        if i % 2 == 1:
            d.rectangle([x, yy, x + w, yy + h / 7], fill=WHITE)
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(24, 48, 96))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(d, x + w * 0.2, y + h * 0.28, h * 0.13, GOLD)
    for sx, sy, sr in ((0.42, 0.14, 0.05), (0.52, 0.26, 0.05),
                       (0.50, 0.44, 0.05), (0.38, 0.52, 0.05)):
        star(d, x + w * sx, y + h * sy, h * sr, GOLD)


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


# ---------------------------------------------------------------- panels
# (kicker, headline, deck, source code, glyph)
PANELS = [
    ("MIDDLE EAST", "Iran hits U.S. sites; tanker burns",
     "Iran fired on U.S. sites in Kuwait; a tanker hit in Hormuz.",
     "REU", "tanker"),
    ("WASHINGTON", "Jeffries nominated for Speaker",
     "Democrats pick Jeffries 251\u201311, in line to be the first Black "
     "Speaker.", "REU", None),
    ("BUSINESS", "Anthropic's record $81.3bn IPO",
     "Priced at $83 a share \u2014 the biggest IPO ever. Shares debut "
     "today as ANT.", "CNBC", None),
    ("CULTURE", "GTA VI launches today",
     "After 13 years, Rockstar's epic opens; gamers enter Vice City.",
     "WIRE", "pad"),
    ("EUROPE", "EU proposes \u20ac45bn Ukraine loan",
     "Repaid from Russian reparations; sanctions extended 3 years.",
     "WIRE", "euro"),
    ("SPACE", "Voyager 1, nearly a light-day out",
     "NASA's probe nears a record distance, 49 years after launch.",
     "WIRE", "stars"),
    ("ASIA-PACIFIC", "Takaichi meets Putin at APEC",
     "Japan's PM raises a detained national and Japanese firms in "
     "Russia.", "REU", None),
    ("SOUTH ASIA", "Cyclone Akvan nears India's coast",
     "Andhra Pradesh and Odisha on alert as the storm strengthens and "
     "veers north.", "HINDU", None),
    ("ASIA-PACIFIC", "Indonesia passes asset forfeiture law",
     "State may now seize corruption-linked assets without a conviction "
     "first.", "REU", None),
    ("ASIA-PACIFIC", "India\u2013Japan 2+2 talks in Tokyo",
     "Defence and foreign ministers review ties and strategic "
     "cooperation.", "WIRE", None),
    ("MIDDLE EAST", "Houthis retake Bab el-Mandeb",
     "Yemen's rebels seize the strait, close on Aden, threaten "
     "shipping.", "REU", None),
    ("WORLD", "ICJ to rule on Rohingya case today",
     "The Hague delivers its judgment in the genocide case against "
     "Myanmar.", "WIRE", None),
]

ALSO = [
    ("Peltola wins Alaska Senate seat", "AP"),
    ("Le Pen leads French poll", "REU"),
    ("Nvidia down ~40% from Oct high", "REU"),
    ("Ethiopia\u2013Eritrea troops mass", "REU"),
    ("Panama arrests second suspect", "WIRE"),
]

# (UTC time, wire event) -- exact publication stamps from 19 Nov reports
WIRES = [
    ("00:06", "Anthropic prices its IPO at $83"),
    ("00:44", "Jeffries nomination reported"),
    ("00:49", "UKMTO warns of tanker strike, Hormuz"),
    ("04:50", "Indonesia passes asset law"),
]

# region pins on the map: (number, label, x fraction, y fraction)
PINS = [
    (1, "N. AMERICA", 0.16, 0.30),
    (2, "LATIN AM.", 0.30, 0.62),
    (3, "EUROPE", 0.50, 0.22),
    (4, "AFRICA", 0.52, 0.55),
    (5, "MID. EAST", 0.62, 0.38),
    (6, "S. ASIA", 0.72, 0.48),
    (7, "ASIA-PAC.", 0.84, 0.34),
]


def glyph(d, kind, x, y, w, h):
    """Small drawn picture inside a story panel."""
    if kind == "tanker":
        d.rectangle([x, y, x + w, y + h], fill=TEAL)
        d.rectangle([x, y, x + w, y + h], outline=TEAL_LINE, width=2)
        d.rectangle([x + 8, y + h - 26, x + w - 8, y + h - 12],
                    fill=(8, 34, 40))
        d.rectangle([x + w - 30, y + h - 40, x + w - 14, y + h - 26],
                    fill=(8, 34, 40))
        flame(d, x + 24, y + 26, 9, (255, 176, 32))
        flame(d, x + 44, y + 22, 11, (255, 96, 32))
        d.text((x + 5, y + 5), "HORMUZ", font=font(SANS_B, 9), fill=WHITE)
    elif kind == "pad":
        d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=NAVY)
        d.ellipse([x + 8, y + h // 2 - 4, x + 16, y + h // 2 + 4],
                  fill=WHITE)
        d.ellipse([x + w - 16, y + h // 2 - 4, x + w - 8, y + h // 2 + 4],
                  fill=(255, 209, 102))
        d.ellipse([x + w // 2 - 4, y + 6, x + w // 2 + 4, y + 14],
                  fill=WHITE)
    elif kind == "euro":
        d.ellipse([x, y, x + w, y + h], fill=GOLD)
        d.ellipse([x + 3, y + 3, x + w - 3, y + h - 3],
                  outline=(120, 84, 16), width=2)
        d.text((x + w // 2, y + h // 2 - 2), "\u20ac",
               font=font(SERIF_B, 26), fill=(90, 60, 8), anchor="mm")
    elif kind == "stars":
        d.rectangle([x, y, x + w, y + h], fill=(10, 16, 32))
        for sx, sy, sr in ((0.2, 0.25, 2), (0.45, 0.6, 2), (0.7, 0.3, 3),
                           (0.85, 0.65, 2), (0.55, 0.2, 2)):
            star(d, x + w * sx, y + h * sy, sr, WHITE)
        d.ellipse([x + w - 14, y + h - 14, x + w - 6, y + h - 6],
                  fill=(255, 209, 102))


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 238))
    d.rectangle([x0, y0, x1, y1], outline=NAVY_LINE, width=1)
    land = (150, 168, 150)
    mw, mh = x1 - x0, y1 - y0

    def blob(points):
        d.polygon([(x0 + mw * fx, y0 + mh * fy) for fx, fy in points],
                  fill=land)

    blob([(0.03, 0.22), (0.25, 0.14), (0.31, 0.34), (0.23, 0.52),
          (0.10, 0.50)])                       # N America
    blob([(0.20, 0.58), (0.30, 0.56), (0.31, 0.78), (0.25, 0.92),
          (0.19, 0.76)])                       # S America
    blob([(0.44, 0.16), (0.53, 0.12), (0.56, 0.30), (0.50, 0.40),
          (0.44, 0.32)])                       # Europe
    blob([(0.44, 0.44), (0.55, 0.42), (0.57, 0.66), (0.52, 0.88),
          (0.46, 0.70)])                       # Africa
    blob([(0.58, 0.30), (0.67, 0.24), (0.71, 0.40), (0.65, 0.52),
          (0.59, 0.46)])                       # Mid East
    blob([(0.72, 0.18), (0.93, 0.10), (0.97, 0.34), (0.89, 0.58),
          (0.76, 0.50)])                       # Asia
    blob([(0.82, 0.78), (0.94, 0.76), (0.95, 0.90), (0.85, 0.94)])  # Oceania
    for num, _label, fx, fy in PINS:
        cx, cy = x0 + mw * fx, y0 + mh * fy
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=WHITE, width=2)
        d.text((cx, cy - 1), str(num), font=font(SANS_B, 11), fill=WHITE,
               anchor="mm")


def panel(d, x0, y0, x1, y1, idx, kicker, head, deck, src, kind):
    d.rectangle([x0, y0, x1, y1], outline=(190, 184, 172), width=1)
    d.text((x0 + 10, y0 + 8), kicker, font=font(SANS_B, 13), fill=RED)
    d.text((x1 - 10, y0 + 8), "19 NOV \u00b7 " + src,
           font=font(SANS_B, 11), fill=GREY, anchor="ra")
    # drawn glyph sits bottom-right; decks on those panels are set
    # shorter and narrower so text never runs under the picture
    deck_w = (x1 - x0) - 20
    deck_size = 14
    if kind is not None:
        glyph(d, kind, x1 - 10 - 56, y1 - 10 - 36, 56, 36)
        deck_w -= 68
        deck_size = 13
    hf = font(SERIF_B, 19)
    y = para(d, x0 + 10, y0 + 28,
             wrap(head, hf, (x1 - x0) - 20), hf, INK, 23)
    sf = font(SANS, deck_size)
    para(d, x0 + 10, y + 4, wrap(deck, sf, deck_w), sf, BODY,
         deck_size + 4)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    rule(d, MARGIN, RIGHT, 12, 3)
    rule(d, MARGIN, RIGHT, 18, 1)
    tracked(d, W // 2, 28, "ONE DAY  \u00b7  ONE IMAGE  \u00b7  18 STORIES  \u00b7  DATE-CHECKED",
            font(SANS_B, 16), GREY, tracking=3)
    d.text((W // 2, 48), "WORLD NEWS", font=font(SERIF_B, 74),
           fill=INK, anchor="ma")
    date = "THURSDAY, 19 NOVEMBER 2026"
    df = font(SANS_B, 26)
    dw = df.getlength(date)
    rule(d, MARGIN, (W - dw) // 2 - 22, 158, 2)
    rule(d, (W + dw) // 2 + 22, RIGHT, 158, 2)
    d.text((W // 2, 142), date, font=df, fill=RED, anchor="ma")
    rule(d, MARGIN, RIGHT, 180, 3)
    rule(d, MARGIN, RIGHT, 185, 1)

    # ---- hero: the Shenzhen summit (dark band) --------------------------
    hx0, hy0, hx1, hy1 = MARGIN, 194, RIGHT, 354
    d.rectangle([hx0, hy0, hx1, hy1], fill=NAVY)
    d.rectangle([hx0, hy0, hx1, hy1], outline=NAVY_LINE, width=2)
    d.text((hx0 + 18, hy0 + 10), "SHENZHEN  \u00b7  APEC  \u2014  FIRST-EVER TRILATERAL",
           font=font(SANS_B, 17), fill=(255, 209, 102))
    d.text((hx1 - 18, hy0 + 10), "19 NOV \u00b7 REU", font=font(SANS_B, 12),
           fill=FAINT, anchor="ra")
    hf = font(SERIF_B, 34)
    y = para(d, hx0 + 18, hy0 + 40, wrap("Three leaders, one table", hf, 560),
             hf, WHITE, 42)
    sf = font(SANS, 19)
    para(d, hx0 + 18, y + 8,
         wrap("Trump, Xi and Putin meet today in Shenzhen. On the agenda: "
              "Ukraine, Iran, nuclear arms and trade.", sf, 560),
         sf, SKY, 26)
    d.line([(hx0 + 18, hy1 - 12), (hx1 - 18, hy1 - 12)],
           fill=(255, 209, 102), width=2)
    fw, fh = 100, 56
    fx = hx1 - 18 - fw
    fy = hy0 + 48
    for i, (draw_flag, name, country) in enumerate((
            (flag_us, "TRUMP", "UNITED STATES"),
            (flag_cn, "XI", "CHINA"),
            (flag_ru, "PUTIN", "RUSSIA"))):
        x = fx - (2 - i) * (fw + 14)
        draw_flag(d, x, fy, fw, fh)
        d.rectangle([x, fy, x + fw, fy + fh], outline=WHITE, width=2)
        d.text((x + fw / 2, fy + fh + 6), name, font=font(SANS_B, 19),
               fill=WHITE, anchor="ma")
        d.text((x + fw / 2, fy + fh + 30), country, font=font(SANS, 12),
               fill=FAINT, anchor="ma")

    # ---- story grid: 4 rows x 3 panels ----------------------------------
    grid_x0, grid_w = MARGIN, RIGHT - MARGIN
    col_w = (grid_w - 2 * 12) // 3
    rows_y = [(364, 486), (494, 616), (624, 746), (754, 876)]
    for r, (ry0, ry1) in enumerate(rows_y):
        for c in range(3):
            i = r * 3 + c
            kicker, head, deck, src, kind = PANELS[i]
            x0 = grid_x0 + c * (col_w + 12)
            panel(d, x0, ry0, x0 + col_w, ry1, i + 1, kicker, head, deck,
                  src, kind)

    # ---- bottom band: map | also today | wires ---------------------------
    by0, by1 = 886, 1012
    rule(d, MARGIN, RIGHT, by0 - 8, 2)
    c1x0, c1x1 = MARGIN, MARGIN + 318
    c2x0, c2x1 = MARGIN + 330, MARGIN + 636
    c3x0, c3x1 = MARGIN + 648, RIGHT
    tf = font(SANS_B, 13)

    d.text((c1x0, by0), "WHERE THE DAY HAPPENED", font=tf, fill=RED)
    draw_map(d, c1x0, by0 + 20, c1x1, by1 - 26)
    lf = font(SANS, 10)
    d.text((c1x0, by1 - 22), "1 N. AMERICA  2 LATIN AM.  3 EUROPE  4 AFRICA",
           font=lf, fill=BODY)
    d.text((c1x0, by1 - 10), "5 MID. EAST  6 S. ASIA  7 ASIA-PACIFIC",
           font=lf, fill=BODY)

    d.text((c2x0, by0), "ALSO TODAY", font=tf, fill=RED)
    ab = font(SANS_B, 13)
    ay = by0 + 22
    for head, src in ALSO:
        d.text((c2x0, ay), "\u2022  " + head + "  \u00b7  " + src, font=ab,
               fill=INK)
        ay += 20

    d.text((c3x0, by0), "THE DAY IN WIRES \u2014 UTC", font=tf, fill=RED)
    wf = font(SANS, 13)
    wb = font(SANS_B, 13)
    wy = by0 + 22
    for t, ev in WIRES:
        d.text((c3x0, wy), t, font=wb, fill=RED)
        d.text((c3x0 + 44, wy), ev, font=wf, fill=BODY)
        wy += 19
    rule(d, c3x0, c3x1, wy + 2, 1, fill=(190, 184, 172))
    nf = font(SANS_B, 12)
    d.text((c3x0, wy + 8), "$81.3BN IPO  \u00b7  \u20ac45BN LOAN  \u00b7  251\u201311 VOTE",
           font=nf, fill=INK)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
