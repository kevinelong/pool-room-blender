"""Annotate v15L wide-angle render from Emergency Exit toward NW stage.
Shows the whole room in one frame: pool tables, two-tops, pendants, and the
NW stage/lockers + classroom + rounds in the deep background."""
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/user/workspace/render_v15L_persp_Exit_to_NW_wide.png"
DST = "/home/user/workspace/render_v15L_persp_Exit_to_NW_wide_annotated.png"

INFO = {
    "title": "Emergency Exit \u2192 NW stage / staff storage (14 mm wide-angle)",
    "subtitle": "Camera just inside the Emergency Exit doorway, framing the entire room diagonally toward the NW stage corner",
    "anchor": "Emergency Exit doorway (S wall right, ~22\" inside, 6\" west of door center); 5'6\" eye height",
    "looking": "Wide diagonal toward NW corner (stage + lockers) with a slight rightward bias so the NE-corner staff storage doors sit on the right",
    "lens": "14 mm ultra-wide",
    "highlights": [
        "MAIN ROOM (foreground + mid): all six pool tables (Diamond Pro-Am 7ft, v15h/v15i) recede in a 3x2 grid from the SE corner toward the NW; blue felts + charcoal cabinets + pocket caps clearly readable in the near tables.",
        "TWO-TOPS + BAR-STOOL FOOTREST RING (v15j/v15k, both walls): pub bar stools on either flank sit at the two-tops; the chrome footrest ring at 4\" off floor is visible on the nearest bar stools left and right.",
        "SEATED + STANDING FIGURES (v15h, retained): patrons at two-tops (heads visible) and a couple of pool players scattered mid-frame.",
        "PENDANT LIGHTS + PARTITION BEAM (mid): dark rod pendants hang over the pool tables; the horizontal partition beam runs across the mid-distance (green painted).",
        "CLASSROOM + ROUND TABLES (v15L rev, deep background near stage): the 2x2 folding banquet grid and the two 48\" folding rounds sit far behind the pool tables. Rounds now share the classroom's off-white laminate + cream T-mold edge, so they blend with the banquets in this distant view.",
        "NW STAGE + LOCKERS (v15k, far background): matte-black stage riser and the ball + triple lockers on the north wall are visible past the classroom.",
        "STAFF / STORAGE (NE corner - right of frame): Storage A on the north wall east end and Storage B on the east wall north end sit at the upper-right vanishing zone.",
        "GREEN SERVICE LANES (floor): the perimeter service band shows the 30\" clearance loop weaving among the tables.",
    ],
}

img = Image.open(SRC).convert("RGB")
iw, ih = img.size

PAD_T, PAD_B = 110, 250
PANEL_W = 480
new_w = iw + PANEL_W
new_h = ih + PAD_T + PAD_B
canvas = Image.new("RGB", (new_w, new_h), (248, 248, 248))
canvas.paste(img, (0, PAD_T))
draw = ImageDraw.Draw(canvas)

F = lambda sz, b=False: ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b
    else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
title_f = F(26, True); subt_f = F(14); hdr_f = F(16, True)
body_f = F(14); tiny_f = F(12)

# Title bar
title = f"Pool Room - v15L Perspective: {INFO['title']}"
draw.text((20, 16), title, fill=(20, 20, 20), font=title_f)
draw.text((20, 52), INFO["subtitle"], fill=(70, 70, 70), font=subt_f)
draw.text((20, 76),
          f"5'6\" eye height  -  {INFO['lens']}  -  Cycles 20 samples - 1280x720  -  v15L rev: round tables match classroom surface",
          fill=(110, 110, 110), font=tiny_f)
draw.line([(20, 100), (new_w - 20, 100)], fill=(180, 180, 180), width=1)

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

draw.text((px, py), "VIEW INFO", fill=(20, 20, 20), font=hdr_f); py += 26
draw.text((px, py), "Camera anchor:", fill=(40, 40, 60), font=body_f); py += 20
for ln in wrap(INFO["anchor"], body_f, PANEL_W - 30):
    draw.text((px + 12, py), ln, fill=(60, 60, 60), font=body_f); py += 18
py += 6
draw.text((px, py), "Looking:", fill=(40, 40, 60), font=body_f); py += 20
for ln in wrap(INFO["looking"], body_f, PANEL_W - 30):
    draw.text((px + 12, py), ln, fill=(60, 60, 60), font=body_f); py += 18
py += 12

draw.text((px, py), "WHAT'S VISIBLE", fill=(20, 20, 20), font=hdr_f); py += 26
for item in INFO["highlights"]:
    draw.ellipse([px + 4, py + 5, px + 10, py + 11], fill=(50, 110, 180))
    lines = wrap(item, body_f, PANEL_W - 60)
    for j, ln in enumerate(lines):
        draw.text((px + 18, py + j * 18), ln, fill=(40, 40, 40), font=body_f)
    py += max(18, 18 * len(lines)) + 6

# Color key (2 rows)
legend_y = PAD_T + ih + 32
draw.text((20, legend_y - 26), "Color key:", fill=(20, 20, 20), font=hdr_f)
row1 = [
    ((26, 21, 24), "Charcoal (cabinets, lockers)"),
    ((30, 76, 110), "Blue felt"),
    ((240, 237, 224), "White laminate (rounds + banquets)"),
    ((77, 10, 15), "Classroom chairs (burgundy)"),
]
row2 = [
    ((184, 184, 189), "Chrome (bar-stool footrest)"),
    ((50, 130, 70), "Service lane (green)"),
    ((10, 10, 10), "Doors / Stage (black)"),
]
for row_i, row in enumerate([row1, row2]):
    sx = 20
    ly = legend_y + row_i * 24
    for color, label in row:
        draw.rectangle([sx, ly - 2, sx + 20, ly + 18], fill=color, outline=(0, 0, 0))
        draw.text((sx + 26, ly), label, fill=(20, 20, 20), font=body_f)
        sx += 30 + draw.textbbox((0,0), label, font=body_f)[2] + 18

footer_lines = [
    "Ultra-wide 14mm framing gets the entire room in one shot: Emergency Exit foreground -> six pool tables -> classroom + rounds -> NW stage/lockers -> NE staff storage corner at upper right.",
    "v15L rev: round-table top now uses MAT_class_top (0.93, 0.91, 0.84) + MAT_class_bump T-mold edge, matching the folding banquet surface.",
    "All prior v15h/v15i/v15j/v15k geometry retained (pool tables, human figures, buffet, stage, lockers, booths, footrest ring).",
]
fy = new_h - 16 - 16 * len(footer_lines)
for fl in footer_lines:
    draw.text((20, fy), fl, fill=(90, 90, 90), font=tiny_f); fy += 16

canvas.save(DST, "PNG", optimize=True)
print(f"-> {DST}  size={canvas.size}")
