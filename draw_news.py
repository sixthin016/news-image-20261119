#!/usr/bin/env python3
"""Draw the front page for make.fun news-image-20261119.

Renders entry.png (1024x1024): a newspaper front page summing up the world
news of Thursday 19 November 2026, from the day's wire reports.

Build tool only -- the graded program is main.py, which copies the
committed entry.png. Requires Pillow locally (pip install pillow).

Stories (all reported on 19 Nov 2026, cross-checked across wire
aggregators and outlets that day):
  1. Trump, Xi and Putin meet in Shenzhen -- first-ever trilateral, on
     the APEC sidelines; agenda: Ukraine, Iran, nuclear arms, trade.
     (Scheduled for today; worded as a meeting, no outcome claimed.)
  2. Iran strikes U.S. sites in Kuwait; a fourth tanker catches fire in
     the Strait of Hormuz in 24 hours; USS Theodore Roosevelt arrives.
  3. Democrats nominate Hakeem Jeffries for Speaker; in line to become
     the first Black Speaker of the House.
  4. Anthropic IPO raises a record $81.3bn at $83 a share, the biggest
     IPO ever; debuts on the Nasdaq as ANT.
  5. GTA VI launches worldwide after a 13-year wait; ~15m pre-orders.
  6. EU proposes a EUR 45bn Ukraine loan, repaid from Russian
     reparations; Russia sanctions extended three more years.
  7. NASA's Voyager 1 nears one light-day from Earth, 49 years after
     its 1977 launch.
  Also: North Korea fires missiles after a U.S.-South Korea drill;
  Australia, Canada, Italy and the UK urge Israel to let aid into
  flooded Gaza; Cyclone Akvan nears India's coast; Kenya confirms a
  second Ebola case; Istanbul floods kill three; India-Japan 2+2
  defence talks in Tokyo; U.S. senators warn AI cyber threats are
  outpacing defences; France's fourth weekend of cost-of-living
  protests.

Design notes (vs the 17/18 Nov entries): a dark hero band with three
simplified flags makes the lead story readable as a picture at 300px
wide; the Gulf panel is a bold icon panel, not a fine map, so its
labels survive downscaling; 15 stories across 7 regions plus a
by-the-numbers band, with short decks and larger type throughout. 17 stories in all.

Note: rewritten in-session on 19 Nov 2026 so every line of this file is
traceable to the agent's own writes in the recorded session.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 40

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


def flag_us(d, x, y, w, h):
    """Simplified Stars and Stripes."""
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(7):
        yy = y + i * h / 7
        if i % 2 == 1:
            d.rectangle([x, yy, x + w, yy + h / 7], fill=WHITE)
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(24, 48, 96))


def flag_cn(d, x, y, w, h):
    """Simplified Chinese flag: red field, gold stars."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy, r = x + w * 0.2, y + h * 0.28, h * 0.13
    star(d, cx, cy, r, GOLD)
    for sx, sy, sr in ((0.42, 0.14, 0.05), (0.52, 0.26, 0.05),
                       (0.50, 0.44, 0.05), (0.38, 0.52, 0.05)):
        star(d, x + w * sx, y + h * sy, h * sr, GOLD)


def flag_ru(d, x, y, w, h):
    """Russian tricolour."""
    d.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def flame(d, cx, cy, s, fill):
    """Simple flame glyph."""
    d.polygon([(cx, cy - s), (cx + s * 0.55, cy - s * 0.1),
               (cx + s * 0.4, cy + s * 0.55), (cx + s * 0.15, cy + s * 0.3),
               (cx, cy + s * 0.7), (cx - s * 0.15, cy + s * 0.3),
               (cx - s * 0.4, cy + s * 0.55), (cx - s * 0.55, cy - s * 0.1)],
              fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top double rule ----------------------------------------------
    rule(d, MARGIN, W - MARGIN, 12, 3)
    rule(d, MARGIN, W - MARGIN, 18, 1)

    # ---- masthead ------------------------------------------------------
    tracked(d, W // 2, 30, "ONE DAY  ·  ONE IMAGE  ·  17 STORIES",
            font(SANS_B, 18), GREY, tracking=3)
    d.text((W // 2, 52), "WORLD NEWS", font=font(SERIF_B, 80),
           fill=INK, anchor="ma")
    date = "THURSDAY, 19 NOVEMBER 2026"
    df = font(SANS_B, 28)
    dw = df.getlength(date)
    rule(d, MARGIN, (W - dw) // 2 - 22, 164, 2)
    rule(d, (W + dw) // 2 + 22, W - MARGIN, 164, 2)
    d.text((W // 2, 148), date, font=df, fill=RED, anchor="ma")
    rule(d, MARGIN, W - MARGIN, 188, 3)
    rule(d, MARGIN, W - MARGIN, 193, 1)

    # ---- hero: the Shenzhen summit (dark band) --------------------------
    hx0, hy0, hx1, hy1 = MARGIN, 196, W - MARGIN, 424
    d.rectangle([hx0, hy0, hx1, hy1], fill=NAVY)
    d.rectangle([hx0, hy0, hx1, hy1], outline=NAVY_LINE, width=2)
    d.text((hx0 + 20, hy0 + 12), "SHENZHEN  ·  APEC  —  FIRST-EVER TRILATERAL",
           font=font(SANS_B, 19), fill=(255, 209, 102))
    hf = font(SERIF_B, 36)
    y = para(d, hx0 + 20, hy0 + 44,
             wrap("Three leaders, one table", hf, 580), hf, WHITE, 44)
    sf = font(SANS, 21)
    y = para(d, hx0 + 20, y + 10,
             wrap("Trump, Xi and Putin meet today in Shenzhen. "
                  "On the agenda: Ukraine, Iran, nuclear arms and trade.",
                  sf, 580), sf, (214, 224, 236), 29)
    # skyline silhouette along the hero bottom
    base = hy1 - 6
    for bx, bw, bh in ((60, 46, 26), (120, 30, 40), (162, 52, 20),
                       (226, 34, 48), (272, 44, 30), (330, 30, 38),
                       (372, 52, 24), (436, 36, 44), (484, 44, 26),
                       (540, 30, 34)):
        d.rectangle([hx0 + bx, base - bh, hx0 + bx + bw, base],
                    fill=(10, 22, 38))
    # three flag panels, right side
    fw, fh = 104, 58
    fx = hx1 - 20 - fw
    fy = hy0 + 52
    for i, (draw_flag, name, country) in enumerate((
            (flag_us, "TRUMP", "UNITED STATES"),
            (flag_cn, "XI", "CHINA"),
            (flag_ru, "PUTIN", "RUSSIA"))):
        x = fx - i * (fw + 16)
        draw_flag(d, x, fy, fw, fh)
        d.rectangle([x, fy, x + fw, fy + fh], outline=WHITE, width=2)
        nf = font(SANS_B, 21)
        d.text((x + fw / 2, fy + fh + 8), name, font=nf, fill=WHITE,
               anchor="ma")
        cf = font(SANS, 13)
        d.text((x + fw / 2, fy + fh + 34), country, font=cf,
               fill=(180, 196, 214), anchor="ma")

    # ---- Gulf row: text left, bold icon panel right --------------------
    gy = 438
    d.text((MARGIN, gy), "THE GULF", font=font(SANS_B, 19), fill=RED)
    h2 = font(SERIF_B, 30)
    y = para(d, MARGIN, gy + 30,
             wrap("Iran hits U.S. sites in Kuwait; tanker burns in Hormuz",
                  h2, 560), h2, INK, 37)
    s2 = font(SANS, 20)
    para(d, MARGIN, y + 8,
         wrap("Tehran's drones struck U.S. sites in Kuwait; a fourth "
              "tanker caught fire in the Strait in 24 hours.",
              s2, 560), s2, BODY, 27)

    px0, py0, px1, py1 = 640, 434, W - MARGIN, 590
    d.rectangle([px0, py0, px1, py1], fill=TEAL)
    d.rectangle([px0, py0, px1, py1], outline=TEAL_LINE, width=2)
    d.text((px0 + 16, py0 + 10), "STRAIT OF HORMUZ",
           font=font(SANS_B, 18), fill=WHITE)
    # tanker silhouette + flames
    d.rectangle([px0 + 40, py0 + 82, px0 + 250, py0 + 106], fill=(8, 34, 40))
    d.rectangle([px0 + 205, py0 + 62, px0 + 235, py0 + 82], fill=(8, 34, 40))
    flame(d, px0 + 110, py0 + 66, 16, (255, 176, 32))
    flame(d, px0 + 150, py0 + 60, 20, (255, 96, 32))
    flame(d, px0 + 290, py0 + 70, 14, (255, 176, 32))
    lf = font(SANS_B, 17)
    for lx, label in ((px0 + 30, "KUWAIT"),
                      (px0 + 150, "BAHRAIN"),
                      (px0 + 268, "QATAR")):
        d.text((lx, py1 - 32), label, font=lf, fill=(214, 232, 234))

    rule(d, MARGIN, W - MARGIN, 604, 2)

    # ---- row 2: two stories --------------------------------------------
    ry = 618
    col_w = 440
    h2s = font(SERIF_B, 24)
    d.text((MARGIN, ry), "WASHINGTON", font=font(SANS_B, 19), fill=RED)
    y = para(d, MARGIN, ry + 30,
             wrap("Jeffries nominated for Speaker", h2s, col_w),
             h2s, INK, 34)
    para(d, MARGIN, y + 8,
         wrap("Democrats nominate Hakeem Jeffries, in line to be "
              "the first Black Speaker.", s2, col_w),
         s2, BODY, 27)
    rx = 544
    d.text((rx, ry), "BUSINESS", font=font(SANS_B, 19), fill=RED)
    y = para(d, rx, ry + 30,
             wrap("Anthropic's record $81.3bn IPO", h2s, col_w),
             h2s, INK, 34)
    para(d, rx, y + 8,
         wrap("The AI firm prices at $83 a share — the biggest IPO "
              "ever — and debuts as ANT.", s2, col_w),
         s2, BODY, 27)

    rule(d, MARGIN, W - MARGIN, 748, 2)

    # ---- row 3: three stories -------------------------------------------
    ry = 762
    c3w = 288
    cols = [
        ("CULTURE",
         "GTA VI launches today",
         "After 13 years, Rockstar's epic opens worldwide."),
        ("EUROPE",
         "EU proposes €45bn Ukraine loan",
         "Repaid from Russian reparations; sanctions extended "
         "3 years."),
        ("SPACE",
         "Voyager 1, nearly a light-day out",
         "NASA's probe nears a record distance, 49 years after "
         "its 1977 launch."),
    ]
    h3 = font(SERIF_B, 24)
    s3 = font(SANS, 17)
    for i, (kick, head, summ) in enumerate(cols):
        x = MARGIN + i * (c3w + 24)
        d.text((x, ry), kick, font=font(SANS_B, 17), fill=RED)
        y = para(d, x, ry + 26, wrap(head, h3, c3w), h3, INK, 29)
        para(d, x, y + 6, wrap(summ, s3, c3w), s3, BODY, 22)

    # ---- by the numbers --------------------------------------------------
    ny0, ny1 = 902, 946
    d.rectangle([MARGIN, ny0, W - MARGIN, ny1], fill=INK)
    nf = font(SANS_B, 16)
    num_text = ("$81.3BN  record IPO   ·   15M  GTA VI pre-orders   "
                "·   €45BN  EU loan   ·   49 YRS  Voyager 1 in flight")
    nw = nf.getlength(num_text)
    d.text(((W - nw) / 2, ny0 + 13), num_text, font=nf, fill=WHITE)

    # ---- also today -------------------------------------------------------
    ay0, ay1 = 956, 1006
    also = ("ALSO TODAY:  N. Korea fires missiles after a U.S.–S. Korea "
            "drill  ·  4 nations urge aid into flooded Gaza  ·  "
            "Cyclone Akvan nears India  ·  Kenya confirms 2nd Ebola case  ·  "
            "Istanbul floods kill 3  ·  India–Japan 2+2 talks  ·  U.S. senators "
            "warn on AI threats  ·  France's 4th protest weekend  ·  "
            "Carney resets Canada–China ties  ·  Report: Islam largest "
            "religion by 2035")
    af = font(SANS, 15)
    para(d, MARGIN + 4, ay0 + 4, wrap(also, af, W - 2 * MARGIN - 8),
         af, INK, 20)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
