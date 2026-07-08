"""Annotate the v16 finalist renders (title bar + orientation + footer).

Callouts are descriptive only — no numeric position coordinates (house
rule since v15). Handles both the top-down and 5.5 ft perspective for each
variant key passed on the command line (default: split lounge).
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys

SRC_DIR = "/tmp/blender_test"

META = {
    # v55: letters A..M in semantic order; keep in sync with configs
    "turnleft": ("A · Four On Top — Turned Left",
                 "the turned pattern slid left · play and service open from the east"),
    "gridleft": ("B · Four On Top — Slid Left",
                 "the straight 2x3 grid + quincunx slid west · the east service lane widens"),
    "gridleftturn": ("C · Four On Top — Slid Left, Turned Corner",
                     "Slid Left with the SE table turned · a showcase corner facing the entry"),
    "westline": ("D · West Line + Wall Rounds",
                 "six tables single-file west · a round beside every table east"),
    "westshift": ("E · West Line — Shifted Down",
                  "the west line slid down-wall · the sixth round reaches the wall"),
    "social": ("F · Four On Top",
               "six tables · four rounds + a center fifth on the north end · two-tops at every row end"),
    "fourturned": ("G · Four On Top — Turned",
                   "six tables rotated 90° · four on top, two below · two-top bands top, middle, bottom"),
    "gridwide": ("H · Four On Top — Wide Aisle",
                 "the straight 2x3 grid with its columns spread · a 72-inch center promenade"),
    "gridbal": ("I · Four On Top — Wide, Beam-Balanced",
                "rows balanced on the beam · four rounds in a staggered row below"),
    "centerline": ("J · Center Line",
                   "six tables turned 90°, end-to-end down the middle · wall two-tops both sides"),
    "centershift": ("K · Center Line — Shifted Down",
                    "the center line slid down-wall · the entry end opens up"),
    "turnright": ("L · Four On Top — Turned Right",
                  "the turned pattern slid right · play and service open from the west"),
    "eastline": ("M · East Line + West Lounge",
                 "six tables single-file east · six aligned rounds down the west"),
    "eastshift": ("N · East Line — Shifted Down",
                  "the east line slid down-wall · top table rejoins the line · all rounds clear"),
}


def get_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def annotate(key):
    name, desc = META[key]
    jobs = [
        (f"render_v16_{key}_topdown.png",
         f"Pool Room v16 — {name} · top-down",
         "orthographic top-down · image-top = SOUTH · Main Entry top-right · "
         "kitchen door mid-right · 1600×3200"),
        (f"render_v16_{key}_persp_west_to_ME_5p5ft.png",
         f"Pool Room v16 — {name} · standing at the Main Entry sight line",
         "cam at south-end west side · aim EAST at Main Entry · eye 5.5 ft · "
         "14 mm · 2560×1440"),
    ]
    for fname, title, foot in jobs:
        src = os.path.join(SRC_DIR, fname)
        if not os.path.isfile(src):
            print(f"  SKIP missing {src}")
            continue
        img = Image.open(src).convert("RGB")
        W, H = img.size
        d = ImageDraw.Draw(img, "RGBA")
        f_title = get_font(max(26, W // 60))
        f_sub = get_font(max(16, W // 110))
        bar = f_title.size + f_sub.size + 34
        d.rectangle([(0, 0), (W, bar)], fill=(20, 20, 24, 210))
        d.text((22, 10), title, font=f_title, fill=(255, 255, 255))
        d.text((22, 16 + f_title.size), desc, font=f_sub, fill=(200, 200, 205))
        d.rectangle([(0, H - f_sub.size - 22), (W, H)], fill=(20, 20, 24, 210))
        d.text((22, H - f_sub.size - 12), foot, font=f_sub,
               fill=(215, 215, 220))
        dst = src.replace(".png", "_annotated.png")
        img.save(dst, "PNG")
        print(f"  wrote {dst}")


if __name__ == "__main__":
    for key in (sys.argv[1:] or ["split", "lounge"]):
        annotate(key)
