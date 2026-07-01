"""Annotate render_v15L3_persp_SW_lookNW_wider.png with descriptive callouts.
Per persistent rules:
  1. Annotate every render similar to initial 2d diagram
  2. Strip ALL numeric position coords from callouts. Descriptive only.
"""
from PIL import Image, ImageDraw, ImageFont
import os

SRC = "/tmp/blender_test/render_v15L3_persp_SW_lookNW_wider.png"
DST = "/tmp/blender_test/render_v15L3_persp_SW_lookNW_wider_annotated.png"

img = Image.open(SRC).convert("RGB")
W, H = img.size
draw = ImageDraw.Draw(img, "RGBA")

# Fonts — fall back to default if DejaVu missing
def get_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = get_font(38)
F_BIG   = get_font(30)
F_MED   = get_font(24)
F_SM    = get_font(20)

def label(xy, text, font=F_MED, fill=(255,255,255), bg=(0,0,0,180), pad=8, anchor="lt"):
    x, y = xy
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    if anchor == "lt":
        box = (x-pad, y-pad, x+tw+pad, y+th+pad*1.5)
        txt = (x, y)
    elif anchor == "rt":
        box = (x-tw-pad, y-pad, x+pad, y+th+pad*1.5)
        txt = (x-tw, y)
    elif anchor == "mt":
        box = (x-tw/2-pad, y-pad, x+tw/2+pad, y+th+pad*1.5)
        txt = (x-tw/2, y)
    draw.rounded_rectangle(box, radius=6, fill=bg)
    draw.text(txt, text, font=font, fill=fill)

def arrow(p1, p2, color=(255,220,80), width=3):
    draw.line([p1, p2], fill=color, width=width)
    # arrow head
    import math
    x1,y1 = p1; x2,y2 = p2
    ang = math.atan2(y2-y1, x2-x1)
    hl = 14
    for da in (0.4, -0.4):
        hx = x2 - hl*math.cos(ang+da)
        hy = y2 - hl*math.sin(ang+da)
        draw.line([(x2,y2),(hx,hy)], fill=color, width=width)

# ---------------- TITLE BAR ----------------
title_bg = (0,0,0,190)
draw.rectangle([(0,0),(W,72)], fill=title_bg)
draw.text((24, 18), "Pool Room — v15L3 · SW corner view, camera turned NW (wider/lefter)",
          font=F_TITLE, fill=(255,255,255))

# ---------------- Compass mini-diagram in top-right ----------------
# View orientation: camera stands at SW corner interior looking NNW toward
# the far (north) wall. Image left ~= west wall (down the length), image
# right ~= north-half of east wall, image far center = NORTH.
cx, cy, r = W-110, 150, 60
draw.rounded_rectangle([(W-200,80),(W-20,220)], radius=8, fill=(0,0,0,160))
# N up
draw.line([(cx,cy),(cx,cy-r+6)], fill=(255,255,255), width=3)
draw.polygon([(cx,cy-r+2),(cx-8,cy-r+16),(cx+8,cy-r+16)], fill=(255,255,255))
draw.text((cx-8, cy-r-18), "N", font=F_MED, fill=(255,255,255))
# camera arrow (from SW towards NNW/N inside compass box)
arrow((cx-r*0.6, cy+r*0.6), (cx-r*0.15, cy-r*0.5), color=(255,220,80), width=3)
draw.text((cx-r-8, cy+r-4), "cam", font=F_SM, fill=(255,220,80))

# ---------------- Descriptive callouts ----------------
# Left / west wall (dominates image left half): pool table row on west side
label((60, 420), "West wall\n(pool tables aligned to west side)", font=F_MED)

# Far center / north (upper middle): stage area, then lockers, then Storage A
label((W//2 - 180, 260), "North wall\n(stage · lockers · Storage A)", font=F_MED, anchor="lt")

# Right / east (behind curtains, partial): east wall receding
label((W - 380, 340), "East wall (receding)\ncurtain/beam obstruction", font=F_MED)

# Foreground cue — highlight one visible cue on nearest table
# The nearest table's cue is around lower-left / lower-center
cue_tip = (620, 640)
cue_lbl = (330, 720)
arrow(cue_lbl, cue_tip, color=(255,140,80), width=4)
label((cue_lbl[0]-8, cue_lbl[1]-4),
      "v15L3 cue on rest\n(tip on felt, butt above rail)",
      font=F_MED, fill=(255,220,180), bg=(80,30,10,200))

# Two-top table with mannequin (right foreground) — service lane clearance
label((W-560, H-160), "Two-top w/ patron\nalong east service lane", font=F_MED)

# Service lane (bright floor strip running down center)
label((W//2 + 40, H - 220), "East service lane\n(server path)", font=F_MED,
      fill=(20,20,20), bg=(210,255,210,220))

# ---------------- Footer ----------------
foot_h = 54
draw.rectangle([(0,H-foot_h),(W,H)], fill=(0,0,0,190))
draw.text((24, H-foot_h+14),
          "v15L3 geometry: 58\" tapered cue, tip=felt, butt above rail, 12\" inward shift · SW cam turned NW · 2560×1440",
          font=F_SM, fill=(220,220,220))

img.save(DST, "PNG")
print(f"[annotate] wrote {DST}  ({os.path.getsize(DST)/1024:.1f} KB)")
