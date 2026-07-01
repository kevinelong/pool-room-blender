"""Annotate render_v15L3_topdown.png with descriptive callouts.
Orientation (fixed per user rule): image-top = SOUTH, image-bottom = NORTH,
image-right = EAST, image-left = WEST.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC = "/tmp/blender_test/render_v15L3_topdown.png"
DST = "/tmp/blender_test/render_v15L3_topdown_annotated.png"

img = Image.open(SRC).convert("RGB")
W, H = img.size
draw = ImageDraw.Draw(img, "RGBA")

def get_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = get_font(38); F_BIG = get_font(30); F_MED = get_font(26); F_SM = get_font(22)

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
    ang = math.atan2(y2-y1, x2-x1); hl = 16
    for da in (0.4, -0.4):
        hx = x2 - hl*math.cos(ang+da); hy = y2 - hl*math.sin(ang+da)
        draw.line([(x2,y2),(hx,hy)], fill=color, width=width)

# Title bar
title_h = 78
draw.rectangle([(0,0),(W,title_h)], fill=(0,0,0,190))
draw.text((24, 20), "Pool Room — v15L3 · Top-down", font=F_TITLE, fill=(255,255,255))

# Compass — image-top = SOUTH (per user fixed rule)
cx, cy, r = 90, 170, 60
draw.rounded_rectangle([(20, title_h+10), (180, title_h+150)], radius=8, fill=(0,0,0,160))
# S arrow up (since image-top = SOUTH)
draw.line([(cx,cy),(cx,cy-r+6)], fill=(255,255,255), width=3)
draw.polygon([(cx,cy-r+2),(cx-8,cy-r+16),(cx+8,cy-r+16)], fill=(255,255,255))
draw.text((cx-8, cy-r-24), "S", font=F_BIG, fill=(255,255,255))
# N arrow down
draw.line([(cx,cy),(cx,cy+r-6)], fill=(200,200,200), width=2)
draw.text((cx-8, cy+r), "N", font=F_SM, fill=(220,220,220))
# W left, E right
draw.text((cx-r-6, cy-12), "W", font=F_SM, fill=(220,220,220))
draw.text((cx+r-16, cy-12), "E", font=F_SM, fill=(220,220,220))

# Edge labels — SOUTH wall label positioned to avoid Main Entry / Emergency Exit callouts
label((W//2 - 100, title_h+90), "SOUTH wall",
      font=F_MED, anchor="mt")
label((W//2, H-52), "NORTH wall (stage · lockers · Storage A · Storage B)",
      font=F_MED, anchor="mt")
label((10, H//2), "WEST", font=F_BIG)
label((W-90, H//2), "EAST", font=F_BIG)

# Pool tables — 6 total, arrayed in three rows of two.
label((W//2 - 190, title_h+150), "6× Diamond 9-ft pool tables\nwest/east pairs, 3 rows",
      font=F_MED, anchor="lt")

# Banquet classroom area — center-lower half
label((W//2 - 130, int(H*0.72)), "Classroom banquet tables\n(6-ft rectangles + chairs)",
      font=F_MED, anchor="lt")

# Rounds — near bottom before stage
label((W//2 - 90, int(H*0.86)), "48\" folding rounds", font=F_MED, anchor="lt")

# Two-tops at east + west service lanes (highball tables with mannequins)
label((10, int(H*0.30)), "Two-tops along\nwest service lane", font=F_SM, bg=(60,20,60,200))
label((W-260, int(H*0.30)), "Two-tops along\neast service lane", font=F_SM, bg=(60,20,60,200))

# Doors (per fixed v15c placement rule)
# Main Entry — SE corner south wall (image top-right)
label((W-280, title_h+16), "Main Entry\n(SE corner)", font=F_SM, bg=(20,60,20,220))
# Emergency Exit — south wall east half (image top-center-right)
label((int(W*0.42), title_h+16), "Emergency Exit\n(S wall, east half)", font=F_SM, bg=(20,60,20,220))
# Storage A — north wall east end (image bottom-right)
label((W-260, H-90), "Storage A\n(N wall east end)", font=F_SM, bg=(20,60,20,220))
# Storage B — east wall north end (per fixed rule #4)
label((W-260, H-260), "Storage B\n(E wall north end)", font=F_SM, bg=(20,60,20,220))
# Kitchen door — east wall
label((W-260, int(H*0.62)), "Kitchen\n(E wall)", font=F_SM, bg=(20,60,20,220))

# Service lanes (green bands)
label((10, int(H*0.55)), "West lane", font=F_SM,
      fill=(20,20,20), bg=(180,255,180,220))
label((W-160, int(H*0.55)), "East lane", font=F_SM,
      fill=(20,20,20), bg=(180,255,180,220))

# Footer
draw.rectangle([(0,H-40),(W,H)], fill=(0,0,0,190))
draw.text((24, H-30),
          "v15L3 · cue tips on felt, butts above rail, 12\" inward · 1600×3200 ortho",
          font=F_SM, fill=(220,220,220))

img.save(DST, "PNG")
print(f"[annotate topdown] wrote {DST}  ({os.path.getsize(DST)/1024:.1f} KB)")
