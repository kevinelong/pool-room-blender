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
               "Player-max: wall-to-wall tables, rail drinks only, no food",
               ["Every square foot goes to play; drinks live on wall rails.",
                "Deliveries cross active tables; dining moves elsewhere."]),
    "social": ("Social Hall (current)",
               "The built layout: tables, classroom, and wall two-tops",
               ["The room as built today — the baseline for every option.",
                "Wall two-tops flex between drinking, dining, and watching."]),
    "tournament": ("Tournament House",
                   "Feature table with bleacher sightlines; stage becomes VIP",
                   ["Bleachers and the stage give the feature table an audience.",
                    "Food drops to handhelds while racks are in play."]),
    "lounge": ("Cocktail Lounge",
               "Bar-forward: high-top lounge and drink rails at the entry end",
               ["The lounge meets guests at the door; trays barely travel.",
                "Play capacity gives way to beverage turf."]),
    "bistro": ("Billiards Bistro",
               "Dining-forward: rounds wrap the kitchen door for a hot carry",
               ["Dinner arrives hot — the rounds sit beside the kitchen door.",
                "Cocktails travel farthest; a mid-room drop station would help."]),
    "split": ("Split-House Flex",
              "Beam line divides: fixed tables north, flex banquet south",
              ["Service never crosses the play zone — both doors land in the flex half.",
               "The south half flips between banquet, dining, and overflow."]),
}

RENDERS = {
    c["key"]: (
        os.path.join(ROOT, "renders",
                     "render_v15L3_persp_west_to_ME_5p5ft.png"
                     if c["key"] == "social" else
                     f"render_v16_{c['key']}_persp_west_to_ME_5p5ft.png"),
        os.path.join(ROOT, "renders",
                     "render_v15L3_topdown.png" if c["key"] == "social" else
                     f"render_v16_{c['key']}_topdown.png"),
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

    # eye-level render, full width
    persp = fit(Image.open(persp_p).convert("RGB"), PAGE_W - 2 * M, 700)
    py = 128
    page.paste(persp, (M + (PAGE_W - 2 * M - persp.width) // 2, py))
    cap_y = py + persp.height + 8
    d.text((M, cap_y), "Standing at the Main Entry sight line, eye level",
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
