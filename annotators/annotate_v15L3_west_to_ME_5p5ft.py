"""Annotate west-side-looking-at-Main-Entry render.
Camera at west-side south-end interior, aiming east directly at Main Entry.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC = "/tmp/blender_test/render_v15L3_persp_west_to_ME_5p5ft.png"
DST = "/tmp/blender_test/render_v15L3_persp_west_to_ME_5p5ft_annotated.png"

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
draw.text((24,18), "Pool Room — v15L3 · West-side south end, aim EAST at Main Entry · eye 5.5 ft",
          font=F_TITLE, fill=(255,255,255))

# Compass — camera stands at south end west side, looking EAST (deeper in frame)
cx, cy, r = W-110, 150, 60
draw.rounded_rectangle([(W-200,80),(W-20,220)], radius=8, fill=(0,0,0,160))
# E arrow points into frame (right)
draw.line([(cx-r*0.4, cy),(cx+r-8, cy)], fill=(255,255,255), width=3)
draw.polygon([(cx+r-4, cy),(cx+r-18, cy-8),(cx+r-18, cy+8)], fill=(255,255,255))
draw.text((cx+r+4, cy-12), "E", font=F_MED, fill=(255,255,255))
draw.text((cx-r-18, cy-12), "W", font=F_SM, fill=(220,220,220))
draw.text((cx-6, 90), "N", font=F_SM, fill=(220,220,220))
draw.text((cx-6, cy+r+4), "S", font=F_SM, fill=(220,220,220))
arrow((cx-r*0.3, cy+r*0.5), (cx+r*0.4, cy-r*0.1), color=(255,220,80), width=3)
draw.text((cx-r*0.4-40, cy+r+4), "cam aim", font=F_SM, fill=(255,220,80))

# Main Entry door — the tall dark rectangle mid-frame (E wall, south end)
# Door center at approx (1145, 820) in 2560×1440 image coords
me_door = (1145, 820)
me_lbl = (300, 760)
arrow(me_lbl, me_door, color=(120,220,255), width=5)
label((me_lbl[0]-8, me_lbl[1]-4),
      "Main Entry\n(E wall, south end)",
      font=F_MED, fill=(200,240,255), bg=(20,50,80,220))

# Emergency Exit — south wall east half; it's BEHIND camera in this view.
label((30, 400),
      "Emergency Exit is\nBEHIND camera\n(S wall, east half)",
      font=F_SM, fill=(255,220,220), bg=(80,20,20,220))

# South wall runs along image-LEFT (camera aims east; south is to camera's
# left because aim direction is +X so left = +Y = SOUTH).
label((30, int(H*0.60)), "SOUTH wall\n(curtain, image-left)", font=F_SM,
      fill=(255,255,255), bg=(60,20,60,200))

# North-side (interior receding)
label((int(W*0.45), 180), "NORTH direction\n(interior receding)", font=F_SM, bg=(0,0,0,180))

# East service lane
label((int(W*0.40), int(H*0.88)), "East service lane\n(green strip)", font=F_SM,
      fill=(20,20,20), bg=(210,255,210,220))

# Two-tops
label((int(W*0.72), int(H*0.45)), "Two-tops w/ patrons\n(east service lane)", font=F_SM,
      fill=(255,255,255), bg=(60,20,60,200))

# Pool tables — foreground
label((int(W*0.55), int(H*0.92)), "Pool tables\n(south row)", font=F_MED)

# Camera position note (top-left)
label((30, 90), "Standing at south-end\nWEST side, aiming EAST\n(5.5 ft eye height)",
      font=F_SM, bg=(20,60,20,220))

# Footer
draw.rectangle([(0,H-54),(W,H)], fill=(0,0,0,190))
draw.text((24, H-40),
          "v15L3 · Cam at south-end west side · aim EAST at Main Entry · eye 5.5 ft · 14 mm · exposure -0.7 · 2560×1440",
          font=F_SM, fill=(220,220,220))

img.save(DST, "PNG")
print(f"[annotate west->ME] wrote {DST}  ({os.path.getsize(DST)/1024:.1f} KB)")
