#!/usr/bin/env python3
"""Build docs/pool_room_v16_options.pdf — six pages, one configuration per
page. Each page composes the rendered Blender views (eye-level perspective
from the Main Entry sight line + overhead render) with the clean 2D
service-flow diagram. Descriptive text only — no numeric commentary.
For the numbers, see the interactive deck or analysis/scorecards.md.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import CONFIGS, cue_clearance_stats  # noqa: E402
from analysis.draw_v16_plans import draw_plan               # noqa: E402

PAGE_W, PAGE_H = 1275, 1650          # US letter @ 150 dpi
M = 40                                # margin
INK = (24, 24, 28)
PAPER = (250, 249, 246)
MUTED = (110, 110, 118)

# Digit-free names, taglines, and trade-off notes for presentation.
CLEAN = {
    "social": ("Four On Top",
               "Six tables; four rounds and a center fifth on the north end",
               ["Four aligned rounds around a center fifth — one big "
                "social cluster that doubles as a tournament gallery "
                "facing the nearest table row.",
                "Wall two-tops flank every table row on both walls.",
                "FLAG: The cluster runs deliberately tight, and the two-top by "
                "the kitchen door partially fronts it — both accepted."]),
    "fourturned": ("Four On Top — Turned",
                   "The same pattern with every table rotated sideways",
                   ["Four tables in a block at the top, two at the bottom, "
                    "all turned ninety degrees.",
                    "Two-top bands ride the top wall, the seam between the "
                    "clusters, and the bottom wall — every table has "
                    "seating at arm's reach.",
                    "FLAG: the rotated ends run tight side-to-side; the "
                    "west and center aisles are the practical maximum."]),
    "turnleft": ("Four On Top — Turned Left",
                 "The turned pattern slid left",
                 ["Both columns slide toward the left wall: the whole "
                  "east side becomes service and standing room with full "
                  "end swings.",
                  "FLAG: the west end swings run hard against the wall — "
                  "the cost of the slide."]),
    "turnright": ("Four On Top — Turned Right",
                  "The turned pattern slid right",
                  ["Both columns slide toward the right wall, as far as "
                   "the chase and entry well allow; the west side becomes "
                   "service and standing room with full end swings.",
                   "FLAG: the east end swings run hard toward the wall — "
                   "the cost of the slide."]),
    "centerline": ("Center Line",
                   "Six tables turned sideways, end-to-end down the middle",
                   ["Every table on display from the full-length side aisles.",
                    "The service lane runs inboard, between the table ends "
                    "and the east wall tops — the wall lane pinched.",
                    "FLAG: Side-to-side swings between neighbours run tight; the "
                    "table ends get full room."]),
    "eastline": ("East Line + West Lounge",
                 "Tables single-file on the east; six aligned rounds west",
                 ["Six rounds in one line down the west side, each on its "
                  "table's centerline.",
                  "FLAG: the southernmost round narrows the Emergency Exit "
                  "approach — the walk bends around its chairs.",
                  "FLAG: Every delivery crosses the table line — hospitality sits "
                  "opposite the doors."]),
    "eastshift": ("East Line — Shifted Down",
                  "The east line slid toward the bottom wall",
                  ["The top table rejoins the straight line and every "
                   "compromise at the entry end dissolves — all six rounds "
                   "sit on their centerlines at the wall, clear of the "
                   "exit approach.",
                   "FLAG: the bottom table's end swing runs tight against "
                   "the bottom wall — the cost of the slide."]),
    "westline": ("West Line + Wall Rounds",
                 "Tables single-file west; a round beside every table east",
                 ["Every table gets its own five-foot round at matching "
                  "height — all six, per the brief.",
                  "FLAG: the southernmost round crowds the Main Entry "
                  "approach beside the stair rail.",
                  "FLAG: one round sits partially in front of the kitchen "
                  "door — accepted to keep its table paired."]),
    "westshift": ("West Line — Shifted Down",
                  "The west line slid toward the bottom wall",
                  ["The entry end frees up: the sixth round reaches the "
                   "east wall like the rest instead of pulling far "
                   "inboard (its chairs still graze the approach corner).",
                   "FLAG: The third round pulls inboard to keep the kitchen "
                   "door's wall approach clear; kitchen service still "
                   "threads a squeeze between two rounds' chairs.",
                   "FLAG: the bottom table's end swing runs tight against "
                   "the bottom wall — the cost of the slide."]),
}

RENDERS = {
    c["key"]: (
        os.path.join(ROOT, "renders",
                     f"render_v16_{c['key']}_persp_west_to_ME_5p5ft.png"),
        os.path.join(ROOT, "renders", f"render_v16_{c['key']}_topdown.png"),
    )
    for c in CONFIGS
}

# v38: nine sightline views per layout — the original entry view plus all
# four side-to-side and all four corner-to-corner (user). Grid rule:
# 3 per row at nine views, 4 per row at eight or twelve.
SIGHT_VIEWS = [
    ("persp_west_to_ME_5p5ft", "entry end: west → Main Entry"),
    ("sl_side_we", "west wall → east"),
    ("sl_side_ew", "east wall → west"),
    ("sl_side_ns", "north wall → south"),
    ("sl_side_sn", "south wall → north"),
    ("sl_corn_nwse", "NW corner → SE"),
    ("sl_corn_nesw", "NE corner → SW"),
    ("sl_corn_swne", "SW corner → NE"),
    ("sl_corn_senw", "SE corner → NW"),
]


def fnt(size, bold=True):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(p, size)


def fit(img, w, h):
    im = img.copy()
    im.thumbnail((w, h))
    return im


def page_for(cfg):
    key = cfg["key"]
    name, tagline, notes = CLEAN[key]
    # v35: pros / cons split (user) — FLAG-prefixed CLEAN notes are cons
    mode, mn = cue_clearance_stats(cfg)
    pros = [n for n in notes if not n.startswith("FLAG:")]
    cons = [(lambda s: s[0].upper() + s[1:])(n[5:].strip())
            for n in notes if n.startswith("FLAG:")]
    measured = (f'Cue room: most sides about {mode}"; '
                f'shortest clearance {mn:.0f}".')
    persp_p, top_p = RENDERS[key]

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # title bar
    d.rectangle([0, 0, PAGE_W, 104], fill=INK)
    letter = cfg.get("letter", "")
    short = cfg.get("short", "")
    d.text((M, 18), f"{letter} · {name}  —  {short}",
           font=fnt(38), fill=(255, 255, 255))
    d.text((M, 68), tagline, font=fnt(19, False), fill=(205, 205, 210))

    # v38: 3x3 grid of eye-level sightlines (entry view + four sides +
    # four corners), each labelled; 3 per row at nine views, 4 per row
    # at eight or twelve
    views = []
    for suffix, lbl in SIGHT_VIEWS:
        vp = os.path.join(ROOT, "renders", f"render_v16_{key}_{suffix}.png")
        if os.path.exists(vp):
            views.append((vp, lbl))
    per_row = 4 if len(views) in (8, 12) else 3
    ggap = 14
    tile_w = (PAGE_W - 2 * M - (per_row - 1) * ggap) // per_row
    tile_h = tile_w * 9 // 16
    lbl_h = 24
    py = 128
    for vi, (vp, lbl) in enumerate(views):
        r, cix = divmod(vi, per_row)
        vx = M + cix * (tile_w + ggap)
        vy = py + r * (tile_h + lbl_h + 8)
        im = Image.open(vp).convert("RGB").resize((tile_w, tile_h))
        page.paste(im, (vx, vy))
        d.rectangle([vx, vy, vx + tile_w, vy + tile_h],
                    outline=(190, 188, 182))
        d.text((vx + 2, vy + tile_h + 4), lbl,
               font=fnt(15, False), fill=MUTED)
    rows_used = (len(views) + per_row - 1) // per_row
    cap_y = py + rows_used * (tile_h + lbl_h + 8) + 2
    d.text((M, cap_y),
           "Nine eye-level sightlines — the entry view, the four "
           "side-to-side views, and the four corner-to-corner views",
           font=fnt(17, False), fill=MUTED)

    # bottom row: overhead render | clean diagram | notes
    row_y = cap_y + 42
    row_h = PAGE_H - row_y - M - 26
    top = fit(Image.open(top_p).convert("RGB"), 420, row_h)
    page.paste(top, (M, row_y))
    d.text((M, row_y + top.height + 8), "Overhead render",
           font=fnt(17, False), fill=MUTED)

    plan = draw_plan(cfg, score=None, clean=True,
                     title=f"Pool Room — {name}", tagline=tagline)
    plan = fit(plan, 420, row_h)
    px = M + top.width + 28
    page.paste(plan, (px, row_y))
    d.text((px, row_y + plan.height + 8), "Service-flow diagram",
           font=fnt(17, False), fill=MUTED)

    tx = px + plan.width + 28
    ty = row_y + 6
    import textwrap
    wrap_w = max(18, (PAGE_W - M - tx) // 11)

    def block(title, items, tcol, icol):
        nonlocal ty
        d.text((tx, ty), title, font=fnt(22), fill=tcol)
        ty += 40
        for note in items:
            for li, line in enumerate(textwrap.wrap(note, wrap_w)):
                d.text((tx + (0 if li == 0 else 14), ty),
                       ("• " if li == 0 else "") + line,
                       font=fnt(18, False), fill=icol)
                ty += 27
            ty += 10

    block("Pros", pros, (30, 110, 40), (60, 60, 66))
    ty += 10
    block("Cons", cons, (165, 45, 40), (95, 60, 58))
    ty += 6
    for line in textwrap.wrap(measured, wrap_w):
        d.text((tx, ty), line, font=fnt(16, False), fill=MUTED)
        ty += 24
    return page


# v34: fairness order — pages run down the semantic columns (left-shifted,
# then centered, then right-shifted), which lands the strong Four On Top
# pair mid-deck instead of leading the document.
PAGE_ORDER = ["turnleft", "westline", "westshift",
              "social", "fourturned", "centerline",
              "turnright", "eastline", "eastshift"]


def overview_page(ordered):
    """Page 1: the 3x3 semantic grid as a visual table of contents."""
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([0, 0, PAGE_W, 104], fill=INK)
    d.text((M, 18), "Pool Room — Nine Layout Options",
           font=fnt(38), fill=(255, 255, 255))
    d.text((M, 68), "Contents — letters read in presentation order; "
           "columns group where the tables sit: left · centered · right",
           font=fnt(19, False), fill=(205, 205, 210))
    cols = [ordered[0:3], ordered[3:6], ordered[6:9]]
    top, lblh, gap = 130, 46, 16
    col_w = (PAGE_W - 2 * M - 2 * gap) // 3
    tile_h = (PAGE_H - top - M - 3 * lblh - 2 * gap) // 3
    for ci, col in enumerate(cols):
        x0 = M + ci * (col_w + gap)
        y = top
        for cfg in col:
            im = Image.open(os.path.join(
                ROOT, "renders",
                f"render_v16_{cfg['key']}_topdown.png")).convert("RGB")
            w = int(im.width * tile_h / im.height)
            if w > col_w:
                w = col_w
            h = int(im.height * w / im.width)
            im = im.resize((w, h))
            page.paste(im, (x0 + (col_w - w) // 2, y))
            y += h
            pageno = ordered.index(cfg) + 3
            d.text((x0 + (col_w - w) // 2, y + 4),
                   f"{cfg['letter']}. {cfg['short']}", font=fnt(20), fill=INK)
            d.text((x0 + col_w - 8, y + 8), f"p. {pageno}",
                   font=fnt(16, False), fill=MUTED, anchor="ra")
            y += lblh + gap
    return page


SCENARIOS = [
    ("If bar and kitchen revenue leads",
     "Four On Top (D) — by far the most seated hospitality, a two-top at "
     "every row end, and it flips to a banquet for free. Runner-up: any "
     "of the line layouts (B, C, H, I)."),
    ("If serious play leads",
     "Center Line (F) — every table on display with the roomiest typical "
     "clearance in the set, at the price of tight side-to-side between "
     "neighbours; D is the classic-room alternative with the fewest "
     "compromised sides."),
    ("If service simplicity leads",
     "West Line (B, C) — zero cue-crossing service conflicts and the "
     "shortest food runs anywhere: hospitality sits along the service "
     "wall."),
    ("If a clear, welcoming entry leads",
     "The shifted lines (C, I) — the whole line slides away from the "
     "entrance, so the door end opens up and every entry-side compromise "
     "dissolves; I audits cleanest of the whole set."),
    ("If the clustered showroom look leads",
     "The turned trio (A, E, G) — four tables in a block reads dramatic "
     "from the door and every cluster gets its own seating band; accept "
     "the tightest end swings and the thinnest seating in the set."),
    ("If events and spectating lead",
     "Four On Top (D) — the five-round cluster doubles as a gallery "
     "facing the nearest row; East Line (H, I) seats a watching row the "
     "full length of the room."),
    ("If nothing is settled yet",
     "Hold D and one line layout (C or I) as the short list: they bracket "
     "the trade-space — maximum hospitality vs maximum play-and-service "
     "clarity — and both pass every safety and walking audit."),
]


def closing_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([0, 0, PAGE_W, 104], fill=INK)
    d.text((M, 18), "Overview", font=fnt(38), fill=(255, 255, 255))
    d.text((M, 68), "If this, then that — the room decides nothing; the "
           "house's priorities do. Read these as directions, not verdicts.",
           font=fnt(19, False), fill=(205, 205, 210))
    import textwrap
    y = 150
    for head, body in SCENARIOS:
        d.text((M, y), head, font=fnt(24), fill=(20, 20, 24))
        y += 38
        for line in textwrap.wrap(body, 88):
            d.text((M + 22, y), line, font=fnt(19, False), fill=(60, 60, 66))
            y += 30
        y += 22
    # v35: -/./+ impact grid
    import json as _json
    sc = _json.load(open(os.path.join(HERE, "scorecards.json")))
    by = {c["key"]: c for c in sc["configs"]}
    areas = [("play", "Play room"), ("hosp", "Hosp. $"), ("svc", "Service"),
             ("walk", "Walking"), ("entry", "Entry/egress"), ("flip", "Flip")]
    SYM = {"+": "+", ".": "·", "-": "−"}
    gy = y + 6
    d.text((M, gy), "Impact at a glance", font=fnt(24), fill=(20, 20, 24))
    gy += 40
    colw = 130
    x0 = M + 150
    for ai, (_k, lbl) in enumerate(areas):
        d.text((x0 + ai * colw + colw // 2, gy), lbl,
               font=fnt(16), fill=MUTED, anchor="ma")
    gy += 30
    for cfg2 in CONFIGS:
        r = by.get(cfg2["key"], {})
        g = r.get("impact", {})
        d.text((M, gy), f"{cfg2['letter']}. {cfg2['short']}",
               font=fnt(17), fill=(40, 40, 46))
        for ai, (k, _lbl) in enumerate(areas):
            v = g.get(k, ".")
            col = ((30, 130, 45) if v == "+" else
                   (170, 50, 45) if v == "-" else (150, 150, 158))
            d.text((x0 + ai * colw + colw // 2, gy), SYM[v],
                   font=fnt(22), fill=col, anchor="ma")
        gy += 32
    foot = ("Every figure behind these pages is computed from the room "
            "geometry — capacities, cue room, walking widths, egress, and "
            "the revenue proxy (a peak-hour comparator at placeholder "
            "margins, not a forecast). Assumptions and per-metric "
            "conventions: analysis/scorecards.md · live re-ranking: the "
            "interactive decision deck.")
    fy = PAGE_H - M - 76
    for line in textwrap.wrap(foot, 110):
        d.text((M, fy), line, font=fnt(16, False), fill=MUTED)
        fy += 24
    return page


from project_urls import WALKTHROUGH_URL, DOWNLOAD_URL, DECK_URL  # noqa: E402


def walkthrough_page():
    """v37: final page — walk the layouts yourself (URL + QR + what to
    expect). v44: the interactive decision deck gets equal billing —
    every printed surface carries all three central URLs."""
    import qrcode
    import textwrap

    def qr_im(url, px):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                           box_size=14, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        return (qr.make_image(fill_color="black", back_color="white")
                .convert("RGB").resize((px, px), Image.NEAREST))

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)
    d.rectangle([0, 0, PAGE_W, 104], fill=INK)
    d.text((M, 18), "Walk it — then weigh it", font=fnt(38),
           fill=(255, 255, 255))
    d.text((M, 68), "A first-person walkthrough of all nine layouts, and an "
           "interactive deck that re-ranks them live — any browser, "
           "no install", font=fnt(19, False), fill=(205, 205, 210))

    panels = [
        ("WALK IT", WALKTHROUGH_URL),
        ("WEIGH THE OPTIONS", DECK_URL),
    ]
    half = PAGE_W // 2
    qpx = 430
    for i, (label, url) in enumerate(panels):
        cx = half // 2 + i * half
        d.text((cx, 150), label, font=fnt(28), fill=(20, 20, 24),
               anchor="ma")
        page.paste(qr_im(url, qpx), (cx - qpx // 2, 205))
        d.text((cx, 205 + qpx + 12), "scan to open",
               font=fnt(16, False), fill=MUTED, anchor="ma")
        # the URL in large print, split to fit half the page
        u1, u2 = url.split("/artifact/")
        d.text((cx, 205 + qpx + 52), u1 + "/artifact/",
               font=fnt(25), fill=(20, 20, 24), anchor="ma")
        d.text((cx, 205 + qpx + 88), u2,
               font=fnt(25), fill=(20, 20, 24), anchor="ma")
    d.line([half, 160, half, 205 + qpx + 120], fill=(210, 208, 202),
           width=2)

    y = 800
    d.text((M, y), "What to expect", font=fnt(24), fill=(20, 20, 24))
    y += 44
    for item in [
        "The walkthrough opens on a gallery of all nine layouts — one "
        "overhead view each, lettered A through I with its short name. "
        "Click any card to jump straight into that room.",
        "By default an auto-tour walks in through the Main Entrance steps, "
        "loops the whole room on a collision-checked path, walks back out, "
        "and fades to the next layout — A through I, then it starts over.",
        "Click the 3-D view to take the controls: WASD or arrow keys to "
        "walk, mouse to look, Shift to hurry, Esc to hand back to the "
        "tour. You collide with every table, round, and chair — walk the "
        "aisles the servers would.",
        "The decision deck holds every computed number in one comparison "
        "matrix. Set the weights to what the house values — play, "
        "hospitality, service, events — and watch the nine layouts "
        "re-rank live. Presets cover the common priorities.",
        "Both pages are single self-contained files: they load instantly, "
        "work offline, and live in the repository under docs/. The "
        "walkthrough also carries this PDF as a download.",
    ]:
        for li, line in enumerate(textwrap.wrap(item, 92)):
            d.text((M + (0 if li == 0 else 22), y),
                   ("\u2022 " if li == 0 else "") + line,
                   font=fnt(19, False), fill=(60, 60, 66))
            y += 30
        y += 14

    y += 10
    d.text((M, y), "Share this study — one-tap download page for this PDF "
           "and the one-page top-down sheet:", font=fnt(18),
           fill=(20, 20, 24))
    d.text((M, y + 32), DOWNLOAD_URL, font=fnt(22), fill=(20, 20, 24))
    return page


def main():
    bykey = {c["key"]: c for c in CONFIGS}
    ordered = [bykey[k] for k in PAGE_ORDER if k in bykey]
    ordered += [c for c in CONFIGS if c not in ordered]
    # v40 (user): the scenarios page leads the document as "Overview";
    # the 3x3 grid follows as "Contents"
    pages = ([closing_page(), overview_page(ordered)]
             + [page_for(c) for c in ordered]
             + [walkthrough_page()])
    out = os.path.join(ROOT, "docs", "pool_room_v16_options.pdf")
    pages[0].save(out, save_all=True, append_images=pages[1:],
                  resolution=150.0)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{len(pages)} pages)")


if __name__ == "__main__":
    main()
