#!/usr/bin/env python3
"""Build docs/pool_room_topdowns.pdf — a single US-letter (8.5x11) page with
all option top-down renders, no words, no annotations.

v29: the page is organized SEMANTICALLY (user): layouts whose tables sit
left (west) run down the LEFT of the page, centered layouts down the
CENTER, right-(east-)shifted layouts down the RIGHT.
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
GAP = 20

# semantic columns: left-shifted | centered | right-shifted
SHEET_COLS = [
    ["turnleft", "westline", "westshift"],
    ["social", "fourturned", "centerline"],
    ["turnright", "eastline", "eastshift"],
]


def main():
    known = {c["key"] for c in CONFIGS}
    cols = [[k for k in col if k in known] for col in SHEET_COLS]
    # any config not placed falls into the center column
    placed = {k for col in cols for k in col}
    cols[1] += [c["key"] for c in CONFIGS if c["key"] not in placed]
    n_cols = len(cols)
    n_rows = max(len(c) for c in cols)
    tile_h = (PAGE_H - (n_rows + 1) * GAP) // n_rows
    tile_w_fit = (PAGE_W - (n_cols + 1) * GAP) // n_cols
    page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    col_w = (PAGE_W - (n_cols + 1) * GAP) // n_cols
    for ci, col in enumerate(cols):
        x0 = GAP + ci * (col_w + GAP)
        # center each column's tile stack vertically
        tiles = []
        for key in col:
            im = Image.open(os.path.join(
                ROOT, "renders", f"render_v16_{key}_topdown.png")).convert("RGB")
            w = int(im.width * tile_h / im.height)
            if w > tile_w_fit:
                w = tile_w_fit
                h = int(im.height * w / im.width)
            else:
                h = tile_h
            tiles.append(im.resize((w, h), Image.LANCZOS))
        total_h = sum(t.height for t in tiles) + (len(tiles) - 1) * GAP
        y = (PAGE_H - total_h) // 2
        for t in tiles:
            page.paste(t, (x0 + (col_w - t.width) // 2, y))
            y += t.height + GAP
    out = os.path.join(ROOT, "docs", "pool_room_topdowns.pdf")
    page.save(out, resolution=float(DPI))
    n = sum(len(c) for c in cols)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, "
          f"{n} layouts in semantic columns, 8.5x11 @ {DPI}dpi)")


if __name__ == "__main__":
    main()
