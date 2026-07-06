#!/usr/bin/env python3
"""Score the six v16 configurations on metrics computed from the geometry.

Outputs analysis/scorecards.json and analysis/scorecards.md.

Metrics per config:
  capacity      players / spectators / drink / dine / flex seats
  cue quality   per-table-side clearance from playfield edge to nearest
                obstruction; % of sides >= 58" (full swing), min clearance
  service       tray-run length from Main Entry to farthest drink seat and
                from kitchen door to farthest dining cover, routed via the
                east service lane; # of seats whose route crosses a cue zone
  egress        Emergency Exit frontage kept clear (bool) + worst straight-
                line distance from any seat/table to its nearest exit door
  revenue proxy $/hr under editable RATES (deck lets decision makers adjust)
  flip cost     minutes to convert to/from the configuration
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from configs.v16_configs import (  # noqa: E402
    CONFIGS, RATES, ROOM_W, ROOM_L, CUE, CUE_TIGHT,
    DOOR_MAIN, DOOR_KITCHEN, EXIT_FRONTAGE, SERVICE_LANE_X,
    table_rect, playfield_rect, cue_zone, obstacles, seat_positions,
    capacities,
)

# Servers walk the wall side of the east lane: the lane's center (x~282)
# sits inside the east table column's 58" cue swing (which reaches x~288.5),
# so the realistic spine hugs the wall at x=298.
LANE_X = 298.0


def _overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def side_clearances(cfg, name, cx, yt):
    """Clearance from each playfield edge to the nearest obstruction/wall."""
    px0, py0, px1, py1 = playfield_rect(cx, yt, cfg.get("rot90", False))
    obs = obstacles(cfg, exclude_table=name)
    out = {}
    for side in "WESN":
        if side == "W":
            best = px0 - 0.0
            for _n, (ox0, oy0, ox1, oy1) in obs:
                if _overlap(py0, py1, oy0, oy1) > 0 and ox1 <= px0 + 1e-6:
                    best = min(best, px0 - ox1)
        elif side == "E":
            best = ROOM_W - px1
            for _n, (ox0, oy0, ox1, oy1) in obs:
                if _overlap(py0, py1, oy0, oy1) > 0 and ox0 >= px1 - 1e-6:
                    best = min(best, ox0 - px1)
        elif side == "N":
            best = py0 - 0.0
            for _n, (ox0, oy0, ox1, oy1) in obs:
                if _overlap(px0, px1, ox0, ox1) > 0 and oy1 <= py0 + 1e-6:
                    best = min(best, py0 - oy1)
        else:  # S
            best = ROOM_L - py1
            for _n, (ox0, oy0, ox1, oy1) in obs:
                if _overlap(px0, px1, ox0, ox1) > 0 and oy0 >= py1 - 1e-6:
                    best = min(best, oy0 - py1)
        out[side] = round(best, 1)
    return out


def route(door, seat, lane_x=LANE_X):
    """Manhattan route door -> east-lane spine -> row aisle -> seat."""
    dx, dy = (door[0] + door[2]) / 2, (door[1] + door[3]) / 2
    sx, sy = seat
    pts = [(dx, dy), (lane_x, dy), (lane_x, sy), (sx, sy)]
    length = sum(abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1])
                 for i in range(len(pts) - 1))
    return pts, length


def seg_hits_rect(p, q, rect):
    (x0, y0, x1, y1) = rect
    px, py = p
    qx, qy = q
    if px == qx:                       # vertical
        if not (x0 <= px <= x1):
            return False
        return _overlap(min(py, qy), max(py, qy), y0, y1) > 0
    if py == qy:                       # horizontal
        if not (y0 <= py <= y1):
            return False
        return _overlap(min(px, qx), max(px, qx), x0, x1) > 0
    return False


def service_metrics(cfg):
    rot = cfg.get("rot90", False)
    zones = [cue_zone(cx, yt, rot) for _n, cx, yt in cfg["tables"]]
    seats = seat_positions(cfg)
    res = {}
    for stream, door, kinds in (
            ("cocktail", DOOR_MAIN, ("drink", "flex")),
            ("food", DOOR_KITCHEN, ("dine", "flex"))):
        targets = [(x, y) for k, x, y in seats if k in kinds]
        if not targets:
            res[stream] = dict(seats=0, max_run_ft=0.0, avg_run_ft=0.0,
                               conflicted_seats=0)
            continue
        runs, conflicts = [], 0
        lane_x = cfg.get("lane_x", LANE_X)
        for t in targets:
            pts, length = route(door, t, lane_x)
            runs.append(length)
            hit = any(seg_hits_rect(pts[i], pts[i + 1], z)
                      for i in range(len(pts) - 1) for z in zones)
            conflicts += int(hit)
        res[stream] = dict(seats=len(targets),
                           max_run_ft=round(max(runs) / 12, 1),
                           avg_run_ft=round(sum(runs) / len(runs) / 12, 1),
                           conflicted_seats=conflicts)
    return res


def egress_metrics(cfg):
    """Widest clear corridor reaching the Emergency Exit door.

    Scan the 66\"-deep approach band in front of the S-wall door, subtract
    obstacle x-intervals, and take the widest clear gap that actually
    overlaps the door span. Pass threshold: 44\" (maintained egress
    corridor); anything under is a hard fail.
    """
    fx0, fy0, fx1, fy1 = EXIT_FRONTAGE
    door_x0, door_x1 = 30.0, 95.0     # v18: EE at the west end of the S wall
    scan_x0, scan_x1 = 0.0, 170.0
    ivals = []
    for _name, (ox0, oy0, ox1, oy1) in obstacles(cfg):
        if _overlap(oy0, oy1, fy0, fy1) > 0 and _overlap(ox0, ox1, scan_x0, scan_x1) > 0:
            ivals.append((max(ox0, scan_x0), min(ox1, scan_x1)))
    ivals.sort()
    corridor = 0.0
    cursor = scan_x0
    for ox0, ox1 in ivals + [(scan_x1, scan_x1)]:
        if ox0 > cursor:
            gap = (cursor, ox0)
            if _overlap(gap[0], gap[1], door_x0, door_x1) > 0:
                corridor = max(corridor, gap[1] - gap[0])
        cursor = max(cursor, ox1)
    half = 26.75 if cfg.get("rot90", False) else 46.25
    pts = [(cx, yt + half) for _n, cx, yt in cfg["tables"]]
    pts += [(x, y) for _k, x, y in seat_positions(cfg)]
    worst = 0.0
    for x, y in pts:
        d_main = abs(316 - x) + abs(647 - y)
        d_exit = abs(62.5 - x) + abs(ROOM_L - y)
        worst = max(worst, min(d_main, d_exit))
    return dict(exit_corridor_in=round(corridor, 1),
                exit_corridor_ok=corridor >= 44.0,
                worst_travel_ft=round(worst / 12, 1))


def path_audit(cfg):
    """v26: measure every painted walking path's REAL clear width — the
    span between the obstacles flanking it — and call out anomalies.
    < 36" is a pinch (single server, no passing); < 24" is a fail."""
    from configs.v16_configs import (ROUND_RING, ROUND_BODY, HVAC,
                                     ENTRY_WELL, KITCHEN_FRONT)
    rot = cfg.get("rot90", False)
    named = [("a pool table", table_rect(tx, ty, rot))
             for _n, tx, ty in cfg["tables"]]
    # rounds measured at the tucked-chair body — the same convention every
    # placement rule uses (a 2" wider halo created phantom pinches)
    named += [("a round's chairs",
               (cx - ROUND_BODY, cy - ROUND_BODY,
                cx + ROUND_BODY, cy + ROUND_BODY))
              for cx, cy in cfg.get("rounds", [])]
    named += [("a wall two-top", (hx - 13, hy - 25, hx + 13, hy + 25))
              for hx, hy in
              list(cfg.get("hightops", [])) + list(cfg.get("twotops", []))]
    named += [("the HVAC chase", HVAC), ("the Main Entry well", ENTRY_WELL)]
    named += [("a bleacher", b) for b in cfg.get("bleachers", [])]

    def zone(x, y):
        ns = "north" if y < 227 else ("center" if y < 455 else "south")
        we = "west" if x < 105 else ("center" if x < 211 else "east")
        return f"{ns}-{we}"

    worst = 1e9
    seen = set()
    anomalies = []
    # The painted strips PLUS the three door approaches — a strip clipped
    # short of an obstacle hides the pinch at its seam, so the approaches
    # are audited as corridors in their own right.
    corridors = [(30.0, 650.0, 276.0, 680.0),    # EE / south-wall walk
                 (250.0, 588.0, 316.0, 612.0),   # Main Entry approach
                 (262.0, 298.0, 316.0, 322.0)]   # kitchen door approach
    for (x0, y0, x1, y1) in list(cfg.get("paths", [])) + corridors:
        horiz = (x1 - x0) >= (y1 - y0)
        length = (x1 - x0) if horiz else (y1 - y0)
        n = max(2, int(length / 8))
        for i in range(n + 1):
            t = i / n
            px = x0 + t * (x1 - x0) if horiz else (x0 + x1) / 2
            py = (y0 + y1) / 2 if horiz else y0 + t * (y1 - y0)
            inside = next((nm for nm, (ox0, oy0, ox1, oy1) in named
                           if ox0 < px < ox1 and oy0 < py < oy1), None)
            if inside:
                key = ("blocked", inside, zone(px, py))
                if key not in seen:
                    seen.add(key)
                    anomalies.append(dict(
                        severity="blocked", width_in=0.0,
                        where=f"{zone(px, py)}: walk crosses {inside}"))
                continue
            if horiz:      # clear span measured in y
                lo, lo_n = 0.0, "the north wall"
                hi, hi_n = ROOM_L, "the south wall"
                for nm, (ox0, oy0, ox1, oy1) in named:
                    if ox0 < px < ox1:
                        if oy1 <= py and oy1 > lo:
                            lo, lo_n = oy1, nm
                        if oy0 >= py and oy0 < hi:
                            hi, hi_n = oy0, nm
            else:          # clear span measured in x
                lo, lo_n = 0.0, "the west wall"
                hi, hi_n = ROOM_W, "the east wall"
                for nm, (ox0, oy0, ox1, oy1) in named:
                    if oy0 < py < oy1:
                        if ox1 <= px and ox1 > lo:
                            lo, lo_n = ox1, nm
                        if ox0 >= px and ox0 < hi:
                            hi, hi_n = ox0, nm
            w = hi - lo
            worst = min(worst, w)
            if w < 36:
                key = (lo_n, hi_n, zone(px, py))
                if key not in seen:
                    seen.add(key)
                    sev = "FAIL" if w < 24 else "pinch"
                    anomalies.append(dict(
                        severity=sev, width_in=round(w, 1),
                        where=f"{zone(px, py)}: between {lo_n} and {hi_n}"))
    anomalies.sort(key=lambda a: a["width_in"])
    return dict(min_width_in=(round(worst, 1) if worst < 1e9 else None),
                anomalies=anomalies)


def analyze(cfg):
    caps = capacities(cfg)
    tables = {}
    full = tight = bad = 0
    min_clr = 1e9
    for name, cx, yt in cfg["tables"]:
        clr = side_clearances(cfg, name, cx, yt)
        tables[name] = clr
        for v in clr.values():
            min_clr = min(min_clr, v)
            if v >= CUE:
                full += 1
            elif v >= CUE_TIGHT:
                tight += 1
            else:
                bad += 1
    n_sides = max(1, full + tight + bad)
    svc = service_metrics(cfg)
    egr = egress_metrics(cfg)
    # A flex seat hosts one patron at a time — value it at the average of
    # the drink and dine rates rather than both.
    flex_rate = (RATES["drink_seat"] + RATES["dine_cover"]) / 2
    revenue = (caps["tables"] * RATES["table"]
               + caps["drink"] * RATES["drink_seat"]
               + caps["dine"] * RATES["dine_cover"]
               + caps["flex"] * flex_rate
               + caps["spectators"] * RATES["spectator"])
    return dict(
        key=cfg["key"], name=cfg["name"], tagline=cfg["tagline"],
        capacity=caps,
        cue=dict(full_pct=round(100 * full / n_sides),
                 tight_pct=round(100 * tight / n_sides),
                 blocked_pct=round(100 * bad / n_sides),
                 min_clearance_in=round(min_clr, 1),
                 per_table=tables),
        service=svc,
        egress=egr,
        paths=path_audit(cfg),
        revenue_proxy_hr=round(revenue),
        flip_minutes=cfg["flip_minutes"],
        notes=cfg["notes"],
    )


def main():
    out = [analyze(c) for c in CONFIGS]
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "scorecards.json"), "w") as fh:
        json.dump(dict(rates=RATES, configs=out), fh, indent=2)
    lines = ["# v16 configuration scorecards\n",
             "| Config | Tables | Players | Spect. | Drink | Dine | Flex | "
             "Cue full% | Min clr\" | Cocktail max run | Food max run | "
             "Svc conflicts | Egress worst | Path min\" | $/hr proxy | "
             "Flip min |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
             "---|"]
    for r in out:
        c, s = r["capacity"], r["service"]
        conf = s["cocktail"]["conflicted_seats"] + s["food"]["conflicted_seats"]
        lines.append(
            f"| {r['name']} | {c['tables']} | {c['players']} | "
            f"{c['spectators']} | {c['drink']} | {c['dine']} | {c['flex']} | "
            f"{r['cue']['full_pct']}% | {r['cue']['min_clearance_in']} | "
            f"{s['cocktail']['max_run_ft']} ft | {s['food']['max_run_ft']} ft | "
            f"{conf} | {r['egress']['worst_travel_ft']} ft | "
            f"{r['paths']['min_width_in']} | "
            f"${r['revenue_proxy_hr']} | {r['flip_minutes']} |")
    # v26: walking-path width anomalies, called out per config
    lines.append("\n## Walking-path anomalies (clear width < 36\")\n")
    for r in out:
        an = r["paths"]["anomalies"]
        if not an:
            lines.append(f"- **{r['name']}** — none; narrowest walk "
                         f"{r['paths']['min_width_in']}\"")
        else:
            lines.append(f"- **{r['name']}** — narrowest walk "
                         f"{r['paths']['min_width_in']}\":")
            for a in an:
                lines.append(f"    - {a['severity']}: {a['width_in']}\" "
                             f"({a['where']})")
    with open(os.path.join(here, "scorecards.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
