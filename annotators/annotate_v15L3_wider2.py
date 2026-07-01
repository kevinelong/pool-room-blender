"""Annotate render_v15L3_persp_SW_lookNW_wider2.png with descriptive callouts."""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC = "/tmp/blender_test/render_v15L3_persp_SW_lookNW_wider2.png"
DST = "/tmp/blender_test/render_v15L3_persp_SW_lookNW_wider2_annotated.png"

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
draw.text((24,18), "Pool Room — v15L3 · SW corner, camera turned further NW (wider2)",
          font=F_TITLE, fill=(255,255,255))

# Compass in top-right
cx, cy, r = W-110, 150, 60
draw.rounded_rectangle([(W-200,80),(W-20,220)], radius=8, fill=(0,0,0,160))
draw.line([(cx,cy),(cx,cy-r+6)], fill=(255,255,255), width=3)
draw.polygon([(cx,cy-r+2),(cx-8,cy-r+16),(cx+8,cy-r+16)], fill=(255,255,255))
draw.text((cx-8, cy-r-18), "N", font=F_MED, fill=(255,255,255))
arrow((cx-r*0.6, cy+r*0.6), (cx-r*0.05, cy-r*0.55), color=(255,220,80), width=3)
draw.text((cx-r-8, cy+r-4), "cam", font=F_SM, fill=(255,220,80))

# Callouts
label((60, 380), "West wall\n(pool tables aligned to west side)", font=F_MED)
label((W//2 - 190, 300), "North wall\n(stage · lockers · Storage A)", font=F_MED)
label((W - 340, 340), "East wall behind curtain", font=F_MED)

# Cue callout — nearest table
cue_tip = (600, 660)
cue_lbl = (320, 720)
arrow(cue_lbl, cue_tip, color=(255,140,80), width=4)
label((cue_lbl[0]-8, cue_lbl[1]-4),
      "v15L3 cue on rest\n(tip on felt, butt above rail)",
      font=F_MED, fill=(255,220,180), bg=(80,30,10,200))

# Two-top + service lane
label((W-540, H-140), "Two-top w/ patron", font=F_MED)
label((W//2 + 60, H - 210), "East service lane\n(server path)", font=F_MED,
      fill=(20,20,20), bg=(210,255,210,220))

# Footer
draw.rectangle([(0,H-54),(W,H)], fill=(0,0,0,190))
draw.text((24, H-40),
          "v15L3 · 58\" tapered cue, tip on felt, butt above rail, 12\" inward · SW cam turned NW · exposure -0.9 · 2560×1440",
          font=F_SM, fill=(220,220,220))

img.save(DST, "PNG")
print(f"[annotate wider2] wrote {DST}  ({os.path.getsize(DST)/1024:.1f} KB)")
