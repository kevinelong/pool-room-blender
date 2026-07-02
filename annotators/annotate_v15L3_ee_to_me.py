"""Annotate render_v15L3_persp_EE_to_ME.png — camera at Emergency Exit
looking SW along south wall toward Main Entry."""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC = "/tmp/blender_test/render_v15L3_persp_EE_to_ME.png"
DST = "/tmp/blender_test/render_v15L3_persp_EE_to_ME_annotated.png"

img = Image.open(SRC).convert("RGB")
W, H = img.size
draw = ImageDraw.Draw(img, "RGBA")

def get_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = get_font(38); F_MED = get_font(24); F_SM = get_font(20)

def label(xy, text, font=F_MED, fill=(255,255,255), bg=(0,0,0,180), pad=8, anchor="lt"):
    x, y = xy
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    if anchor == "lt":
        box = (x-pad, y-pad, x+tw+pad, y+th+pad*1.5); txt = (x,y)
    elif anchor == "rt":
        box = (x-tw-pad, y-pad, x+pad, y+th+pad*1.5); txt = (x-tw,y)
    elif anchor == "mt":
        box = (x-tw/2-pad, y-pad, x+tw/2+pad, y+th+pad*1.5); txt = (x-tw/2,y)
    draw.rounded_rectangle(box, radius=6, fill=bg)
    draw.text(txt, text, font=font, fill=fill)

def arrow(p1, p2, color=(255,220,80), width=3):
    draw.line([p1, p2], fill=color, width=width)
    x1,y1 = p1; x2,y2 = p2
    ang = math.atan2(y2-y1, x2-x1); hl = 14
    for da in (0.4, -0.4):
        hx = x2 - hl*math.cos(ang+da); hy = y2 - hl*math.sin(ang+da)
        draw.line([(x2,y2),(hx,hy)], fill=color, width=width)

# Title bar
draw.rectangle([(0,0),(W,72)], fill=(0,0,0,190))
draw.text((24,18), "Pool Room — v15L3 · Emergency Exit → Main Entry (view along south wall)",
          font=F_TITLE, fill=(255,255,255))

# Compass — camera stands near SE room corner (image-top-right on topdown)
# looking WEST/SW. So in this image, up is roughly UP (ceiling), depth is
# west along south wall. West = deeper in frame (into the image);
# North = to the left (behind the near table); South = to the right (curtain wall).
cx, cy, r = W-110, 150, 60
draw.rounded_rectangle([(W-200,80),(W-20,220)], radius=8, fill=(0,0,0,160))
# W arrow points into frame -> left in image (camera aim is roughly westward)
draw.line([(cx+r*0.4, cy),(cx-r+8, cy)], fill=(255,255,255), width=3)
draw.polygon([(cx-r+4, cy),(cx-r+18, cy-8),(cx-r+18, cy+8)], fill=(255,255,255))
draw.text((cx-r-18, cy-12), "W", font=F_MED, fill=(255,255,255))
draw.text((cx+r*0.5, cy-12), "E", font=F_SM, fill=(220,220,220))
# N up / S down (south wall is behind camera-right in this view; keep compass simple)
draw.text((cx-6, 90), "N", font=F_SM, fill=(220,220,220))
draw.text((cx-6, cy+r+4), "S", font=F_SM, fill=(220,220,220))
# camera arrow
arrow((cx+r*0.3, cy+r*0.5), (cx-r*0.4, cy-r*0.1), color=(255,220,80), width=3)
draw.text((cx+r*0.4, cy+r+4), "cam aim", font=F_SM, fill=(255,220,80))

# ---- Callouts ----
# Behind camera (out of frame) is Emergency Exit
label((30, 90), "Standing just inside\nEmergency Exit\n(S wall, east half)",
      font=F_SM, bg=(20,60,20,220))

# Main Entry — the small dark rectangle in the right side of the frame
# It's the door on the E wall south end (image-right side, at eye height)
me_door = (930, 300)
me_lbl = (760, 130)
arrow(me_lbl, me_door, color=(120,220,255), width=4)
label((me_lbl[0]-8, me_lbl[1]-4),
      "Main Entry\n(E wall, south end)",
      font=F_MED, fill=(200,240,255), bg=(20,50,80,220))

# South wall — receding down the length on image right
label((int(W*0.75), int(H*0.55)), "SOUTH wall (curtain)", font=F_MED,
      fill=(255,255,255), bg=(60,20,60,200))

# North side of frame (image left) — pool tables + service infrastructure
label((30, int(H*0.35)), "Pool tables\n(south-end pair)", font=F_MED)

# Cue on nearest table
cue_pt = (450, 380)
cue_lbl = (60, 500)
arrow(cue_lbl, cue_pt, color=(255,140,80), width=4)
label((cue_lbl[0]-8, cue_lbl[1]-4),
      "v15L3 cue on rest\n(tip on felt, butt above rail)",
      font=F_MED, fill=(255,220,180), bg=(80,30,10,200))

# Two-tops with patrons — mid frame
label((280, 180), "Two-tops along\neast service lane", font=F_SM,
      fill=(255,255,255), bg=(60,20,60,200))

# Service lane green band
label((int(W*0.45), int(H*0.72)), "East service lane", font=F_MED,
      fill=(20,20,20), bg=(210,255,210,220))

# Footer
draw.rectangle([(0,H-54),(W,H)], fill=(0,0,0,190))
draw.text((24, H-40),
          "v15L3 · Camera at Emergency Exit interior, 8 ft eye · aim SW along south wall toward Main Entry · 12 mm · exposure -0.7 · 2560×1440",
          font=F_SM, fill=(220,220,220))

img.save(DST, "PNG")
print(f"[annotate ee->me] wrote {DST}  ({os.path.getsize(DST)/1024:.1f} KB)")
