"""Annotate render_topdown_v15h.png - v15h pool tables fully rebuilt to
match authentic Diamond Pro-Am 7ft Charcoal cabinet (54x94, wedge corner
caps, square tapered legs, charcoal Dymondwood, diamond sights, pocket
throats, ball-return apron). Researched from manufacturer photos. NO
numeric position coords."""
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/user/workspace/render_topdown_v15L2.png"
DST = "/home/user/workspace/render_topdown_v15L2_annotated.png"

img = Image.open(SRC).convert("RGB")
img_w, img_h = img.size

PAD_L, PAD_R, PAD_T, PAD_B = 440, 540, 150, 340
new_w, new_h = img_w + PAD_L + PAD_R, img_h + PAD_T + PAD_B
canvas = Image.new("RGB", (new_w, new_h), (250, 250, 250))
canvas.paste(img, (PAD_L, PAD_T))
draw = ImageDraw.Draw(canvas)

F = lambda sz, b=False: ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b
    else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
title_f, subt_f = F(22, True), F(14)
hdr_f, lbl_f = F(14, True), F(13, True)
val_f, dim_f, tiny_f = F(12), F(12, True), F(12)

ROOM_W, ROOM_L = 316.0, 682.0
PX = img_h / (ROOM_L * 1.05)
def w2i(wx, wy):
    return (PAD_L + img_w/2 + (wx - ROOM_W/2) * PX,
            PAD_T + img_h/2 - (wy - ROOM_L/2) * PX)

# Title
title1 = "Pool Room - v15L Top-Down (round stacking tables + lockers + folding banquets + bar-stool footrests + black-vinyl booths)"
title2 = "v15L (rev): round tables now share the classroom (folding banquet) surface - same off-white laminate top + cream T-mold bullnose ring around the edge. Chrome splayed legs and X-brace retained."
tw1 = draw.textbbox((0,0), title1, font=title_f)[2]
tw2 = draw.textbbox((0,0), title2, font=subt_f)[2]
draw.text(((new_w - tw1)/2, 14), title1, fill=(20, 20, 20), font=title_f)
draw.text(((new_w - tw2)/2, 44), title2, fill=(70, 70, 70), font=subt_f)
sub2 = '316" x 682"  |  6 pool tables  |  4 folding banquets (2x2) + 2 round stacking tables  |  buffet on E wall  |  two-tops  |  NW stage w/ lockers  |  3 black-vinyl booths  |  5 doors'
stw = draw.textbbox((0,0), sub2, font=tiny_f)[2]
draw.text(((new_w - stw)/2, 70), sub2, fill=(100, 100, 100), font=tiny_f)

# Overall dimensions
ax = PAD_L - 30
top_y, bot_y = PAD_T + 5, PAD_T + img_h - 5
draw.line([(ax, top_y), (ax, bot_y)], fill=(40, 40, 40), width=2)
for y_e, dy in [(top_y, 1), (bot_y, -1)]:
    draw.polygon([(ax, y_e), (ax - 5, y_e + 10*dy), (ax + 5, y_e + 10*dy)], fill=(40, 40, 40))
txt = "Room length  682\"  (56'-10\")"
tw, th = draw.textbbox((0,0), txt, font=dim_f)[2:]
t_img = Image.new("RGBA", (tw + 6, th + 4), (250, 250, 250, 255))
ImageDraw.Draw(t_img).text((3, 2), txt, fill=(20, 20, 20), font=dim_f)
t_img = t_img.rotate(90, expand=True)
canvas.paste(t_img, (ax - 25 - t_img.width//2, (top_y + bot_y)//2 - t_img.height//2), t_img)

ay = PAD_T - 20
lx, rx = PAD_L + 5, PAD_L + img_w - 5
draw.line([(lx, ay), (rx, ay)], fill=(40, 40, 40), width=2)
for x_e, dx in [(lx, 1), (rx, -1)]:
    draw.polygon([(x_e, ay), (x_e + 10*dx, ay - 5), (x_e + 10*dx, ay + 5)], fill=(40, 40, 40))
draw.text(((lx + rx)/2 - 90, ay - 30), "Room width  316\"  (26'-4\")",
          fill=(20, 20, 20), font=dim_f)

# Door labels (outside the floor plan)
def text_blk(x, y, hdr, sub, hdr_col=(20,20,20), sub_col=(80,80,80)):
    draw.text((x, y), hdr, fill=hdr_col, font=hdr_f)
    draw.text((x, y + 16), sub, fill=sub_col, font=val_f)

sb_ix, sb_iy = w2i(316, 22)
text_blk(PAD_L + img_w + 6, sb_iy - 8, "STORAGE B", "(E wall, NE corner)")
draw.line([(PAD_L + img_w, sb_iy), (PAD_L + img_w + 4, sb_iy)], fill=(80, 80, 80), width=2)

k_ix, k_iy = w2i(316, 310)
text_blk(PAD_L + img_w + 6, k_iy - 8, "KITCHEN", "(N of HVAC)")
draw.line([(PAD_L + img_w, k_iy), (PAD_L + img_w + 4, k_iy)], fill=(80, 80, 80), width=2)

me_ix, me_iy = w2i(316, 647)
text_blk(PAD_L + img_w + 6, me_iy - 8, "MAIN ENTRY (bar)", "railed stairs land here")
draw.line([(PAD_L + img_w, me_iy), (PAD_L + img_w + 4, me_iy)], fill=(80, 80, 80), width=2)

sa_ix, sa_iy = w2i(294, 0)
draw.text((sa_ix - 35, PAD_T + img_h + 4), "STORAGE A", fill=(20, 20, 20), font=hdr_f)
draw.text((sa_ix - 55, PAD_T + img_h + 20), "(N wall, NE corner)", fill=(80, 80, 80), font=val_f)
draw.line([(sa_ix, PAD_T + img_h), (sa_ix, PAD_T + img_h + 2)], fill=(80, 80, 80), width=2)

ee_ix, ee_iy = w2i(253.5, 682)
draw.text((ee_ix - 60, PAD_T - 60), "EMERGENCY EXIT", fill=(15, 100, 25), font=hdr_f)
draw.line([(ee_ix, PAD_T - 28), (ee_ix, PAD_T)], fill=(15, 100, 25), width=2)

# Pool table labels
POOL = [("Table 1\n(Back L)", 105, 283.5),
        ("Table 2\n(Back R)", 211, 283.5),
        ("Table 3\n(Main A-L)", 105, 434.5),
        ("Table 4\n(Main A-R)", 211, 434.5),
        ("Table 5\n(Main B-L)", 105, 579.5),
        ("Table 6\n(Main B-R)", 211, 579.5)]
for label, cx, cy in POOL:
    ix, iy = w2i(cx, cy)
    for k, ln in enumerate(label.split("\n")):
        bw = draw.textbbox((0,0), ln, font=lbl_f)[2]
        draw.text((ix - bw/2, iy - 12 + k*14), ln, fill=(20, 20, 60), font=lbl_f)

def callout(text_lines, anchor_world, side="right", offset=(0, 0),
            color=(255, 247, 200), border=(120, 100, 30),
            text_color=(20, 20, 20), font=lbl_f):
    ax_w, ay_w = anchor_world
    ax_i, ay_i = w2i(ax_w, ay_w)
    lines = text_lines if isinstance(text_lines, list) else [text_lines]
    line_h = font.size + 4
    pad = 6
    widths = [draw.textbbox((0,0), ln, font=font)[2] for ln in lines]
    tw = max(widths) + 2*pad
    th = line_h * len(lines) + 2*pad
    if side == "right":
        bx, by = PAD_L + img_w + 130 + offset[0], ay_i - th/2 + offset[1]
    elif side == "left":
        bx, by = PAD_L - tw - 20 + offset[0], ay_i - th/2 + offset[1]
    elif side == "above":
        bx, by = ax_i - tw/2 + offset[0], ay_i - th - 30 + offset[1]
    else:
        bx, by = ax_i - tw/2 + offset[0], ay_i + 30 + offset[1]
    bx = max(4, min(bx, new_w - tw - 4))
    by = max(4, min(by, new_h - th - 4))
    if side == "right": lp = (bx, by + th/2)
    elif side == "left": lp = (bx + tw, by + th/2)
    elif side == "above": lp = (bx + tw/2, by + th)
    else: lp = (bx + tw/2, by)
    draw.line([lp, (ax_i, ay_i)], fill=(110, 90, 30), width=1)
    draw.ellipse([ax_i-3, ay_i-3, ax_i+3, ay_i+3], fill=(180, 30, 30))
    draw.rectangle([bx, by, bx+tw, by+th], fill=color, outline=border, width=1)
    for i, ln in enumerate(lines):
        draw.text((bx+pad, by+pad+i*line_h), ln, fill=text_color, font=font)

# --- v15L callouts ---

# RIGHT SIDE (east wall area)
callout(["NE-CORNER STORAGE DOORS",
         "Storage A on N wall (east end)",
         "Storage B on E wall (north end)"],
        anchor_world=(308, 18), side="right", offset=(0, 80),
        color=(225, 225, 235), border=(80, 80, 100))

callout(["POOL TABLES (v15h/v15i, 7ft)",
         "Diamond Pro-Am style, 53.5x92.5,",
         "charcoal cabinets, 7.25\" K-66",
         "rails, wedge corner caps, square",
         "tapered legs, diamond sights,",
         "ball-return apron slots"],
        anchor_world=(215, 283), side="right", offset=(0, 0),
        color=(225, 230, 240), border=(40, 50, 80))

callout(["HOTEL BUFFET (v15f, retained)",
         "banquet skirt + tablecloth",
         "+ 2 coffee urns, creamer/sugar,",
         "tea, cups, vases, placards"],
        anchor_world=(307, 193), side="right", offset=(0, 240),
        color=(255, 245, 220), border=(170, 130, 40))

callout(["TWO-TOPS (v15e/v15j, retained)",
         "rounded dark-walnut tops on",
         "matte-black pedestals, pub bar",
         "stools with chrome footrest ring"],
        anchor_world=(304, 540), side="right", offset=(0, 0),
        color=(230, 245, 235), border=(40, 110, 70))

# LEFT SIDE (west wall area)
callout(["WEST TWO-TOPS (v15e/v15j, retained)",
         "pedestal base + pub bar stools",
         "with chrome footrest ring;",
         "chair spacing 2\" from table"],
        anchor_world=(8, 434), side="left", offset=(0, 0),
        color=(225, 235, 250), border=(50, 80, 140))

callout(["Partition beam"],
        anchor_world=(170, 332), side="left", offset=(0, 0),
        color=(225, 225, 225), border=(80, 80, 80))

callout(["FOLDING BANQUET CLASSROOM (v15k)",
         "4 white-laminate folding banquets",
         "in a 2x2 grid (Row 2 removed for",
         "round tables); black tubular",
         "H-frame legs + cross stretcher;",
         "burgundy padded stacking chairs"],
        anchor_world=(56, 130), side="left", offset=(0, 0),
        color=(255, 230, 230), border=(140, 30, 30))

callout(["30\" SERVICE LANES (unchanged)",
         "green band shows minimum",
         "lane clearance around all",
         "furniture & walls"],
        anchor_world=(20, 85), side="left", offset=(0, 80),
        color=(220, 240, 230), border=(40, 120, 80))

callout(["NW STAGE + LOCKERS (v15k)",
         "4'x8'x1' matte-black stage,",
         "ball locker (24W, 3-zone with",
         "balls display) + triple locker",
         "(36W, 3 vertical doors) both",
         "72H x 18D against back wall"],
        anchor_world=(60, 24), side="left", offset=(0, 200),
        color=(255, 235, 205), border=(170, 100, 30))

callout(["HVAC chase"],
        anchor_world=(302, 359), side="right", offset=(0, -120),
        color=(235, 235, 235), border=(80, 80, 80))

# v15h HUMAN FIGURES (combined)
callout(["HUMAN FIGURES (v15h, retained)",
         "3 standing pool players (BackL,",
         "MainAR, MainBL) holding cues in",
         "bridge stance; 1 seated patron",
         "per two-top (6 total)"],
        anchor_world=(80, 434), side="left", offset=(0, 240),
        color=(255, 225, 235), border=(180, 40, 100))

# --- v15L / v15k NEW FEATURE CALLOUTS ---

callout(["ROUND STACKING TABLES (v15L rev)",
         "2 folding rounds, 48\" dia;",
         "TOP + EDGE now match classroom",
         "folding banquet: same off-white",
         "laminate + cream T-mold bullnose",
         "ring around the edge; chrome",
         "splayed legs + black foot caps",
         "+ X cross-brace under; 4 chairs",
         "per table fanned across south",
         "half; between stage and Storage",
         "A door; REPLACES back row of",
         "classroom"],
        anchor_world=(228, 48), side="right", offset=(0, -60),
        color=(240, 240, 245), border=(90, 90, 110))

callout(["BLACK-VINYL BOOTHS (v15k, NEW)",
         "3 channel-tufted booth sections",
         "REPLACE the plain bench along N",
         "wall; ~55W each, 30\" tall backs,",
         "5 vertical shadow grooves per",
         "section, matte-black plinth base"],
        anchor_world=(186, 9), side="right", offset=(0, 60),
        color=(230, 230, 230), border=(60, 60, 60))

callout(["BAR-STOOL FOOTREST RING (v15k, NEW)",
         "4 chrome cross-bars at 4\" off",
         "floor between the 4 legs of each",
         "pub bar stool at the two-tops",
         "(SketchUp Bar Stool reference)"],
        anchor_world=(310, 470), side="right", offset=(0, 140),
        color=(240, 245, 250), border=(80, 100, 140))

# Color key
legend_y = new_h - PAD_B + 170
draw.text((PAD_L, legend_y), "Color key:", fill=(20, 20, 20), font=hdr_f)
swatches = [
    ((26, 21, 24), "Charcoal cabinet"),
    ((30, 76, 110), "Blue felt"),
    ((240, 237, 224), "White laminate (round/banquet tops)"),
    ((184, 184, 189), "Chrome legs / footrest"),
    ((8, 8, 9), "Black vinyl (booths)"),
    ((242, 237, 219), "Buffet skirt (cream)"),
    ((0, 200, 60), "30\" service lanes"),
]
sx = PAD_L + 80
for color, label in swatches:
    draw.rectangle([sx, legend_y-2, sx+18, legend_y+16], fill=color, outline=(0, 0, 0))
    draw.text((sx+24, legend_y), label, fill=(20, 20, 20), font=val_f)
    sx += 26 + draw.textbbox((0,0), label, font=val_f)[2] + 18

footer = "v15L: 2 round STACKING FOLDING TABLES (48\" dia, white laminate top, chrome splayed legs, black feet caps, X-brace under) between stage and Storage A per SketchUp reference. Back row of classroom removed to make space. Classroom tables now FOLDING BANQUETS (white laminate, black tubular H-frame legs, cross stretcher). 3 BLACK-VINYL BOOTHS with tall channel-tufted backs replace the plain bench. Bar stools gain a 4-bar chrome FOOTREST RING at 4\" off floor. Lockers rebuilt to real dimensions: 1 BALL locker (24W, 3-zone with balls display) + 1 TRIPLE locker (36W, 3 vertical doors + vents)."
footer_w = draw.textbbox((0,0), footer, font=tiny_f)[2]
draw.text(((new_w - footer_w) / 2, new_h - 28), footer, fill=(80, 80, 80), font=tiny_f)

canvas.save(DST, "PNG", optimize=True)
print(f"Annotated -> {DST}  size={canvas.size}")
