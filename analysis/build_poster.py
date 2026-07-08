#!/usr/bin/env python3
"""Build docs/pool_room_poster.pdf — an 8.5x14 (legal) black-and-white
line-drawing poster promoting the three central URLs, each with a QR code
and the URL in print. Hero art: a pure line drawing of layout D (Four On
Top) generated from the live config geometry.
"""
import os
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import (  # noqa: E402
    CONFIGS, ROOM_W, ROOM_L, BEAM_Y, HVAC, ENTRY_WELL, table_rect,
    tbl_rot,
)
sys.path.insert(0, HERE)
from project_urls import WALKTHROUGH_URL, DOWNLOAD_URL, DECK_URL  # noqa: E402

DPI = 300
W, H = int(8.5 * DPI), 14 * DPI          # 2550 x 4200
BLACK, WHITE = 0, 255

LINKS = [
    ("WALK IT",
     "A first-person tour of all fourteen layouts — auto-walks each room, "
     "or take the controls. Downloads live at the top of the page.",
     WALKTHROUGH_URL),
    ("GET THE PDF",
     "One tap, one file: the full options study with sightlines, "
     "pros & cons, and the one-page comparison sheet.",
     DOWNLOAD_URL),
    ("WEIGH THE OPTIONS",
     "The interactive decision deck — set what the house values and "
     "watch the fourteen layouts re-rank live.",
     DECK_URL),
]


def font(size, bold=True, mono=False):
    base = "/usr/share/fonts/truetype/dejavu/"
    p = (base + ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf")
         if mono else
         base + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"))
    if not os.path.exists(p):
        p = base + "DejaVuSans.ttf"
    return ImageFont.truetype(p, size)


def draw_plan_lineart(cfg, pw, ph, stroke=5):
    """Pure black-line top-down of a layout (image-top = south, as in
    every other document)."""
    img = Image.new("L", (pw, ph), WHITE)
    d = ImageDraw.Draw(img)
    pad = stroke * 3
    sx = (pw - 2 * pad) / ROOM_W
    sy = (ph - 2 * pad) / ROOM_L

    def X(v):
        return pad + v * sx

    def Y(v):
        return pad + (ROOM_L - v) * sy      # top = south

    def rect(x0, y0, x1, y1, w=stroke):
        d.rectangle([X(x0), Y(y1), X(x1), Y(y0)], outline=BLACK, width=w)

    # room shell (double line)
    d.rectangle([X(0), Y(ROOM_L), X(ROOM_W), Y(0)], outline=BLACK,
                width=stroke + 2)
    d.rectangle([X(0) - stroke * 2, Y(ROOM_L) - stroke * 2,
                 X(ROOM_W) + stroke * 2, Y(0) + stroke * 2],
                outline=BLACK, width=2)
    # doors: thick ticks
    for (x0, y0, x1, y1) in [(30, ROOM_L - 3, 95, ROOM_L),        # EE
                             (ROOM_W - 3, 290, ROOM_W, 330),      # kitchen
                             (276, 0, 312, 3),                    # storage A
                             (ROOM_W - 3, 4, ROOM_W, 40)]:        # storage B
        d.rectangle([X(x0), Y(y1), X(x1), Y(y0)], fill=BLACK)
    # entry well: sunken channel along the S wall, treads at the west end
    ew = ENTRY_WELL
    d.rectangle([X(ew[0]), Y(ew[3]), X(ew[2]), Y(ew[1])],
                outline=BLACK, width=2)
    for tx in (ew[0] + 11, ew[0] + 22):
        d.line([X(tx), Y(ew[3]), X(tx), Y(ew[1])], fill=BLACK, width=2)
    # beam (dashed)
    xx = 0
    while xx < ROOM_W:
        d.line([X(xx), Y(BEAM_Y), X(min(xx + 12, ROOM_W)), Y(BEAM_Y)],
               fill=BLACK, width=2)
        xx += 22
    # HVAC
    rect(*HVAC, w=3)
    d.line([X(HVAC[0]), Y(HVAC[3]), X(HVAC[2]), Y(HVAC[1])],
           fill=BLACK, width=2)
    # tables: cabinet + playfield inner line
    for _n, tx, ty in cfg["tables"]:
        x0, y0, x1, y1 = table_rect(tx, ty, tbl_rot(cfg, _n))
        rect(x0, y0, x1, y1, w=stroke)
        rect(x0 + 7.25, y0 + 7.25, x1 - 7.25, y1 - 7.25, w=2)
    # rounds + chairs
    plus = {(round(px, 1), round(py, 1))
            for px, py in cfg.get("rounds_plus", [])}
    import math
    for cx, cy in cfg.get("rounds", []):
        d.ellipse([X(cx - 30), Y(cy + 30), X(cx + 30), Y(cy - 30)],
                  outline=BLACK, width=stroke)
        a0 = 0 if (round(cx, 1), round(cy, 1)) in plus else 45
        for k in range(4):
            a = math.radians(a0 + 90 * k)
            chx, chy = cx + 40 * math.sin(a), cy + 40 * math.cos(a)
            d.rectangle([X(chx - 6), Y(chy + 6), X(chx + 6), Y(chy - 6)],
                        outline=BLACK, width=2)
    # bar tops + stools
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        ns = hy < 40 or hy > ROOM_L - 40
        w2, l2 = (14, 11) if ns else (11, 14)
        rect(hx - w2, hy - l2, hx + w2, hy + l2, w=3)
        st = [(hx - 16, hy), (hx + 16, hy)] if ns else \
             [(hx, hy - 16), (hx, hy + 16)]
        for sx_, sy_ in st:
            d.ellipse([X(sx_ - 6), Y(sy_ + 6), X(sx_ + 6), Y(sy_ - 6)],
                      outline=BLACK, width=2)
    return img


def draw_plan_grid(configs, cell_h=560, label_h=48, gap=36, cols=3,
                   stroke=4):
    """All twelve layouts as line art in a lettered grid (reading order
    A..I, three per row — same order as every other document)."""
    cell_w = int(cell_h * (ROOM_W / ROOM_L)) + 24
    rows = (len(configs) + cols - 1) // cols
    gw = cols * cell_w + (cols - 1) * gap
    gh = rows * (cell_h + label_h) + (rows - 1) * gap
    img = Image.new("L", (gw, gh), WHITE)
    d = ImageDraw.Draw(img)
    for i, cfg in enumerate(configs):
        r, c = divmod(i, cols)
        x = c * (cell_w + gap)
        y = r * (cell_h + label_h + gap)
        img.paste(draw_plan_lineart(cfg, cell_w, cell_h, stroke=stroke),
                  (x, y))
        text = f"{cfg['letter']} · {cfg['short'].upper()}"
        size = int(label_h * 0.62)
        while size > 12 and d.textlength(text, font=font(size)) > cell_w - 6:
            size -= 2
        d.text((x + cell_w // 2, y + cell_h + 8), text,
               font=font(size), fill=BLACK, anchor="ma")
    return img


def qr_img(url, px):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                      box_size=12, border=2)
    q.add_data(url)
    q.make(fit=True)
    return (q.make_image(fill_color="black", back_color="white")
            .convert("L").resize((px, px), Image.NEAREST))


def main():
    poster = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(poster)
    M = 90
    # double border
    d.rectangle([M, M, W - M, H - M], outline=BLACK, width=8)
    d.rectangle([M + 22, M + 22, W - M - 22, H - M - 22],
                outline=BLACK, width=3)

    # title block
    d.text((W // 2, 230), "THE POOL ROOM", font=font(150), fill=BLACK,
           anchor="ma")
    d.text((W // 2, 420), "FOURTEEN WAYS TO RACK THE ROOM",
           font=font(64), fill=BLACK, anchor="ma")
    d.line([W // 2 - 700, 540, W // 2 + 700, 540], fill=BLACK, width=6)
    d.text((W // 2, 570),
           "SIX TABLES  ·  ONE ROOM  ·  SEE EVERY OPTION, THEN DECIDE",
           font=font(40, False), fill=BLACK, anchor="ma")

    # hero: all twelve layouts as a lettered line-art grid
    grid = draw_plan_grid(CONFIGS, cols=4, cell_h=430)  # 14 layouts, 4 rows
    poster.paste(grid, ((W - grid.width) // 2, 690))
    d.text((W // 2, 690 + grid.height + 22),
           "ALL FOURTEEN LAYOUTS, A TO N — SCAN TO WALK EVERY ONE.",
           font=font(38), fill=BLACK, anchor="ma")

    # three QR panels
    top = 690 + grid.height + 120
    panel_w = (W - 2 * M - 2 * 60) // 3
    qr_px = 560
    for i, (label, blurb, url) in enumerate(LINKS):
        x0 = M + i * (panel_w + 60)
        cx = x0 + panel_w // 2
        y = top
        d.text((cx, y), label, font=font(58), fill=BLACK, anchor="ma")
        y += 95
        q = qr_img(url, qr_px)
        poster.paste(q, (cx - qr_px // 2, y))
        y += qr_px + 26
        import textwrap
        for line in textwrap.wrap(blurb, 34):
            d.text((cx, y), line, font=font(28, False), fill=BLACK,
                   anchor="ma")
            y += 38
        y += 14
        from urllib.parse import urlsplit
        parts = urlsplit(url)
        d.text((cx, y), parts.scheme + "://" + parts.netloc,
               font=font(30, True, mono=True), fill=BLACK, anchor="ma")
        d.text((cx, y + 42), parts.path, font=font(30, True, mono=True),
               fill=BLACK, anchor="ma")

    # footer (letter key lives on the grid labels now)
    d.line([M + 60, H - 260, W - M - 60, H - 260], fill=BLACK, width=4)
    d.text((W // 2, H - 215),
           "EVERY NUMBER COMPUTED FROM THE ROOM GEOMETRY — NOT ESTIMATED",
           font=font(30), fill=BLACK, anchor="ma")

    out = os.path.join(ROOT, "docs", "pool_room_poster.pdf")
    poster.convert("RGB").save(out, resolution=float(DPI))
    png = os.path.join(ROOT, "docs", "pool_room_poster.png")
    poster.save(png)
    print(f"wrote {out} ({os.path.getsize(out)/1e6:.1f} MB) and PNG")


if __name__ == "__main__":
    main()
