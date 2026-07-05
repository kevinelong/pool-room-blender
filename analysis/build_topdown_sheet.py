#!/usr/bin/env python3
"""Build docs/pool_room_topdowns.pdf — ONE page, all option top-down
renders side by side, no words, no annotations. Pure visual comparison.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import CONFIGS                     # noqa: E402

GAP = 24
TILE_H = 1400            # each top-down scaled to this height


def main():
    tiles = []
    for c in CONFIGS:
        p = os.path.join(ROOT, "renders",
                         f"render_v16_{c['key']}_topdown.png")
        im = Image.open(p).convert("RGB")
        w = int(im.width * TILE_H / im.height)
        tiles.append(im.resize((w, TILE_H)))
    page_w = sum(t.width for t in tiles) + GAP * (len(tiles) + 1)
    page_h = TILE_H + 2 * GAP
    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
    x = GAP
    for t in tiles:
        page.paste(t, (x, GAP))
        x += t.width + GAP
    out = os.path.join(ROOT, "docs", "pool_room_topdowns.pdf")
    page.save(out, resolution=150.0)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{len(tiles)} layouts on one page)")


if __name__ == "__main__":
    main()
