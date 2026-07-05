#!/usr/bin/env python3
"""Build docs/pool_room_topdowns.pdf — a single US-letter (8.5x11) page with
all option top-down renders, no words, no annotations.

Layout math: the renders are 1:2 (room aspect). On a portrait letter page
the six tiles come out largest as 3 columns x 2 rows, upright — each tile
~2.7 x 5.4 inches at 300 dpi, which beats every rotated or landscape
arrangement for per-tile area.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import CONFIGS                     # noqa: E402

DPI = 300
PAGE_W, PAGE_H = int(8.5 * DPI), 11 * DPI      # 2550 x 3300
# v27: four options after the Social/Tournament merge — 2x2 tiles beat
# 3x2 for per-tile area; fall back to 3 columns for five or six options
COLS = 2 if len(CONFIGS) <= 4 else 3
ROWS = (len(CONFIGS) + COLS - 1) // COLS
GAP = 20


def main():
    tile_h = (PAGE_H - (ROWS + 1) * GAP) // ROWS          # 1620
    tile_w_fit = (PAGE_W - (COLS + 1) * GAP) // COLS      # 823
    page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    tiles = []
    for c in CONFIGS:
        p = os.path.join(ROOT, "renders",
                         f"render_v16_{c['key']}_topdown.png")
        im = Image.open(p).convert("RGB")
        w = int(im.width * tile_h / im.height)
        if w > tile_w_fit:                                # width-limited
            w = tile_w_fit
            h = int(im.height * w / im.width)
        else:
            h = tile_h
        tiles.append(im.resize((w, h), Image.LANCZOS))
    rows = [tiles[i:i + COLS] for i in range(0, len(tiles), COLS)]
    for r, row_tiles in enumerate(rows):
        x_gap = (PAGE_W - sum(t.width for t in row_tiles)) // (len(row_tiles) + 1)
        x = x_gap
        for t in row_tiles:
            y = GAP + r * (tile_h + GAP)
            page.paste(t, (x, y + (tile_h - t.height) // 2))
            x += t.width + x_gap
    out = os.path.join(ROOT, "docs", "pool_room_topdowns.pdf")
    page.save(out, resolution=float(DPI))
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{len(tiles)} layouts, 8.5x11 @ {DPI}dpi)")


if __name__ == "__main__":
    main()
