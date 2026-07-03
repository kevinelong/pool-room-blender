#!/usr/bin/env python3
"""Build docs/pool_room_v16_options.pdf — six pages, one configuration per
page, clean floor plans only: descriptive labels, no scorecards, no
numeric commentary. For the numbers, see the interactive deck
(docs/decision_deck_v16.html) or analysis/scorecards.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from configs.v16_configs import CONFIGS                     # noqa: E402
from analysis.draw_v16_plans import draw_plan               # noqa: E402

# Digit-free names and taglines for the no-numbers presentation.
CLEAN = {
    "league": ("League Hall",
               "Player-max: wall-to-wall tables, rail drinks only, no food"),
    "social": ("Social Hall (current)",
               "The built layout: tables, classroom, and wall two-tops"),
    "tournament": ("Tournament House",
                   "Feature table with bleacher sightlines; stage becomes VIP"),
    "lounge": ("Cocktail Lounge",
               "Bar-forward: high-top lounge and drink rails at the entry end"),
    "bistro": ("Billiards Bistro",
               "Dining-forward: rounds wrap the kitchen door for a hot carry"),
    "split": ("Split-House Flex",
              "Beam line divides: fixed tables north, flex banquet south"),
}


def main():
    pages = []
    for cfg in CONFIGS:
        name, tagline = CLEAN[cfg["key"]]
        img = draw_plan(cfg, score=None, clean=True,
                        title=f"Pool Room — {name}", tagline=tagline)
        pages.append(img.convert("RGB"))
    out = os.path.join(HERE, "..", "docs", "pool_room_v16_options.pdf")
    pages[0].save(out, save_all=True, append_images=pages[1:],
                  resolution=100.0)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{len(pages)} pages)")


if __name__ == "__main__":
    main()
