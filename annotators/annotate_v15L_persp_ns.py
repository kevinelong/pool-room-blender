"""Annotate v15L E->W across the north strip render. Highlights the round
stacking tables in context between the stage/locker corner and the Storage A
side, with the classroom banquets and booths in view."""
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/user/workspace/render_v15L_persp_E_to_W_north_strip.png"
DST = "/home/user/workspace/render_v15L_persp_E_to_W_north_strip_annotated.png"

INFO = {
    "title": "E \u2192 W across the North Strip (24 mm)",
    "subtitle": "Camera near the east wall, aligned with the round-tables center line, looking west toward the NW stage / locker corner",
    "anchor": "East wall, ~8\" inside; y = 48\" (aligned with round tables' center)",
    "looking": "West along the north strip, past the two round tables toward the stage / locker corner",
    "lens": "24 mm",
    "highlights": [
        "ROUND STACKING TABLES (v15L, NEW - hero of this view): both 48\" folding rounds are dead center in the frame, one nearer and one farther. Chrome splayed legs (four per table) angle outward to black foot caps; an X cross-brace sits under each top; top is white laminate (reads mid-grey under Filmic at -0.4 EV, same as the top-down).",
        "FOLDING BANQUET CLASSROOM (v15k, right side): white-laminate folding banquets with black tubular H-frame legs; burgundy padded stacking chairs on both long sides. This is the 2x2 grid that replaces the old 2x3 - Row 2 was removed to make space for the rounds you see on the left.",
        "STAGE + LOCKERS (v15k, foreground-left silhouette): the tall dark blocks that dominate the left edge are the matte-black stage riser and the ball + triple lockers (72H x 18D against the back wall). This confirms the rounds land squarely BETWEEN the stage and the Storage A door.",
        "BOOTHS + STORAGE A DOOR (far right sliver, mostly out of frame): black-vinyl booth backs run along the north wall to the right of the frame; Storage A door is on the north wall east end just past the far round table.",
        "SEATED PATRON (far-right edge): a v15h seated figure at an east two-top is visible past the classroom - unrelated to the rounds but confirms scale (~68\" figure).",
        "SERVICE-LANE FLOOR (green underfoot): the north strip service lane clears the round tables' south edge; 4 chairs fan across the south half of each round.",
    ],
}

img = Image.open(SRC).convert("RGB")
iw, ih = img.size

PAD_T, PAD_B = 110, 240
PANEL_W = 460
new_w = iw + PANEL_W
new_h = ih + PAD_T + PAD_B
canvas = Image.new("RGB", (new_w, new_h), (248, 248, 248))
canvas.paste(img, (0, PAD_T))
draw = ImageDraw.Draw(canvas)

F = lambda sz, b=False: ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b
    else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
title_f = F(24, True); subt_f = F(13); hdr_f = F(15, True)
body_f = F(13); tiny_f = F(11)

# Title bar
title = f"Pool Room - v15L Perspective: {INFO['title']}"
draw.text((20, 16), title, fill=(20, 20, 20), font=title_f)
draw.text((20, 50), INFO["subtitle"], fill=(70, 70, 70), font=subt_f)
draw.text((20, 72),
          f"5 ft eye height  -  {INFO['lens']} lens  -  Cycles - 960x540  -  v15L: round stacking tables in context",
          fill=(110, 110, 110), font=tiny_f)
draw.line([(20, 96), (new_w - 20, 96)], fill=(180, 180, 180), width=1)

# Side panel
px = iw + 20
py = PAD_T + 4

def wrap(text, font, max_w):
    words = text.split(); out = []; cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= max_w: cur = test
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

draw.text((px, py), "VIEW INFO", fill=(20, 20, 20), font=hdr_f); py += 24
draw.text((px, py), "Camera anchor:", fill=(40, 40, 60), font=body_f); py += 18
for ln in wrap(INFO["anchor"], body_f, PANEL_W - 30):
    draw.text((px + 12, py), ln, fill=(60, 60, 60), font=body_f); py += 17
py += 6
draw.text((px, py), "Looking:", fill=(40, 40, 60), font=body_f); py += 18
for ln in wrap(INFO["looking"], body_f, PANEL_W - 30):
    draw.text((px + 12, py), ln, fill=(60, 60, 60), font=body_f); py += 17
py += 12

draw.text((px, py), "WHAT'S VISIBLE", fill=(20, 20, 20), font=hdr_f); py += 24
for item in INFO["highlights"]:
    draw.ellipse([px + 4, py + 5, px + 10, py + 11], fill=(50, 110, 180))
    lines = wrap(item, body_f, PANEL_W - 60)
    for j, ln in enumerate(lines):
        draw.text((px + 18, py + j * 17), ln, fill=(40, 40, 40), font=body_f)
    py += max(17, 17 * len(lines)) + 6

py += 8
draw.text((px, py), "ORIENTATION KEY", fill=(20, 20, 20), font=hdr_f); py += 22
for ln in [
    "image-top    = ceiling / troffers",
    "image-left   = NW corner (stage, lockers)",
    "image-right  = east wall / Storage A end",
    "camera is on the EAST wall, looking WEST",
]:
    draw.text((px + 4, py), ln, fill=(60, 60, 60), font=tiny_f); py += 14

# Color key (2 rows to keep clear of panel)
legend_y = PAD_T + ih + 24
draw.text((20, legend_y - 22), "Color key:", fill=(20, 20, 20), font=hdr_f)
row1 = [
    ((240, 237, 224), "White laminate (round tops)"),
    ((184, 184, 189), "Chrome splayed legs"),
    ((8, 8, 9), "Black feet / plinth"),
    ((77, 10, 15), "Classroom chairs (burgundy)"),
]
row2 = [
    ((26, 21, 24), "Charcoal / lockers"),
    ((50, 130, 70), "Service-lane floor (BRG)"),
    ((30, 76, 110), "(pool felt, off-frame)"),
]
for row_i, row in enumerate([row1, row2]):
    sx = 20
    ly = legend_y + row_i * 22
    for color, label in row:
        draw.rectangle([sx, ly - 2, sx + 18, ly + 16], fill=color, outline=(0, 0, 0))
        draw.text((sx + 24, ly), label, fill=(20, 20, 20), font=body_f)
        sx += 26 + draw.textbbox((0,0), label, font=body_f)[2] + 16

# Callout arrows drawn ON the render itself for the two round tables
def render_callout(anchor_xy, text, side="above", box_col=(255, 247, 200),
                   border=(120, 100, 30)):
    ax_i, ay_i = anchor_xy
    ax_i += 0
    ay_i += PAD_T
    lines = text if isinstance(text, list) else [text]
    line_h = body_f.size + 4
    pad = 6
    widths = [draw.textbbox((0,0), ln, font=body_f)[2] for ln in lines]
    tw = max(widths) + 2*pad
    th = line_h * len(lines) + 2*pad
    if side == "above":
        bx, by = ax_i - tw/2, ay_i - th - 30
    else:
        bx, by = ax_i - tw/2, ay_i + 30
    bx = max(4, min(bx, iw - tw - 4))
    by = max(PAD_T + 4, min(by, PAD_T + ih - th - 4))
    lp = (bx + tw/2, by + th) if side == "above" else (bx + tw/2, by)
    draw.line([lp, (ax_i, ay_i)], fill=(110, 90, 30), width=1)
    draw.ellipse([ax_i-3, ay_i-3, ax_i+3, ay_i+3], fill=(180, 30, 30))
    draw.rectangle([bx, by, bx+tw, by+th], fill=box_col, outline=border, width=1)
    for i, ln in enumerate(lines):
        draw.text((bx+pad, by+pad+i*line_h), ln, fill=(20, 20, 20), font=body_f)

# On-render callouts anchoring the two rounds
render_callout((410, 320), ["Round table (far, west)", "48\" folding, chrome splayed legs"], side="above")
render_callout((340, 450), ["Round table (near, east)", "same design, 4 chairs south"], side="below")
render_callout((790, 380), ["Folding banquet classroom", "2x2 grid (Row 2 removed)"], side="above")
render_callout((100, 300), ["Stage + lockers", "72H black locker at NW"], side="below")

footer_lines = [
    "v15L: rounds sit between the NW stage (foreground-left silhouette) and the classroom (right), replacing what used to be Row 2 of the training tables.",
    "White laminate tops appear mid-grey here under Filmic tone-mapping at -0.4 EV; the base color remains (0.94, 0.93, 0.88) as spec'd.",
    "All prior v15h/v15i/v15j/v15k geometry retained.",
]
fy = new_h - 14 - 14 * len(footer_lines)
for fl in footer_lines:
    draw.text((20, fy), fl, fill=(90, 90, 90), font=tiny_f); fy += 14

canvas.save(DST, "PNG", optimize=True)
print(f"-> {DST}  size={canvas.size}")
