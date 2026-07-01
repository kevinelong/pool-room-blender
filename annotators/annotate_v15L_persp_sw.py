"""Annotate the v15L2 SW->NE wide-angle render with title, view info,
and what's visible callouts. Matches the style of prior annotated
perspective renders (side panel + color key + captions)."""
from PIL import Image, ImageDraw, ImageFont
import os

SRC = "/home/user/workspace/render_v15L_persp_SW_to_NE_wide.png"
DST = "/home/user/workspace/render_v15L_persp_SW_to_NE_wide_annotated.png"

# Font resolution
def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

f_title = load_font(28, bold=True)
f_sub   = load_font(16, bold=False)
f_meta  = load_font(14, bold=False)
f_hdr   = load_font(18, bold=True)
f_body  = load_font(14, bold=False)
f_key   = load_font(13, bold=False)

# Load image
src = Image.open(SRC).convert("RGBA")
W_SRC, H_SRC = src.size
print(f"src size: {W_SRC}x{H_SRC}")

# Layout: top title band, left = render at native, right = side panel
PANEL_W = 480
PAD_T   = 110
PAD_B   = 250
PAD_L   = 20
PAD_R   = 20
GAP     = 20

W = W_SRC + PANEL_W + PAD_L + PAD_R + GAP
H = H_SRC + PAD_T + PAD_B

canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
draw = ImageDraw.Draw(canvas)

# Title band
title = "Pool Room - v15L2 Perspective: SW corner \u2192 NE corner (14 mm wide-angle)"
sub   = "Camera in the top-left of the topdown (SW room corner) looking diagonally toward the NE corner (Storage A / Storage B)"
meta  = "5'6\" eye height  \u00b7  14 mm ultra-wide  \u00b7  Cycles 20 samples  \u00b7  1280x720  \u00b7  v15L2 rev: round tables share classroom folding banquet surface"

draw.text((PAD_L, 12),  title, fill=(20, 20, 20, 255), font=f_title)
draw.text((PAD_L, 52),  sub,   fill=(60, 60, 60, 255), font=f_sub)
draw.text((PAD_L, 78),  meta,  fill=(90, 90, 90, 255), font=f_meta)

# Divider under title
draw.line([(PAD_L, 100), (W - PAD_R, 100)], fill=(200, 200, 200, 255), width=1)

# Paste render
img_x = PAD_L
img_y = PAD_T
canvas.paste(src, (img_x, img_y), src)

# Side panel
px = img_x + W_SRC + GAP
py = PAD_T

draw.text((px, py), "VIEW INFO", fill=(20, 20, 20, 255), font=f_hdr)
py += 26
draw.text((px, py), "Camera anchor:", fill=(20, 20, 20, 255), font=f_body)
py += 18
def wrap(text, x, y, width_px, font, fill=(50, 50, 50, 255), line_h=17):
    # Simple word-wrap
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > width_px:
            draw.text((x, y), line, fill=fill, font=font)
            y += line_h
            line = w
        else:
            line = test
    if line:
        draw.text((x, y), line, fill=fill, font=font)
        y += line_h
    return y

py = wrap("SW corner of the room (image top-left of topdown), 22\" east of west wall + 22\" north of south wall; 5'6\" eye height", px + 12, py, PANEL_W - 24, f_body)
py += 6
draw.text((px, py), "Looking:", fill=(20, 20, 20, 255), font=f_body)
py += 18
py = wrap("Wide diagonal toward the NE corner (image bottom-right of topdown) where Storage A (N wall east) and Storage B (E wall north) meet", px + 12, py, PANEL_W - 24, f_body)
py += 14

draw.text((px, py), "WHAT'S VISIBLE", fill=(20, 20, 20, 255), font=f_hdr)
py += 26

sections = [
    ("MAIN ROOM (foreground + mid)",
     "All six Diamond Pro-Am 7ft pool tables recede from the SW corner across the room. Left column (Tables 1/3/5) is the nearest; right column (Tables 2/4/6) trails behind them."),
    ("EAST-WALL TWO-TOPS + BAR STOOLS (v15j/v15k, right foreground)",
     "The east wall two-tops appear on the right with pub bar stools + chrome footrest ring at 4\" off floor. A seated patron is visible at the near two-top; standing pool players are scattered mid-frame."),
    ("BUFFET + PARTITION BEAM (mid-back, deep)",
     "The dark buffet along the east wall and the horizontal green partition beam running across the room are visible in the far background."),
    ("CLASSROOM + ROUND TABLES (v15L2, deep background)",
     "The 2x2 folding banquet grid + the two 48\" folding rounds sit in the far distance near the north wall. Rounds share the same off-white laminate + cream T-mold edge as the banquets."),
    ("STAGE + LOCKERS (v15k, far background left)",
     "The NW stage riser and ball + triple lockers on the north wall are just visible on the far left back."),
    ("STORAGE (NE corner, vanishing point)",
     "Storage A door (north wall east end) and Storage B door (east wall north end) sit near the vanishing point at the upper right."),
    ("GREEN SERVICE LANES (floor)",
     "The perimeter service band (green) shows the 30\" clearance loop weaving among all tables."),
]

for hdr, body in sections:
    # bullet
    draw.ellipse([(px, py + 6), (px + 6, py + 12)], fill=(80, 120, 200, 255))
    py2 = wrap(hdr, px + 14, py, PANEL_W - 26, f_body, fill=(20, 20, 20, 255))
    py = wrap(body, px + 14, py2, PANEL_W - 26, f_body, fill=(55, 55, 55, 255))
    py += 8

# Bottom color key
key_y = PAD_T + H_SRC + 20
draw.text((PAD_L, key_y), "Color key:", fill=(20, 20, 20, 255), font=f_hdr)
key_y += 28

def swatch(x, y, color, label):
    draw.rectangle([(x, y), (x + 20, y + 20)], fill=color, outline=(80, 80, 80, 255), width=1)
    draw.text((x + 28, y + 2), label, fill=(40, 40, 40, 255), font=f_key)

swatches = [
    ((30, 30, 34, 255),    "Charcoal (cabinets, lockers)"),
    ((55, 90, 130, 255),   "Blue felt"),
    ((235, 232, 220, 255), "White laminate (rounds + banquets)"),
    ((140, 30, 40, 255),   "Classroom chairs (burgundy)"),
    ((190, 190, 195, 255), "Chrome (bar-stool footrest)"),
    ((90, 170, 110, 255),  "Service lane (green)"),
    ((15, 15, 15, 255),    "Doors / Stage (black)"),
]
sx = PAD_L
sy = key_y
col_w = 260
for i, (c, lab) in enumerate(swatches):
    if i and i % 4 == 0:
        sx = PAD_L
        sy += 30
    swatch(sx, sy, c, lab)
    sx += col_w

# Footer caption
foot_y = H - 80
draw.line([(PAD_L, foot_y - 8), (W - PAD_R, foot_y - 8)], fill=(220, 220, 220, 255), width=1)
foot = (
    "Ultra-wide 14mm framing from the SW room corner (top-left of topdown) diagonally across the room to the NE corner (bottom-right of topdown). "
    "Includes all 6 pool tables, east-wall two-tops + bar stools, buffet, classroom banquets + rounds, and NW stage/lockers glimpsed on the far left."
)
foot2 = (
    "v15L2 rev: round-table top uses MAT_class_top (0.93, 0.91, 0.84) + MAT_class_bump T-mold edge, matching the folding banquet surface."
)
foot3 = "All prior v15h/v15i/v15j/v15k geometry retained (pool tables, human figures, buffet, stage, lockers, booths, footrest ring)."
draw.text((PAD_L, foot_y), foot,  fill=(40, 40, 40, 255), font=f_body)
draw.text((PAD_L, foot_y + 20), foot2, fill=(40, 40, 40, 255), font=f_body)
draw.text((PAD_L, foot_y + 40), foot3, fill=(40, 40, 40, 255), font=f_body)

canvas.convert("RGB").save(DST, "PNG", optimize=True)
print(f"wrote {DST} size={canvas.size}")
