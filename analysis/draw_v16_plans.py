#!/usr/bin/env python3
"""Draw the six v16 configuration plans as annotated top-down diagrams.

House orientation rule: image-top = high Y = SOUTH, image-right = high X =
EAST (matches every render and the original 2D diagram). Callouts are
descriptive only — no numeric position coordinates.

Each plan shows furniture, cue-swing zones, both service streams routed via
the east lane (cocktail from Main Entry, food from the kitchen door), and a
scorecard sidebar fed by analyze_config. Output: renders/plans/plan_v16_<key>.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from configs.v16_configs import (  # noqa: E402
    CONFIGS, ROOM_W, ROOM_L, BEAM_Y, ROUND_D, STAGE, BENCH, HVAC, LOCKERS,
    CLASSROOM, SERVICE_LANE_X, DOOR_MAIN, DOOR_KITCHEN, DOOR_EXIT,
    table_rect, playfield_rect, cue_zone, seat_positions,
)
from analysis.analyze_config import analyze, route, seg_hits_rect  # noqa: E402

S = 2.0                    # px per inch
MX, MTOP, MBOT = 50, 96, 46
PLAN_W, PLAN_H = int(ROOM_W * S), int(ROOM_L * S)
SIDEBAR = 470
W = MX * 2 + PLAN_W + SIDEBAR
H = MTOP + PLAN_H + MBOT

COL_FLOOR = (244, 241, 234)
COL_WALL = (60, 60, 64)
COL_LANE = (208, 240, 208)
COL_CUE = (255, 120, 120)
COL_TABLE = (90, 94, 100)
COL_FELT = (120, 180, 225)
COL_WOOD = (196, 160, 110)
COL_STAGE = (170, 150, 170)
COL_COCKTAIL = (150, 60, 200)
COL_FOOD = (235, 140, 40)
COL_CONFLICT = (220, 40, 40)


def fnt(size, bold=True):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(p, size)


F_TITLE, F_H, F_M, F_S = fnt(30), fnt(20), fnt(16), fnt(13, False)


def px(x):
    return MX + x * S


def py(y):
    return MTOP + (ROOM_L - y) * S     # image-top = SOUTH


def rect(d, r, **kw):
    x0, y0, x1, y1 = r
    d.rectangle([px(x0), py(y1), px(x1), py(y0)], **kw)


def draw_plan(cfg, score, clean=False, title=None, tagline=None):
    """clean=True: plan only — no scorecard sidebar, no numeric commentary."""
    width = MX * 2 + PLAN_W if clean else W
    img = Image.new("RGB", (width, H), (250, 250, 250))
    d = ImageDraw.Draw(img, "RGBA")

    # title bar
    d.rectangle([0, 0, width, 64], fill=(25, 25, 30))
    d.text((20, 10), title or f"Pool Room v16 — {cfg['name']}", font=F_TITLE,
           fill=(255, 255, 255))
    d.text((20, 44), tagline or cfg["tagline"], font=F_S, fill=(200, 200, 200))

    # floor + walls
    rect(d, (0, 0, ROOM_W, ROOM_L), fill=COL_FLOOR)
    # east service lane
    rect(d, (SERVICE_LANE_X[0], 60, SERVICE_LANE_X[1], ROOM_L - 60),
         fill=COL_LANE)
    # beam line
    d.line([px(0), py(BEAM_Y), px(ROOM_W), py(BEAM_Y)],
           fill=(150, 120, 90), width=3)
    d.text((px(6), py(BEAM_Y) - 20), "overhead beam", font=F_S,
           fill=(150, 120, 90))

    # cue zones under furniture
    rot = cfg.get("rot90", False)
    for _n, cx, yt in cfg["tables"]:
        rect(d, cue_zone(cx, yt, rot), fill=COL_CUE + (28,),
             outline=COL_CUE + (90,), width=1)

    # fixed elements
    stage_r = cfg.get("stage_rect", STAGE)
    rect(d, stage_r, fill=COL_STAGE)
    d.text((px(stage_r[0] + 12), py((stage_r[1] + stage_r[3]) / 2)),
           "stage", font=F_S, fill=(60, 40, 60))
    rect(d, LOCKERS, fill=(150, 150, 158))
    d.text((px(272), py(4) - 14), "lockers", font=F_S, fill=(70, 70, 78))
    rect(d, HVAC, fill=(190, 190, 196))
    d.text((px(289), py(366)), "hvac", font=F_S, fill=(90, 90, 96))
    if cfg.get("bench"):
        rect(d, BENCH, fill=COL_WOOD)
        d.text((px(160), py(6) - 14), "bench", font=F_S, fill=(90, 60, 20))
    if cfg.get("classroom"):
        rect(d, CLASSROOM, fill=(215, 205, 185), outline=(150, 130, 90))
        d.text((px(115), py(150)), "classroom", font=F_M, fill=(110, 90, 50))
    for bl in cfg.get("bleachers", []):
        rect(d, bl, fill=(180, 165, 200), outline=(120, 100, 150))
        x0, y0, x1, y1 = bl
        d.text((px(x0 + 4), py((y0 + y1) / 2)), "bleachers", font=F_S,
               fill=(80, 60, 110))

    # pool tables
    for name, cx, yt in cfg["tables"]:
        rect(d, table_rect(cx, yt, rot), fill=COL_TABLE)
        rect(d, playfield_rect(cx, yt, rot), fill=COL_FELT)

    # rounds / two-tops / high-tops / rails
    for cx, cy in cfg.get("rounds", []):
        r = ROUND_D / 2
        d.ellipse([px(cx - r), py(cy + r), px(cx + r), py(cy - r)],
                  fill=COL_WOOD, outline=(120, 90, 50))
    for cx, cy in cfg.get("twotops", []):
        d.rectangle([px(cx - 11), py(cy + 14), px(cx + 11), py(cy - 14)],
                    fill=(120, 80, 40))
    for cx, cy in cfg.get("hightops", []):     # standard 22x28 two-top
        d.rectangle([px(cx - 11), py(cy + 14), px(cx + 11), py(cy - 14)],
                    fill=(90, 60, 100), outline=(60, 40, 70))
    for x0, y0, x1, y1, _role in cfg.get("rails", []):
        d.line([px(x0), py(y0), px(x1), py(y1)], fill=(90, 60, 100), width=7)

    # doors
    for (dx0, dy0, dx1, dy1), col, lbl, anchor in (
            (DOOR_MAIN, COL_COCKTAIL, "MAIN ENTRY\n(cocktails in)", "right"),
            (DOOR_KITCHEN, COL_FOOD, "KITCHEN\n(food in)", "right"),
            (DOOR_EXIT, (200, 40, 40), "EMERGENCY EXIT", "top")):
        d.line([px(dx0), py(dy0), px(dx1), py(dy1)], fill=col, width=9)
        if anchor == "right":
            d.multiline_text((px(ROOM_W) - 12, py((dy0 + dy1) / 2) - 14),
                             lbl, font=F_S, fill=col, align="right",
                             anchor="ra")
        else:
            d.text((px((dx0 + dx1) / 2) - 62, py(dy0) + 12), lbl,
                   font=F_S, fill=col)

    # service routes: all-seat routes faint, farthest bold; conflict rings
    zones = [cue_zone(cx, yt, rot) for _n, cx, yt in cfg["tables"]]
    seats = seat_positions(cfg)
    for stream, door, kinds, col in (
            ("cocktail", DOOR_MAIN, ("drink", "flex"), COL_COCKTAIL),
            ("food", DOOR_KITCHEN, ("dine", "flex"), COL_FOOD)):
        targets = [(x, y) for k, x, y in seats if k in kinds]
        if not targets:
            continue
        lane_x = cfg.get("lane_x")
        kw = {"lane_x": lane_x} if lane_x else {}
        far = max(targets, key=lambda t: route(door, t, **kw)[1])
        for t in targets:
            pts, _ = route(door, t, **kw)
            xy = [c for p in pts for c in (px(p[0]), py(p[1]))]
            bold = (t == far)
            d.line(xy, fill=col + (255 if bold else 60,),
                   width=5 if bold else 2)
            hit = any(seg_hits_rect(pts[i], pts[i + 1], z)
                      for i in range(len(pts) - 1) for z in zones)
            if hit:
                d.ellipse([px(t[0]) - 9, py(t[1]) - 9,
                           px(t[0]) + 9, py(t[1]) + 9],
                          outline=COL_CONFLICT, width=3)

    # room outline on top
    d.rectangle([px(0), py(ROOM_L), px(ROOM_W), py(0)],
                outline=COL_WALL, width=5)

    # compass (top-right of plan area)
    cxp, cyp = MX + 44, MTOP + 40
    d.ellipse([cxp - 30, cyp - 30, cxp + 30, cyp + 30],
              fill=(25, 25, 30, 220))
    d.text((cxp - 6, cyp - 27), "S", font=F_S, fill=(255, 255, 255))
    d.text((cxp - 6, cyp + 12), "N", font=F_S, fill=(255, 255, 255))
    d.text((cxp + 14, cyp - 8), "E", font=F_S, fill=(255, 255, 255))
    d.text((cxp - 26, cyp - 8), "W", font=F_S, fill=(255, 255, 255))

    if clean:
        # legend only (no numbers anywhere)
        ly = H - MBOT + 6
        d.line([MX, ly + 10, MX + 30, ly + 10], fill=COL_COCKTAIL, width=5)
        d.text((MX + 36, ly), "cocktail service", font=F_S, fill=(60, 60, 60))
        d.line([MX + 190, ly + 10, MX + 220, ly + 10], fill=COL_FOOD, width=5)
        d.text((MX + 226, ly), "food service", font=F_S, fill=(60, 60, 60))
        d.rectangle([MX + 360, ly + 2, MX + 378, ly + 18],
                    fill=COL_CUE + (60,), outline=COL_CUE)
        d.text((MX + 384, ly), "cue-swing zone", font=F_S, fill=(60, 60, 60))
        return img

    # sidebar scorecard
    sx = MX * 2 + PLAN_W - 10
    d.rectangle([sx, 80, W - 16, H - 20], fill=(32, 32, 38))
    ty = 96
    cap = score["capacity"]

    def row(label, val, col=(255, 255, 255)):
        nonlocal ty
        d.text((sx + 18, ty), label, font=F_M, fill=(170, 170, 180))
        d.text((sx + 260, ty), str(val), font=F_H, fill=col)
        ty += 32

    d.text((sx + 18, ty), "SCORECARD", font=F_H, fill=(255, 220, 80))
    ty += 40
    row("Pool tables", cap["tables"])
    row("Player positions", cap["players"])
    row("Spectator seats", cap["spectators"])
    row("Drink positions", cap["drink"])
    row("Dining covers", cap["dine"])
    row("Flex seats", cap["flex"])
    ty += 10
    cue = score["cue"]
    col = ((120, 230, 120) if cue["full_pct"] >= 95 else
           (255, 210, 90) if cue["full_pct"] >= 80 else (255, 120, 120))
    row("Full cue swing", f"{cue['full_pct']}% of sides", col)
    row("Tightest swing", f"{cue['min_clearance_in']}\"", col)
    ty += 10
    svc = score["service"]
    row("Cocktail run (max)", f"{svc['cocktail']['max_run_ft']} ft"
        if svc["cocktail"]["seats"] else "n/a")
    row("Food run (max)", f"{svc['food']['max_run_ft']} ft"
        if svc["food"]["seats"] else "n/a")
    nconf = (svc["cocktail"]["conflicted_seats"]
             + svc["food"]["conflicted_seats"])
    row("Service x cue conflicts", nconf,
        (120, 230, 120) if nconf == 0 else (255, 120, 120))
    ty += 10
    egr = score["egress"]
    ok = egr["exit_corridor_ok"]
    row("Exit corridor", f"{egr['exit_corridor_in']}\" clear",
        (120, 230, 120) if ok else (255, 80, 80))
    row("Worst egress walk", f"{egr['worst_travel_ft']} ft")
    ty += 10
    row("Revenue proxy", f"${score['revenue_proxy_hr']}/hr", (255, 220, 80))
    row("Flip cost", f"{score['flip_minutes']} min")

    ty += 16
    d.text((sx + 18, ty), "TRADE-OFFS", font=F_H, fill=(255, 220, 80))
    ty += 34
    import textwrap
    for note in score["notes"]:
        for li, line in enumerate(textwrap.wrap(note, 42)):
            d.text((sx + 18 + (0 if li == 0 else 14), ty),
                   ("• " if li == 0 else "") + line, font=F_S,
                   fill=(220, 220, 225))
            ty += 20
        ty += 8

    # legend + footer
    ly = H - MBOT + 6
    d.line([MX, ly + 10, MX + 30, ly + 10], fill=COL_COCKTAIL, width=5)
    d.text((MX + 36, ly), "cocktail service", font=F_S, fill=(60, 60, 60))
    d.line([MX + 190, ly + 10, MX + 220, ly + 10], fill=COL_FOOD, width=5)
    d.text((MX + 226, ly), "food service", font=F_S, fill=(60, 60, 60))
    d.rectangle([MX + 360, ly + 2, MX + 378, ly + 18],
                fill=COL_CUE + (60,), outline=COL_CUE)
    d.text((MX + 384, ly), "cue-swing zone", font=F_S, fill=(60, 60, 60))
    d.ellipse([MX + 530, ly + 2, MX + 546, ly + 18],
              outline=COL_CONFLICT, width=3)
    d.text((MX + 552, ly), "service crosses cue zone", font=F_S,
           fill=(60, 60, 60))
    return img


def main():
    outdir = os.path.join(HERE, "..", "renders", "plans")
    os.makedirs(outdir, exist_ok=True)
    for cfg in CONFIGS:
        score = analyze(cfg)
        img = draw_plan(cfg, score)
        path = os.path.join(outdir, f"plan_v16_{cfg['key']}.png")
        img.save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
