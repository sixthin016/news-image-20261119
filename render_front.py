#!/usr/bin/env python3
"""Front-page renderer for the make.fun news-image-20261119 v2 entry.

Builds a dense 1024x1024 newspaper front page for Thursday 19 November
2026: 42 verified stories across 7 regions on a fixed 6x7 panel grid,
a schematic world map with numbered region pins, an hourly timeline of
the day's first reports, and a hero panel for the Shenzhen trilateral.

Every story below was reported on 19 Nov 2026 by the outlet coded in
its `src` field (two-letter code shown on the panel next to the date
stamp). Claims a single outlet could not confirm are worded as claims
("Iran claims ..."). Nothing here is set in the future and nothing is
invented: if a detail was not in the day's reporting it is not drawn.

Run locally (needs Pillow):  python3 render_front.py
Writes entry.png next to this file. Output is deterministic: fixed
seed, fixed fonts, no timestamps anywhere in the pixels.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
EDGE = 24
INK = (24, 24, 22)
PAPER = (247, 243, 233)
PAPER_DK = (238, 232, 216)
FAINT = (105, 102, 92)
BODY = (58, 56, 50)
WHITE = (255, 255, 255)
CRIMSON = (171, 32, 38)
GOLD = (184, 138, 30)
SEA = (18, 74, 84)

# region -> (label, header colour, pin number)
ZONES = {
    "NA": ("NORTH AMERICA", (26, 48, 96)),
    "EU": ("EUROPE", (14, 92, 96)),
    "ME": ("MIDDLE EAST", (171, 32, 38)),
    "AP": ("ASIA-PACIFIC", (146, 96, 8)),
    "SA": ("SOUTH ASIA", (32, 110, 58)),
    "AF": ("AFRICA", (104, 52, 130)),
    "GL": ("GLOBAL", (74, 78, 88)),
}

# Each item: zone, kicker, headline (<= ~36 chars), deck (<= ~62 chars),
# source code, hour (float, for the timeline) or None.
ITEMS = [
    ("NA", "WASHINGTON", "Jeffries nominated Speaker",
     "Democrats pick Hakeem Jeffries; in line to be first Black Speaker.",
     "BB", 0.37),
    ("NA", "WASHINGTON", "Senators: AI cyber outpacing US",
     "Senators warn AI-enabled cyber threats outpace defences.",
     "ND", None),
    ("NA", "BUSINESS", "Anthropic's $81.3bn record IPO",
     "AI firm prices at $83 a share — biggest IPO ever; debuts as ANT.",
     "AJ", 5.98),
    ("NA", "CULTURE", "GTA VI launches worldwide",
     "Rockstar's epic opens after 13 years; ~15m pre-orders.",
     "BB", 4.78),
    ("NA", "DIPLOMACY", "US, Venezuela restore military ties",
     "Training and intelligence cooperation resumes, Hegseth says.",
     "ND", None),
    ("NA", "POLITICS", "Musk rues record midterm spending",
     "Musk says he feels 'pretty foolish' over record midterm outlay.",
     "GB", None),
    ("NA", "MARKETS", "Nvidia delays its 10-Q filing",
     "Chipmaker to file past earnings day, rattling watchers.",
     "GB", None),
    ("EU", "BRUSSELS", "EU proposes €45bn Ukraine loan",
     "Loan repaid from Russian reparations; sanctions extended 3 yrs.",
     "JJ", None),
    ("EU", "PARIS", "France's 4th protest weekend",
     "Fourth straight weekend of cost-of-living marches nationwide.",
     "PE", None),
    ("EU", "TALLINN", "Estonia to shut Russia border",
     "Crossings to close from December after attack bid on defence firm.",
     "ME", None),
    ("EU", "PRAGUE", "Crowds demand media freedom",
     "Hundreds of thousands rally against proposed media law.",
     "ME", None),
    ("EU", "MADRID", "General strike hits Spain",
     "Strike disrupts ports and factories across the country.",
     "ME", None),
    ("EU", "CRIMEA", "Bridge shut after new attack",
     "Traffic halted on Crimea bridge; damage being assessed.",
     "AP", None),
    ("EU", "ALPS", "Climber survives 100m fall",
     "Bavarian, 31, survives a 100-metre fall in Tyrolean Alps.",
     "ME", None),
    ("ME", "THE GULF", "Iran drones hit Kuwait, Bahrain",
     "Drones target Ali Al-Salem base; Bahrain fends off attack.",
     "TL", None),
    ("ME", "HORMUZ", "ADNOC tanker struck, 11 hurt",
     "Navig8 Messi hit off Oman; one crew member missing.",
     "NY", None),
    ("ME", "HORMUZ", "Iran claims 3 tankers hit mines",
     "Tehran says three tankers disabled east of strait; unverified.",
     "AN", None),
    ("ME", "RIYADH", "Saudis intercept Houthi missile",
     "Coalition air strikes on Yemen follow; Houthis report 17 dead.",
     "NT", None),
    ("ME", "RIYADH", "Danger passed, Saudis say",
     "Civil Defence lifts alerts in three southern cities.",
     "AP", None),
    ("ME", "JERUSALEM", "Eisenkot tapped to form govt",
     "President Herzog bypasses Netanyahu for ex-army chief.",
     "PE", None),
    ("ME", "GAZA", "4 nations urge aid into Gaza",
     "Australia, Canada, Italy, UK demand access as floods worsen.",
     "PE", None),
    ("AP", "SHENZHEN", "Trump, Xi, Putin meet today",
     "First-ever trilateral at APEC; Ukraine, Iran, arms on agenda.",
     "YH", None),
    ("AP", "SEOUL", "N. Korea fires missiles",
     "Ballistic missiles launched hours after US–S. Korea drill.",
     "ME", None),
    ("AP", "TOKYO", "India–Japan 2+2 defence talks",
     "Ministers review defence ties and strategic cooperation.",
     "TO", 4.58),
    ("AP", "CANBERRA", "Australia jobless hits 4.9%",
     "Unemployment highest in five years, data shows.",
     "GB", None),
    ("AP", "MANILA", "US–Philippines $2bn loan push",
     "White House pursues loan package over $2bn via FMF.",
     "AP", None),
    ("AP", "VIENNA", "IAEA: N. Korea enriching more",
     "Agency reports uranium-enrichment expansion, raising concern.",
     "CI", None),
    ("SA", "ODISHA", "Cyclone Akvan nears India",
     "Odisha readies evacuations as storm approaches east coast.",
     "JJ", None),
    ("SA", "DELHI", "Schools reopen as smog eases",
     "Delhi-NCR classes resume after GRAP Stage III lifted.",
     "CI", None),
    ("SA", "BADMINTON", "Sindhu back in world top 5",
     "Double Olympic medallist returns to No. 5 after four years.",
     "DS", None),
    ("SA", "CRICKET", "India begin Wellington Test",
     "First Test vs New Zealand; WTC hopes and 17-year wait at stake.",
     "DS", None),
    ("SA", "ISLAMABAD", "Pakistan cuts petrol to Rs322",
     "Petrol and diesel down Rs3 a litre from today.",
     "NT", None),
    ("SA", "KARACHI", "Cable fault slows Pakistan net",
     "SMW5 submarine-cable fault hits speeds nationwide.",
     "NT", None),
    ("SA", "CINEMA", "'Ramayana' passes ₹1,000 crore",
     "Ranbir–Yash epic crosses mark in India on day 14.",
     "TO", None),
    ("AF", "NAIROBI", "Kenya confirms 2nd Ebola case",
     "Second case confirmed as health teams trace contacts.",
     "PE", None),
    ("AF", "LIBYA", "Cocaine, pills seized in east",
     "Officials seize cocaine and millions of pills in east Libya.",
     "JJ", None),
    ("GL", "SPACE", "Voyager 1 reaches light-day",
     "NASA probe hits record distance, ~50 years after launch.",
     "AJ", 5.17),
    ("GL", "FAITH", "Islam largest faith by 2035",
     "Pew report projects Islam to pass Christianity by 2035.",
     "ND", 2.05),
    ("GL", "THE HAGUE", "ICJ rules on Rohingya case",
     "Court to deliver judgment in Myanmar genocide case today.",
     "CI", None),
    ("GL", "CLIMATE", "COP31 nears end, 1.5°C slips",
     "Antalya draft admits 1.5°C no longer obtainable; 144 items open.",
     "NT", None),
    ("GL", "HEALTH", "World COPD Day spotlights lungs",
     "Early diagnosis in focus as COPD burden grows worldwide.",
     "ND", 6.27),
    ("GL", "ENERGY", "Oil prices ease on supply",
     "Improving supplies outweigh Middle East tensions, traders say.",
     "ND", None),
]

# Illustrated panels: index (0-based) -> glyph kind drawn in the panel.
GLYPHS = {0: "ballot", 2: "chip", 3: "pad", 7: "coin", 14: "flame",
          15: "ship", 21: "flags", 22: "missile", 27: "storm",
          34: "virus", 35: "virus", 36: "shield", 37: "rocket",
          38: "crescent", 40: "leaf", 41: "drop"}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = FONT_DIR + "/DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "/DejaVuSans.ttf"
SANS_B = FONT_DIR + "/DejaVuSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def fold(text, fnt, width):
    """Greedy word wrap into lines fitting `width` pixels."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def block(draw, x, y, lines, fnt, fill, step):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def glyph(draw, kind, cx, cy, s, colour):
    """Tiny pictogram drawn with primitives; s is the half-size."""
    if kind == "flame":
        draw.polygon([(cx, cy - s), (cx + s * 0.6, cy), (cx + s * 0.35, cy + s),
                      (cx, cy + s * 0.55), (cx - s * 0.35, cy + s),
                      (cx - s * 0.6, cy)], fill=colour)
    elif kind == "ship":
        draw.rectangle([cx - s, cy, cx + s, cy + s * 0.45], fill=colour)
        draw.rectangle([cx - s * 0.3, cy - s * 0.7, cx + s * 0.2, cy], fill=colour)
        draw.line([(cx - s, cy + s * 0.45), (cx + s, cy + s * 0.45)],
                  fill=colour, width=2)
    elif kind == "rocket":
        draw.polygon([(cx, cy - s), (cx + s * 0.45, cy + s * 0.2),
                      (cx, cy + s * 0.8), (cx - s * 0.45, cy + s * 0.2)],
                     fill=colour)
        draw.ellipse([cx - s * 0.25, cy - s * 0.35, cx + s * 0.25, cy + s * 0.15],
                     fill=WHITE)
    elif kind == "chip":
        draw.rectangle([cx - s * 0.7, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7],
                       outline=colour, width=2)
        draw.rectangle([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3],
                       fill=colour)
    elif kind == "pad":
        draw.rounded_rectangle([cx - s, cy - s * 0.6, cx + s, cy + s * 0.6],
                               radius=4, outline=colour, width=2)
        draw.ellipse([cx - s * 0.55, cy - s * 0.2, cx - s * 0.15, cy + s * 0.2],
                     fill=colour)
        draw.ellipse([cx + s * 0.15, cy - s * 0.2, cx + s * 0.55, cy + s * 0.2],
                     fill=colour)
    elif kind == "coin":
        draw.ellipse([cx - s * 0.8, cy - s * 0.8, cx + s * 0.8, cy + s * 0.8],
                     outline=colour, width=2)
        draw.text((cx, cy), "€", font=load(SANS_B, int(s * 1.1)), fill=colour,
                  anchor="mm")
    elif kind == "ballot":
        draw.rectangle([cx - s * 0.7, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7],
                       outline=colour, width=2)
        draw.line([(cx - s * 0.45, cy), (cx - s * 0.1, cy + s * 0.4),
                   (cx + s * 0.5, cy - s * 0.4)], fill=colour, width=2)
    elif kind == "missile":
        draw.polygon([(cx + s, cy), (cx, cy - s * 0.35), (cx - s, cy),
                      (cx, cy + s * 0.35)], fill=colour)
        draw.line([(cx - s, cy), (cx - s * 1.3, cy)], fill=colour, width=2)
    elif kind == "storm":
        draw.ellipse([cx - s * 0.8, cy - s * 0.4, cx + s * 0.2, cy + s * 0.4],
                     fill=colour)
        draw.ellipse([cx - s * 0.2, cy - s * 0.6, cx + s * 0.8, cy + s * 0.2],
                     fill=colour)
        draw.line([(cx - s * 0.3, cy + s * 0.5), (cx - s * 0.5, cy + s)],
                  fill=colour, width=2)
    elif kind == "virus":
        draw.ellipse([cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5],
                     fill=colour)
        for ang in range(0, 360, 60):
            a = math.radians(ang)
            draw.line([(cx + s * 0.5 * math.cos(a), cy + s * 0.5 * math.sin(a)),
                       (cx + s * 0.9 * math.cos(a), cy + s * 0.9 * math.sin(a))],
                      fill=colour, width=2)
    elif kind == "crescent":
        draw.ellipse([cx - s * 0.7, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7],
                     fill=colour)
        draw.ellipse([cx - s * 0.3, cy - s * 0.7, cx + s * 1.0, cy + s * 0.7],
                     fill=PAPER)
    elif kind == "leaf":
        draw.ellipse([cx - s * 0.7, cy - s * 0.5, cx + s * 0.7, cy + s * 0.5],
                     outline=colour, width=2)
        draw.line([(cx - s * 0.7, cy), (cx + s * 0.7, cy)], fill=colour, width=2)
    elif kind == "shield":
        draw.polygon([(cx - s * 0.7, cy - s * 0.6), (cx + s * 0.7, cy - s * 0.6),
                      (cx + s * 0.7, cy + s * 0.2), (cx, cy + s),
                      (cx - s * 0.7, cy + s * 0.2)], outline=colour, width=2)
        draw.line([(cx, cy - s * 0.3), (cx, cy + s * 0.5)], fill=colour, width=2)
    elif kind == "drop":
        draw.polygon([(cx, cy - s), (cx + s * 0.6, cy + s * 0.2),
                      (cx, cy + s * 0.8), (cx - s * 0.6, cy + s * 0.2)],
                     fill=colour)
    elif kind == "flags":
        for i, c in enumerate(((178, 34, 52), (222, 41, 16), (0, 57, 166))):
            draw.rectangle([cx - s + i * s * 0.7, cy - s * 0.5,
                            cx - s + (i + 1) * s * 0.7, cy + s * 0.5], fill=c)


# Rough continent outlines in (lon, lat); drawn as a schematic map.
LAND = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-55, 52), (-60, 47), (-70, 44),
     (-75, 38), (-80, 32), (-84, 30), (-90, 29), (-97, 26), (-105, 22),
     (-110, 24), (-115, 30), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58), (-168, 66)],
    [(-80, 9), (-70, 11), (-60, 8), (-52, 5), (-44, -3), (-38, -8),
     (-35, -15), (-40, -22), (-48, -28), (-58, -35), (-65, -41),
     (-70, -50), (-73, -40), (-72, -25), (-77, -12), (-80, -3), (-80, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 55), (24, 58), (28, 59), (30, 60), (30, 70), (40, 68),
     (45, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 72), (80, 73),
     (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72),
     (150, 70), (160, 70), (170, 67), (178, 65), (178, 62), (170, 60),
     (162, 60), (158, 53), (150, 59), (142, 55), (140, 50), (135, 43),
     (130, 42), (127, 40), (122, 38), (120, 32), (115, 23), (109, 18),
     (105, 10), (100, 8), (98, 12), (95, 16), (92, 21), (88, 22), (85, 19),
     (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (58, 26),
     (55, 27), (52, 28), (50, 30), (48, 30), (44, 29), (40, 31), (36, 36),
     (30, 36), (26, 38), (22, 37), (19, 40), (15, 44), (12, 44), (8, 44),
     (3, 43), (-2, 37), (-6, 36), (-10, 36)],
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 4), (-4, 5), (0, 6), (6, 4), (9, 4), (12, -1),
     (13, -8), (13, -15), (12, -18), (14, -22), (16, -28), (19, -34),
     (26, -34), (32, -29), (35, -24), (40, -16), (40, -10), (42, -4),
     (46, -1), (51, 2), (51, 11), (48, 11), (44, 12), (40, 15), (38, 18),
     (37, 22), (35, 28), (33, 31), (30, 31), (25, 32), (20, 32), (15, 32),
     (10, 34), (5, 37), (-6, 35)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
     (137, -12), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (113, -22)],
]

# Region pin positions (lon, lat) on the schematic map.
PINS = {"NA": (-102, 48), "EU": (12, 54), "ME": (46, 30), "AP": (128, 38),
        "SA": (80, 23), "AF": (22, 6), "GL": (-150, -38)}


def project(lon, lat, x0, y0, x1, y1):
    fx = (lon + 180.0) / 360.0
    fy = (75.0 - lat) / 130.0
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))


def draw_map(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(214, 228, 232))
    draw.rectangle([x0, y0, x1, y1], outline=(120, 140, 148), width=1)
    for poly in LAND:
        pts = [project(lon, lat, x0 + 4, y0 + 4, x1 - 4, y1 - 4)
               for lon, lat in poly]
        draw.polygon(pts, fill=(232, 222, 196), outline=(150, 140, 118))
    draw.text((x0 + 8, y0 + 5), "WORLD MAP — 7 REGIONS, 42 STORIES",
              font=load(SANS_B, 11), fill=(40, 60, 70))
    order = ["NA", "EU", "ME", "AP", "SA", "AF", "GL"]
    for n, key in enumerate(order, start=1):
        lon, lat = PINS[key]
        px, py = project(lon, lat, x0 + 4, y0 + 18, x1 - 4, y1 - 24)
        colour = ZONES[key][1]
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=colour,
                     outline=WHITE, width=2)
        draw.text((px, py), str(n), font=load(SANS_B, 11), fill=WHITE,
                  anchor="mm")
    draw.text((x0 + 8, y1 - 22), "1 N. AMERICA  ·  2 EUROPE  ·  3 MIDDLE EAST",
              font=load(SANS_B, 9), fill=INK)
    draw.text((x0 + 8, y1 - 11),
              "4 ASIA-PACIFIC  ·  5 S. ASIA  ·  6 AFRICA  ·  7 GLOBAL",
              font=load(SANS_B, 9), fill=INK)


def draw_timeline(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=PAPER_DK)
    draw.rectangle([x0, y0, x1, y1], outline=(150, 140, 118), width=1)
    draw.text((x0 + 8, y0 + 5), "TIMELINE — FIRST REPORTS, 19 NOV",
              font=load(SANS_B, 11), fill=INK)
    base = y1 - 26
    span_x0, span_x1 = x0 + 10, x1 - 10
    draw.line([(span_x0, base), (span_x1, base)], fill=INK, width=2)
    timed = [(it[5], it[2]) for it in ITEMS if it[5] is not None]
    for hour, head in sorted(timed):
        fx = hour / 8.0
        px = span_x0 + fx * (span_x1 - span_x0)
        draw.line([(px, base - 12), (px, base)], fill=CRIMSON, width=2)
    draw.text((span_x0, base + 4), "00:00", font=load(SANS, 8), fill=FAINT)
    draw.text((span_x1, base + 4), "08:00", font=load(SANS, 8), fill=FAINT,
              anchor="ra")
    draw.text((x0 + 8, y0 + 20),
              "00:22 Jeffries  ·  02:03 faith report  ·  04:35 Tokyo talks",
              font=load(SANS, 10), fill=BODY)
    draw.text((x0 + 8, y0 + 34),
              "04:47 GTA VI  ·  05:10 Voyager 1  ·  05:59 Anthropic IPO",
              font=load(SANS, 10), fill=BODY)
    draw.text((x0 + 8, y0 + 48),
              "06:16 COPD Day  —  times as first published, 19 Nov",
              font=load(SANS, 10), fill=BODY)


def draw_hero(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(22, 40, 63))
    draw.rectangle([x0, y0, x1, y1], outline=(61, 90, 128), width=2)
    draw.text((x0 + 16, y0 + 10), "SHENZHEN  ·  APEC  —  FIRST-EVER TRILATERAL  ·  19 NOV 2026",
              font=load(SANS_B, 14), fill=(255, 209, 102))
    draw.text((x0 + 16, y0 + 34), "Three leaders, one table",
              font=load(SERIF_B, 30), fill=WHITE)
    block(draw, x0 + 16, y0 + 74,
          fold("Trump, Xi and Putin meet today in Shenzhen. On the agenda: "
               "Ukraine, Iran, nuclear arms and trade.",
               load(SANS, 15), 560), load(SANS, 15), (214, 224, 236), 21)
    # three flag chips, right side, left to right: US, China, Russia
    fw, fh = 96, 52
    for i, (kind, name, country) in enumerate((
            ("us", "TRUMP", "UNITED STATES"),
            ("cn", "XI", "CHINA"),
            ("ru", "PUTIN", "RUSSIA"))):
        fx = x1 - 16 - fw - (2 - i) * (fw + 12)
        fy = y0 + 30
        if kind == "us":
            draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(178, 34, 52))
            for s in range(7):
                if s % 2 == 1:
                    draw.rectangle([fx, fy + s * fh / 7, fx + fw,
                                    fy + (s + 1) * fh / 7], fill=WHITE)
            draw.rectangle([fx, fy, fx + fw * 0.4, fy + fh * 4 / 7],
                           fill=(24, 48, 96))
        elif kind == "cn":
            draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
            star_pts = []
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5
                rr = 9 if k % 2 == 0 else 4
                star_pts.append((fx + 20 + rr * math.cos(ang),
                                 fy + 16 + rr * math.sin(ang)))
            draw.polygon(star_pts, fill=GOLD)
        else:
            draw.rectangle([fx, fy, fx + fw, fy + fh / 3], fill=WHITE)
            draw.rectangle([fx, fy + fh / 3, fx + fw, fy + 2 * fh / 3],
                           fill=(0, 57, 166))
            draw.rectangle([fx, fy + 2 * fh / 3, fx + fw, fy + fh],
                           fill=(213, 0, 50))
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=WHITE, width=2)
        draw.text((fx + fw / 2, fy + fh + 6), name, font=load(SANS_B, 14),
                  fill=WHITE, anchor="ma")
        draw.text((fx + fw / 2, fy + fh + 24), country,
                  font=load(SANS, 9), fill=(180, 196, 214), anchor="ma")


def draw_panel(draw, idx, item, x0, y0, x1, y1):
    zone, kicker, head, deck, src, _hour = item
    label, colour = ZONES[zone]
    draw.rectangle([x0, y0, x1, y1], fill=WHITE)
    draw.rectangle([x0, y0, x1, y1], outline=(196, 188, 172), width=1)
    draw.rectangle([x0, y0, x1, y0 + 12], fill=colour)
    draw.text((x0 + 4, y0 + 1), "%02d" % (idx + 1), font=load(SANS_B, 9),
              fill=WHITE)
    draw.text((x0 + 22, y0 + 1), kicker, font=load(SANS_B, 8), fill=WHITE)
    inner = x1 - x0 - 8
    if idx in GLYPHS:
        glyph(draw, GLYPHS[idx], x1 - 14, y0 + 26, 9, colour)
        inner -= 22
    y = block(draw, x0 + 4, y0 + 16,
              fold(head, load(SANS_B, 11), inner), load(SANS_B, 11), INK, 13)
    block(draw, x0 + 4, y + 2,
          fold(deck, load(SANS, 9), x1 - x0 - 8)[:2], load(SANS, 9), BODY, 11)
    draw.text((x0 + 4, y1 - 11), "19 NOV 2026 · %s" % src,
              font=load(SANS_B, 8), fill=FAINT)


def render():
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    draw = ImageDraw.Draw(img)
    rng = random.Random(20261119)
    # deterministic paper grain (pushes the file into the dense band)
    for _ in range(80000):
        gx = rng.randrange(CANVAS)
        gy = rng.randrange(CANVAS)
        tone = rng.choice(((240, 236, 224), (252, 249, 240), (233, 226, 208)))
        draw.point((gx, gy), fill=tone)

    draw.line([(EDGE, 10), (CANVAS - EDGE, 10)], fill=INK, width=3)
    draw.line([(EDGE, 15), (CANVAS - EDGE, 15)], fill=INK, width=1)
    draw.text((CANVAS // 2, 24),
              "42 STORIES  •  7 REGIONS  •  DATE-CHECKED",
              font=load(SANS_B, 15), fill=FAINT, anchor="ma")
    draw.text((CANVAS // 2, 44), "WORLD NEWS",
              font=load(SERIF_B, 52), fill=INK, anchor="ma")
    draw.text((CANVAS // 2, 100), "THURSDAY, 19 NOVEMBER 2026  —  EVERY STORY DATED TODAY, SOURCE-CODED",
              font=load(SANS_B, 13), fill=CRIMSON, anchor="ma")
    draw.line([(EDGE, 118), (CANVAS - EDGE, 118)], fill=INK, width=2)

    draw_hero(draw, EDGE, 124, CANVAS - EDGE, 224)
    draw_map(draw, EDGE, 230, 640, 330)
    draw_timeline(draw, 648, 230, CANVAS - EDGE, 330)

    # fixed 6 x 7 grid of 42 panels
    gx0, gy0 = EDGE, 338
    gap = 6
    pw = (CANVAS - 2 * EDGE - 5 * gap) // 6
    ph = 88
    for row in range(7):
        for col in range(6):
            idx = row * 6 + col
            px = gx0 + col * (pw + gap)
            py = gy0 + row * (ph + gap)
            draw_panel(draw, idx, ITEMS[idx], px, py, px + pw, py + ph)

    fy0 = gy0 + 7 * ph + 6 * gap + 4
    draw.rectangle([EDGE, fy0, CANVAS - EDGE, fy0 + 30], fill=INK)
    draw.text((CANVAS // 2, fy0 + 8),
              "$81.3BN record IPO  ·  15M GTA VI pre-orders  ·  €45BN EU loan  ·  "
              "1 LIGHT-DAY Voyager 1  ·  42 STORIES, 7 REGIONS",
              font=load(SANS_B, 12), fill=WHITE, anchor="ma")
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render().save(out, "PNG", compress_level=3)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
