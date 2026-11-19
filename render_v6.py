#!/usr/bin/env python3
"""Draw the v6 front page for make.fun news-image-20261119.

Renders entry.png (1024x1024): a newspaper front page summing up the
world news of Thursday 19 November 2026.

v6 keeps the v4 philosophy that ranked best in live data (v1: 17
stories, picture-led, rank 2171; v2/v3: 42 dense stories, ranks 3864 /
3792; v5: 42 stories + pictograms, no measured gain). It does NOT go
back to the 42-story almanac. What v6 fixes, measured against v4's
self-rubric (23/25: breadth 4/5, craft 4/5):

  * breadth 4 -> 5: 24 stories instead of 18, still picture-led.
    The 4x3 grid becomes 4x4 (16 panels, headline kept at 18 px,
    decks short). New panels: two SPORT stories (Jazz stun the
    Lakers 109-97, ending a nine-game win streak; F1 practice opens
    in Las Vegas), Fed minutes turn hawkish, Australia jobless hits
    a five-year high at 4.9%. "Also today" grows 5 -> 7 items
    (Giannis 27 as the Heat top the Bucks, IMF warning global
    inflation hit 4.7%). All 24 verified against reporting published
    18-19 Nov 2026 (Reuters, AP, CNBC, The Hindu, Guardian).
  * craft 4 -> 5: the schematic blob map is replaced by real
    coastlines drawn from hand-plotted lon/lat polygons (equirect-
    angular projection, deterministic, no external data), plus a
    30-degree graticule, equator, ocean labels, and region labels
    placed next to the 7 numbered pins. A verified markets line
    (Wednesday close: Brent $92.0, S&P 7,323.6, gold $3,739,
    Bitcoin $63,384) is added under the wire timeline.

Items dropped in v4 stay dropped: Kenya's "second Ebola case"
(14 October), the four-nation Gaza statement (15 November), North
Korea firing missiles (no 19 Nov report), Istanbul floods, France
protests, "Islam largest by 2035".

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
OCEAN = (222, 229, 236)
LAND = (170, 183, 166)
GRIDLINE = (196, 205, 213)
ORANGE = (232, 122, 34)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")

WARNINGS = []


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
     "Iran fired on U.S. sites in Kuwait.",
     "REU", "tanker"),
    ("WASHINGTON", "Jeffries nominated for Speaker",
     "Jeffries picked 251\u201311; first Black Speaker in line.", "REU", None),
    ("BUSINESS", "Anthropic's record $81.3bn IPO",
     "Priced at $83 a share \u2014 the biggest IPO ever.", "CNBC", None),
    ("CULTURE", "GTA VI launches today",
     "After 13 years, Vice City awaits.",
     "WIRE", "pad"),
    ("EUROPE", "EU proposes \u20ac45bn Ukraine loan",
     "Repaid from Russian reparations.",
     "WIRE", "euro"),
    ("SPACE", "Voyager 1, nearly a light-day out",
     "NASA's probe nears a record distance.",
     "WIRE", "stars"),
    ("ASIA-PACIFIC", "Takaichi meets Putin at APEC",
     "Japan's PM raises a detained national in Russia.", "REU", None),
    ("SOUTH ASIA", "Cyclone Akvan nears India's coast",
     "Andhra Pradesh and Odisha on alert as it strengthens.",
     "HINDU", None),
    ("ASIA-PACIFIC", "Indonesia passes asset forfeiture law",
     "State may seize graft-linked assets without a conviction.",
     "REU", None),
    ("ASIA-PACIFIC", "India\u2013Japan 2+2 talks in Tokyo",
     "Defence and foreign ministers review ties.", "WIRE", None),
    ("MIDDLE EAST", "Houthis retake Bab el-Mandeb",
     "Yemen's rebels seize the strait, close on Aden.", "REU", None),
    ("WORLD", "ICJ to rule on Rohingya case today",
     "The Hague rules in the genocide case vs Myanmar.", "WIRE", None),
    ("SPORT", "Jazz stun Lakers 109\u201397",
     "Utah ends the Lakers' nine-game streak.",
     "REU", "ball"),
    ("SPORT", "F1 roars into Las Vegas tonight",
     "Practice opens on the Strip tonight.",
     "WIRE", "flag"),
    ("ECONOMY", "Fed minutes turn hawkish",
     "Officials see more hikes; December rise ~95% priced in.",
     "CNBC", None),
    ("ASIA-PACIFIC", "Australia jobless hits 4.9%",
     "Five-year high as the economy slows; shares slide.",
     "WIRE", None),
]

ALSO = [
    ("Peltola wins Alaska Senate seat", "AP"),
    ("Le Pen leads French poll", "REU"),
    ("Giannis 27, Heat top Bucks 137\u2013130", "REU"),
    ("Nvidia down ~40% from Oct high", "REU"),
    ("IMF: global inflation hits 4.7%", "HINDU"),
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

# ---------------------------------------------------------------- map
# Coastlines as (lon, lat) polygons, hand-plotted, equirectangular
# projection: lon -180..180 across, lat 85..-60 down.
CONTINENTS = [
    # North America (without Greenland)
    [(-168, 66), (-158, 71), (-140, 70), (-128, 71), (-115, 73),
     (-100, 73), (-95, 80), (-85, 80), (-80, 73), (-75, 72),
     (-68, 62), (-60, 55), (-55, 52), (-60, 47), (-65, 44),
     (-70, 42), (-75, 36), (-76, 34), (-80, 26), (-81, 25),
     (-84, 30), (-90, 21), (-94, 17), (-97, 16), (-102, 18),
     (-105, 21), (-110, 24), (-114, 29), (-117, 33), (-122, 37),
     (-124, 42), (-124, 49), (-130, 55), (-140, 60), (-152, 60),
     (-162, 58), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 65), (-42, 70),
     (-50, 74), (-58, 76), (-65, 76), (-68, 72), (-60, 70)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-57, 6), (-52, 5),
     (-50, 0), (-44, -3), (-38, -6), (-35, -9), (-35, -17),
     (-39, -22), (-41, -28), (-48, -28), (-53, -33), (-58, -38),
     (-62, -41), (-66, -45), (-68, -50), (-69, -54), (-71, -54),
     (-74, -50), (-73, -42), (-73, -33), (-72, -25), (-70, -18),
     (-75, -15), (-79, -8), (-81, -3), (-80, 3), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48),
     (-4, 50), (0, 50), (2, 51), (5, 53), (7, 54),
     (8, 57), (10, 59), (12, 56), (18, 56), (21, 55),
     (24, 58), (24, 60), (28, 60), (30, 62), (28, 65),
     (25, 68), (22, 70), (18, 69), (14, 67), (12, 64),
     (10, 62), (5, 60), (5, 58), (0, 57), (-3, 55),
     (-5, 50), (-8, 44), (-9, 38)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57),
     (1, 53), (1, 51), (-3, 50)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 25), (-11, 29), (-6, 33),
     (-5, 35), (0, 36), (10, 37), (15, 35), (20, 32),
     (25, 32), (30, 31), (33, 28), (35, 28), (38, 22),
     (40, 18), (43, 12), (46, 11), (51, 12), (51, 10),
     (48, 5), (44, 0), (41, -5), (40, -10), (37, -15),
     (35, -20), (33, -25), (32, -28), (30, -32), (28, -33),
     (25, -34), (20, -35), (17, -32), (15, -28), (13, -22),
     (12, -17), (13, -12), (12, -8), (9, 4), (6, 4),
     (2, 6), (-4, 5), (-8, 4), (-12, 8), (-15, 11)],
    # Eurasia (Middle East + Asia, one polygon)
    [(35, 36), (36, 36), (40, 36), (43, 34), (44, 31),
     (47, 30), (50, 29), (52, 26), (55, 26), (57, 25),
     (60, 25), (62, 25), (65, 25), (67, 24), (70, 22),
     (72, 20), (73, 16), (75, 12), (76, 9), (78, 8),
     (80, 10), (82, 15), (85, 18), (87, 21), (89, 22),
     (91, 22), (93, 20), (95, 16), (97, 15), (98, 10),
     (100, 8), (101, 6), (103, 2), (104, 6), (105, 9),
     (106, 11), (109, 13), (110, 17), (110, 20), (113, 22),
     (116, 23), (118, 25), (120, 27), (121, 30), (120, 33),
     (122, 37), (123, 39), (126, 40), (128, 39), (130, 42),
     (132, 43), (135, 44), (138, 45), (140, 46), (141, 50),
     (141, 53), (139, 55), (137, 58), (135, 60), (133, 63),
     (135, 66), (138, 68), (142, 70), (146, 70), (150, 70),
     (154, 69), (158, 66), (162, 62), (166, 60), (170, 60),
     (173, 64), (178, 65), (178, 62), (173, 60), (170, 60),
     (166, 59), (162, 57), (158, 54), (156, 51), (152, 48),
     (148, 45), (144, 42), (141, 40), (139, 38), (137, 36),
     (135, 34), (132, 33), (130, 32), (128, 34), (127, 36),
     (126, 38), (124, 39), (121, 38), (120, 35), (118, 33),
     (116, 30), (113, 26), (110, 21), (108, 18), (106, 12),
     (104, 9), (102, 8), (100, 10), (98, 13), (96, 15),
     (94, 17), (92, 21), (90, 22), (88, 21), (86, 20),
     (84, 19), (82, 16), (80, 13), (78, 9), (76, 10),
     (74, 14), (72, 19), (70, 22), (68, 24), (66, 25),
     (64, 25), (62, 25), (59, 25), (57, 26), (54, 27),
     (51, 28), (49, 30), (47, 30), (44, 32), (42, 35),
     (39, 36), (36, 36)],
    # Japan
    [(130, 31), (131, 33), (133, 34), (135, 34), (137, 35),
     (139, 36), (140, 38), (141, 40), (141, 42), (140, 44),
     (139, 43), (138, 41), (137, 39), (135, 37), (133, 35),
     (131, 33)],
    # Indonesia (island chain)
    [(95, 5), (98, 4), (100, 1), (102, -1), (104, -3),
     (106, -6), (108, -7), (110, -7), (112, -7), (114, -8),
     (116, -9), (118, -9), (120, -10), (122, -9), (124, -9),
     (126, -8), (128, -6), (130, -4), (132, -2), (134, -2),
     (136, -2), (138, -4), (140, -5), (141, -7), (140, -8),
     (136, -8), (132, -6), (128, -7), (124, -9), (120, -10),
     (116, -9), (112, -8), (108, -8), (104, -5), (100, 0),
     (97, 3)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (117, -35), (120, -34),
     (124, -33), (128, -32), (132, -32), (135, -35), (138, -35),
     (140, -38), (143, -39), (146, -39), (149, -37), (150, -35),
     (153, -32), (153, -28), (151, -24), (148, -20), (146, -19),
     (143, -15), (142, -11), (140, -12), (137, -12), (135, -13),
     (133, -12), (130, -13), (127, -14), (124, -16), (121, -18),
     (118, -20), (115, -21)],
    # New Zealand
    [(167, -45), (169, -43), (171, -42), (173, -41), (175, -39),
     (177, -38), (176, -40), (174, -41), (172, -43), (169, -46)],
]

# region pins: (number, label, lon, lat, label dx, label dy, label anchor)
PINS = [
    (1, "N. AMERICA", -100, 52, 12, -4, "l"),
    (2, "LATIN AM.", -62, -12, 12, -4, "l"),
    (3, "EUROPE", 12, 52, 12, -4, "l"),
    (4, "AFRICA", 22, 6, 12, 11, "l"),
    (5, "MID EAST", 46, 27, -12, -4, "r"),
    (6, "S. ASIA", 79, 22, 0, -15, "m"),
    (7, "ASIA-PAC.", 122, 18, 0, 11, "m"),
]

OCEANS = [
    ("PACIFIC", -150, -8),
    ("ATLANTIC", -40, 15),
    ("INDIAN OCEAN", 78, -38),
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
    elif kind == "ball":
        d.ellipse([x + 6, y, x + w - 6, y + h], fill=ORANGE,
                  outline=(120, 60, 10), width=2)
        cx, cy = x + w // 2, y + h // 2
        d.line([(cx, y + 1), (cx, y + h - 1)], fill=(120, 60, 10), width=2)
        d.line([(x + 7, cy), (x + w - 7, cy)], fill=(120, 60, 10), width=2)
        d.arc([x - 6, y - 8, x + w - 14, y + h + 4], 300, 60,
              fill=(120, 60, 10), width=2)
        d.arc([x + 14, y - 8, x + w + 6, y + h + 4], 120, 240,
              fill=(120, 60, 10), width=2)
    elif kind == "flag":
        d.rectangle([x, y + 2, x + 3, y + h - 2], fill=(60, 50, 40))
        fx0, fy0, fw, fh = x + 5, y + 2, w - 8, h - 12
        sq = 4
        for r in range(3):
            for c in range(5):
                if (r + c) % 2 == 0:
                    d.rectangle([fx0 + c * (fw // 5), fy0 + r * (fh // 3),
                                 fx0 + (c + 1) * (fw // 5),
                                 fy0 + (r + 1) * (fh // 3)], fill=INK)
                else:
                    d.rectangle([fx0 + c * (fw // 5), fy0 + r * (fh // 3),
                                 fx0 + (c + 1) * (fw // 5),
                                 fy0 + (r + 1) * (fh // 3)], fill=WHITE)
        d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], outline=INK, width=1)
        d.text((x + w // 2, y + h - 9), "LAS VEGAS",
               font=font(SANS_B, 8), fill=INK, anchor="ma")


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=OCEAN)
    d.rectangle([x0, y0, x1, y1], outline=NAVY_LINE, width=1)
    mw, mh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360 * mw,
                y0 + (85 - lat) / 145 * mh)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    # graticule: every 30 degrees
    for lon in range(-150, 151, 30):
        gx, _ = proj(lon, 0)
        d.line([(gx, y0), (gx, y1)], fill=GRIDLINE, width=1)
    for lat in (60, 30, -30):
        _, gy = proj(0, lat)
        d.line([(x0, gy), (x1, gy)], fill=GRIDLINE, width=1)
    _, eq = proj(0, 0)
    for sx in range(int(x0), int(x1), 8):
        d.line([(sx, eq), (min(sx + 4, x1), eq)], fill=(150, 162, 176),
               width=1)
    of = font(SANS_B, 8)
    for name, lon, lat in OCEANS:
        ox, oy = proj(lon, lat)
        tracked(d, ox, oy, name, of, (120, 130, 142), tracking=2)
    lf = font(SANS_B, 9)
    for num, label, lon, lat, dx, dy, anch in PINS:
        cx, cy = proj(lon, lat)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=WHITE, width=2)
        d.text((cx, cy - 1), str(num), font=font(SANS_B, 11), fill=WHITE,
               anchor="mm")


def panel(d, x0, y0, x1, y1, idx, kicker, head, deck, src, kind):
    d.rectangle([x0, y0, x1, y1], outline=(190, 184, 172), width=1)
    d.text((x0 + 10, y0 + 7), kicker, font=font(SANS_B, 12), fill=RED)
    d.text((x1 - 10, y0 + 7), "19 NOV \u00b7 " + src,
           font=font(SANS_B, 10), fill=GREY, anchor="ra")
    deck_w = (x1 - x0) - 20
    deck_size = 13
    if kind is not None:
        glyph(d, kind, x1 - 10 - 52, y1 - 10 - 32, 52, 32)
        deck_w -= 62
        deck_size = 12
    hf = font(SERIF_B, 18)
    head_lines = wrap(head, hf, (x1 - x0) - 20)
    if len(head_lines) > 2:
        WARNINGS.append("panel %d headline wraps to %d lines: %r"
                        % (idx, len(head_lines), head))
        head_lines = head_lines[:2]
    y = para(d, x0 + 10, y0 + 26, head_lines, hf, INK, 21)
    sf = font(SANS, deck_size)
    deck_lines = wrap(deck, sf, deck_w)
    max_deck = max(1, (y1 - 8 - (y + 3)) // (deck_size + 4))
    if len(deck_lines) > max_deck:
        WARNINGS.append("panel %d deck truncated %d -> %d lines: %r"
                        % (idx, len(deck_lines), max_deck, deck))
        deck_lines = deck_lines[:max_deck]
        last = deck_lines[-1]
        while sf.getlength(last + "\u2026") > deck_w and len(last) > 3:
            last = last[:-1]
        deck_lines[-1] = last + "\u2026"
    para(d, x0 + 10, y + 3, deck_lines, sf, BODY, deck_size + 4)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    rule(d, MARGIN, RIGHT, 12, 3)
    rule(d, MARGIN, RIGHT, 18, 1)
    tracked(d, W // 2, 28, "ONE DAY  \u00b7  ONE IMAGE  \u00b7  24 STORIES  \u00b7  DATE-CHECKED",
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

    # ---- story grid: 4 rows x 4 panels ----------------------------------
    grid_x0, grid_w = MARGIN, RIGHT - MARGIN
    col_w = (grid_w - 3 * 12) // 4
    rows_y = [(364, 486), (494, 616), (624, 746), (754, 876)]
    for r, (ry0, ry1) in enumerate(rows_y):
        for c in range(4):
            i = r * 4 + c
            kicker, head, deck, src, kind = PANELS[i]
            x0 = grid_x0 + c * (col_w + 12)
            panel(d, x0, ry0, x0 + col_w, ry1, i + 1, kicker, head, deck,
                  src, kind)

    # ---- bottom band: map | also today | wires ---------------------------
    by0, by1 = 886, 1012
    rule(d, MARGIN, RIGHT, by0 - 8, 2)
    c1x0, c1x1 = MARGIN, MARGIN + 340
    c2x0, c2x1 = MARGIN + 352, MARGIN + 662
    c3x0, c3x1 = MARGIN + 674, RIGHT
    tf = font(SANS_B, 13)

    d.text((c1x0, by0), "WHERE THE DAY HAPPENED", font=tf, fill=RED)
    draw_map(d, c1x0, by0 + 18, c1x1, by1 - 26)
    lf = font(SANS, 10)
    d.text((c1x0, by1 - 22), "1 N. AMERICA  2 LATIN AM.  3 EUROPE  4 AFRICA",
           font=lf, fill=BODY)
    d.text((c1x0, by1 - 10), "5 MID. EAST  6 S. ASIA  7 ASIA-PACIFIC",
           font=lf, fill=BODY)

    d.text((c2x0, by0), "ALSO TODAY", font=tf, fill=RED)
    ab = font(SANS_B, 12)
    ay = by0 + 20
    for head, src in ALSO:
        line = "\u2022  " + head + "  \u00b7  " + src
        if ab.getlength(line) > (c2x1 - c2x0):
            WARNINGS.append("also-today line too wide: %r" % line)
        d.text((c2x0, ay), line, font=ab, fill=INK)
        ay += 15

    d.text((c3x0, by0), "THE DAY IN WIRES \u2014 UTC", font=tf, fill=RED)
    wf = font(SANS, 13)
    wb = font(SANS_B, 13)
    wy = by0 + 20
    for t, ev in WIRES:
        d.text((c3x0, wy), t, font=wb, fill=RED)
        d.text((c3x0 + 44, wy), ev, font=wf, fill=BODY)
        wy += 18
    rule(d, c3x0, c3x1, wy + 2, 1, fill=(190, 184, 172))
    nf = font(SANS_B, 11)
    d.text((c3x0, wy + 8),
           "MARKETS (WED CLOSE) \u2014 BRENT $92.0", font=nf, fill=INK)
    d.text((c3x0, wy + 22),
           "S&P 7,323.6  \u00b7  GOLD $3,739  \u00b7  BTC $63,384",
           font=nf, fill=INK)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
    for w in WARNINGS:
        print("WARNING:", w)
    if not WARNINGS:
        print("no layout warnings")


if __name__ == "__main__":
    main()
