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
from configs.v16_configs import CONFIGS                     # noqa: E402
from analysis.draw_v16_plans import draw_plan               # noqa: E402

PAGE_W, PAGE_H = 1275, 1650          # US letter @ 150 dpi
M = 40                                # margin
INK = (24, 24, 28)
PAPER = (250, 249, 246)
MUTED = (110, 110, 118)

# Digit-free names, taglines, and trade-off notes for presentation.
CLEAN = {
    "league": ("League Hall",
               "Player-first: the six tables at maximum elbow room, rail drinks",
               ["The same six tables as every option, spread for the widest "
                "aisles in the study.",
                "Drinks live on the west rail; deliveries cross active play."]),
    "social": ("Social Hall (current)",
               "The built layout: six tables, classroom, and wall two-tops",
               ["The room as built today — the baseline for every option.",
                "Wall two-tops flex between drinking, dining, and watching."]),
    "tournament": ("Tournament House",
                   "A north gallery of bleachers and the stage face the feature row",
                   ["The bench gives way to a bleacher gallery; the nearest "
                    "table row becomes the feature row.",
                    "Food drops to handhelds while racks are in play."]),
    "centerline": ("Center Line",
                   "Six tables turned sideways, end-to-end down the middle",
                   ["Every table on display from the full-length side aisles.",
                    "Side-to-side swings between neighbours run tight; the "
                    "table ends get full room."]),
    "eastline": ("East Line + West Lounge",
                 "Tables single-file on the east; hospitality strip west",
                 ["The west side hosts folding rounds and a high-top the "
                  "full length of the room.",
                  "Every delivery crosses the table line — hospitality sits "
                  "opposite the doors."]),
    "westline": ("West Line + Moved Stage",
                 "Tables single-file west; the stage rotates to the east wall",
                 ["Relocating the stage beside the HVAC chase is what makes "
                  "a west-hugging file possible.",
                  "Hospitality fills the east wall around the stage; "
                  "service never crosses play."]),
}

RENDERS = {
    c["key"]: (
        os.path.join(ROOT, "renders",
                     f"render_v16_{c['key']}_persp_west_to_ME_5p5ft.png"),
        os.path.join(ROOT, "renders", f"render_v16_{c['key']}_topdown.png"),
    )
    for c in CONFIGS
}


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
    persp_p, top_p = RENDERS[key]

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # title bar
    d.rectangle([0, 0, PAGE_W, 104], fill=INK)
    d.text((M, 18), f"Pool Room — {name}", font=fnt(38), fill=(255, 255, 255))
    d.text((M, 68), tagline, font=fnt(19, False), fill=(205, 205, 210))

    # eye-level render, full width, with door callouts. All six pages share
    # the same camera (SW end of the room, eye level, aimed east at the
    # Main Entry), so the door pixel anchors are constant: the big dark
    # slab is the Main Entry door in the east wall; the thin dark panel
    # left of it is the Emergency Exit door (south wall) seen edge-on.
    persp = fit(Image.open(persp_p).convert("RGB"), PAGE_W - 2 * M, 700)
    px0 = M + (PAGE_W - 2 * M - persp.width) // 2
    py = 128
    page.paste(persp, (px0, py))
    s = persp.width / 2560.0
    dd = ImageDraw.Draw(page)

    def callout(anchor_2560, label, text_2560):
        ax, ay = px0 + anchor_2560[0] * s, py + anchor_2560[1] * s
        tx, ty = px0 + text_2560[0] * s, py + text_2560[1] * s
        dd.line([tx, ty, ax, ay], fill=(255, 220, 80), width=3)
        dd.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(255, 220, 80))
        f = fnt(16)
        bbox = dd.textbbox((0, 0), label, font=f)
        pad = 5
        dd.rounded_rectangle([tx - pad, ty - pad - (bbox[3] - bbox[1]) - 6,
                              tx + (bbox[2] - bbox[0]) + pad, ty + pad],
                             radius=4, fill=(20, 20, 24))
        dd.text((tx, ty - (bbox[3] - bbox[1]) - 6), label, font=f,
                fill=(255, 255, 255))

    callout((1130, 720), "Main Entry — two steps down, iron rails",
            (1420, 380))
    callout((1360, 640), "wood door standing open", (1620, 990))
    # (v18: the Emergency Exit moved to the west end of the S wall and is
    # behind the camera in this view — no callout.)

    cap_y = py + persp.height + 8
    d.text((M, cap_y),
           "Inside the room at the southwest end, eye level, looking east "
           "toward the Main Entry",
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
    d.text((tx, ty), "In brief", font=fnt(22), fill=INK)
    ty += 44
    import textwrap
    wrap_w = max(18, (PAGE_W - M - tx) // 11)
    for note in notes:
        lines = textwrap.wrap(note, wrap_w)
        for li, line in enumerate(lines):
            d.text((tx + (0 if li == 0 else 14), ty),
                   ("• " if li == 0 else "") + line,
                   font=fnt(18, False), fill=(60, 60, 66))
            ty += 27
        ty += 12
    return page


def main():
    pages = [page_for(c) for c in CONFIGS]
    out = os.path.join(ROOT, "docs", "pool_room_v16_options.pdf")
    pages[0].save(out, save_all=True, append_images=pages[1:],
                  resolution=150.0)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{len(pages)} pages)")


if __name__ == "__main__":
    main()
