#!/usr/bin/env python3
"""Build docs/index.html — a single-file first-person walkthrough of every
layout (Wolfenstein-style), with a landing gallery of all layouts (letter +
short name + ONE overhead render each; no 3-D views on the gallery).

Default behaviour: an auto-tour walks in from the Main Entrance, loops the
room, walks back out, fades, and proceeds to the next layout — through all
layouts and back to the top, forever. Click the canvas for manual WASD +
mouse-look control; Esc resumes the tour. Everything (engine, geometry,
tour paths, thumbnails) is embedded — no external requests.
"""
import base64
import heapq
import io
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import (  # noqa: E402
    CONFIGS, ROOM_W, ROOM_L, BEAM_Y, HVAC, ENTRY_WELL, table_rect,
    tbl_rot,
)
sys.path.insert(0, HERE)
from project_urls import DOWNLOAD_URL, DECK_URL  # noqa: E402

# fallback only — configs carry letter/short as canonical fields (v39
# letters follow the semantic page order: left, centered, right)
SHORT = {
    "turnleft":     ("A", "left 4+2"),
    "gridleft":     ("B", "left 2×3"),
    "gridleftturn": ("C", "left 2×3 turn"),
    "westline":     ("D", "west 1×6"),
    "westshift":    ("E", "west 1×6 low"),
    "social":       ("F", "center 2×3"),
    "fourturned":   ("G", "center 4+2"),
    "gridwide":     ("H", "center 2×3 wide"),
    "gridbal":      ("I", "center 2×3 bal"),
    "centerline":   ("J", "center 1×6"),
    "centershift":  ("K", "center 1×6 low"),
    "turnright":    ("L", "right 4+2"),
    "eastline":     ("M", "east 1×6"),
    "eastshift":    ("N", "east 1×6 low"),
}


def thumb_data_uri(key):
    # v42: higher-res so the same embedded image doubles as a decent
    # downloadable overhead (cards downscale it via CSS)
    p = os.path.join(ROOT, "renders", f"render_v16_{key}_topdown.png")
    im = Image.open(p).convert("RGB")
    im.thumbnail((720, 1440))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=76)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def file_data_uri(relpath, mime):
    fp = os.path.join(ROOT, relpath)
    if not os.path.exists(fp):
        return None
    with open(fp, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


def chairs_for(cx, cy, plus):
    """Chair (center_x, center_y, yaw_deg) — mirrors the render driver."""
    base = [(cx, cy - 40.0, 0), (cx, cy + 40.0, 180),
            (cx - 39.5, cy, 90), (cx + 39.5, cy, 270)]
    if plus:
        return base
    out = []
    c45, s45 = math.cos(math.pi / 4), math.sin(math.pi / 4)
    for bx, by, yaw in base:
        dx, dy = bx - cx, by - cy
        out.append((cx + dx * c45 - dy * s45, cy + dx * s45 + dy * c45,
                    yaw + 45))
    return out


def obstacle_rects(cfg):
    """Collision rects (also the A* occupancy source)."""
    obs = [table_rect(tx, ty, tbl_rot(cfg, _n))
           for _n, tx, ty in cfg["tables"]]
    for cx, cy in cfg.get("rounds", []):
        obs.append((cx - 36, cy - 36, cx + 36, cy + 36))
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        obs.append((hx - 14, hy - 27, hx + 14, hy + 27))
    obs.append(HVAC)
    # entry-well rails flank the treads (the corridor between them is
    # the walk-in route)
    obs.append((ENTRY_WELL[0], ENTRY_WELL[1] - 2, ROOM_W, ENTRY_WELL[1] + 2))
    obs.append((ENTRY_WELL[0], ROOM_L - 4, ROOM_W, ROOM_L))
    return obs


# ---------------------------------------------------------------- A* tour --
CELL = 4.0
GW, GH = int(ROOM_W / CELL), int(ROOM_L / CELL)


def build_grid(obs, clearance=11.0):
    blocked = bytearray(GW * GH)
    margin = 8.0
    for gy in range(GH):
        cy = (gy + 0.5) * CELL
        for gx in range(GW):
            cx = (gx + 0.5) * CELL
            if (cx < margin or cx > ROOM_W - margin
                    or cy < margin or cy > ROOM_L - margin):
                blocked[gy * GW + gx] = 1
    for (x0, y0, x1, y1) in obs:
        ax0 = max(0, int((x0 - clearance) / CELL))
        ay0 = max(0, int((y0 - clearance) / CELL))
        ax1 = min(GW - 1, int((x1 + clearance) / CELL))
        ay1 = min(GH - 1, int((y1 + clearance) / CELL))
        for gy in range(ay0, ay1 + 1):
            for gx in range(ax0, ax1 + 1):
                blocked[gy * GW + gx] = 1
    # keep the entry channel (S wall, v50 orientation) walkable
    for gy in range(int(646 / CELL), int(678 / CELL)):
        for gx in range(int(236 / CELL), GW):
            cx, cy = (gx + 0.5) * CELL, (gy + 0.5) * CELL
            if 236 < cx < ROOM_W - 2 and 646 < cy < 678:
                blocked[gy * GW + gx] = 0
    return blocked


def nearest_free(blocked, x, y):
    gx0, gy0 = int(x / CELL), int(y / CELL)
    best, bd = None, 1e18
    for gy in range(GH):
        for gx in range(GW):
            if not blocked[gy * GW + gx]:
                d = (gx - gx0) ** 2 + (gy - gy0) ** 2
                if d < bd:
                    bd, best = d, (gx, gy)
    return best


def astar(blocked, a, b):
    if a == b:
        return [a]
    openq = [(0, a)]
    came, gsc = {a: None}, {a: 0.0}
    moves = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
             (1, 1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (-1, -1, 1.414)]
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == b:
            path = [cur]
            while came[cur] is not None:
                cur = came[cur]
                path.append(cur)
            return path[::-1]
        cx, cy = cur
        for dx, dy, w in moves:
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < GW and 0 <= ny < GH):
                continue
            if blocked[ny * GW + nx]:
                continue
            if dx and dy and (blocked[cy * GW + nx] or blocked[ny * GW + cx]):
                continue
            ng = gsc[cur] + w
            if ng < gsc.get((nx, ny), 1e18):
                gsc[(nx, ny)] = ng
                came[(nx, ny)] = cur
                h = math.hypot(b[0] - nx, b[1] - ny)
                heapq.heappush(openq, (ng + h, (nx, ny)))
    return None


def los_free(blocked, a, b):
    steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) * 2 + 1
    for i in range(steps + 1):
        t = i / steps
        gx = int(round(a[0] + (b[0] - a[0]) * t))
        gy = int(round(a[1] + (b[1] - a[1]) * t))
        if blocked[gy * GW + gx]:
            return False
    return True


def smooth(blocked, cells):
    if not cells:
        return []
    out = [cells[0]]
    i = 0
    while i < len(cells) - 1:
        j = len(cells) - 1
        while j > i + 1 and not los_free(blocked, cells[i], cells[j]):
            j -= 1
        out.append(cells[j])
        i = j
    return out


def tour_for(cfg):
    obs = obstacle_rects(cfg)
    blocked = build_grid(obs)
    inside_entry = (238.0, 662.0)   # room floor at the top of the treads
    targets = [(280.0, 588.0), (260.0, 56.0), (52.0, 56.0),
               (52.0, 600.0), (160.0, 350.0), inside_entry]
    cur = nearest_free(blocked, *inside_entry)
    cells = [cur]
    for t in targets:
        goal = nearest_free(blocked, *t)
        leg = astar(blocked, cells[-1], goal)
        if leg:
            # smooth per leg — the whole tour is a closed loop, and
            # smoothing it as one polyline collapses start-to-end
            cells += smooth(blocked, leg)[1:]
    pts = [((gx + 0.5) * CELL, (gy + 0.5) * CELL) for gx, gy in cells]
    # scripted door legs: spawn outside, enter; exit at the end
    entry_out = (348.0, 662.0)
    return [entry_out, (316.0, 662.0)] + pts + [(316.0, 662.0), entry_out]


# ------------------------------------------------------------------- data --
def layout_data(cfg):
    key = cfg["key"]
    letter = cfg.get("letter") or SHORT[key][0]
    short = cfg.get("short") or SHORT[key][1]
    rot = cfg.get("rot90", False)
    plus = {(round(px, 1), round(py, 1))
            for px, py in cfg.get("rounds_plus", [])}
    rounds, chairs = [], []
    for cx, cy in cfg.get("rounds", []):
        isplus = (round(cx, 1), round(cy, 1)) in plus
        rounds.append([round(cx, 1), round(cy, 1)])
        chairs += [[round(a, 1), round(b, 1), round(yaw, 1)]
                   for a, b, yaw in chairs_for(cx, cy, isplus)]
    tops = []
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        ns = 1 if (hy < 40 or hy > ROOM_L - 40) else 0
        tops.append([round(hx, 1), round(hy, 1), ns])
    return dict(
        key=key, letter=letter, short=short,
        name=cfg["name"].split("·", 1)[-1].strip(),
        img=thumb_data_uri(key),
        tables=[[round(v, 2) for v in table_rect(tx, ty, tbl_rot(cfg, _n))]
                for _n, tx, ty in cfg["tables"]],
        rounds=rounds, chairs=chairs, tops=tops,
        paths=[[round(v, 1) for v in p] for p in cfg.get("paths", [])],
        obstacles=[[round(v, 1) for v in r] for r in obstacle_rects(cfg)],
        tour=[[round(x, 1), round(y, 1)] for x, y in tour_for(cfg)],
    )


def main():
    data = dict(
        room=dict(w=ROOM_W, l=ROOM_L, beamY=BEAM_Y, hvac=list(HVAC),
                  well=list(ENTRY_WELL)),
        layouts=[layout_data(c) for c in CONFIGS],
        downloads=dict(
            options_pdf=file_data_uri("docs/pool_room_v16_options.pdf",
                                      "application/pdf"),
            sheet_pdf=file_data_uri("docs/pool_room_topdowns.pdf",
                                    "application/pdf"),
        ),
        links=dict(deck=DECK_URL, download=DOWNLOAD_URL),
    )
    tpl_path = os.path.join(HERE, "walkthrough_template.html")
    with open(tpl_path) as fh:
        tpl = fh.read()
    html = tpl.replace("/*__DATA__*/", "const DATA = "
                       + json.dumps(data, separators=(",", ":")) + ";")
    # v47: walk.html — the hub owns index.html (the GitHub Pages root)
    # v48: Pages serves the repo root — public pages live there
    out = os.path.join(ROOT, "walk.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1e6:.1f} MB, "
          f"{len(data['layouts'])} layouts)")


if __name__ == "__main__":
    main()
