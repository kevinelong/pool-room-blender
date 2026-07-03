"""v16 configuration study — six floor-plan variants of the pool room.

Each config strikes a different balance between pool players, spectators,
drinkers, eaters, and the two service streams (kitchen food via the mid-east
kitchen door; bar cocktail service via the SE Main Entry).

All coordinates are room inches: x 0..316 (west->east), y 0..682
(north->south, y=0 is the north/stage wall) — same convention as
build_pool_room.py / build_pool_room_furniture.py. Table tuples are
(name, cabinet_center_x, cabinet_top_y) matching build_pool_table().
"""

# ---- shared geometry (mirrors the build scripts) ---------------------------
ROOM_W, ROOM_L = 316, 682
BEAM_Y = 332
PLAY_W, PLAY_L, RAIL_W = 39.0, 78.0, 7.25
TBL_W, TBL_L = PLAY_W + 2 * RAIL_W, PLAY_L + 2 * RAIL_W   # 53.5 x 92.5
CUE = 58.0                       # full cue-swing clearance from playfield edge
CUE_TIGHT = 54.0                 # "playable but tight" threshold

XL, XR, XC = 105.0, 211.0, 158.0  # west column, east column, center (feature)

STAGE = (0, 0, 96, 48)            # NW corner stage
BENCH = (102, 0, 270, 18)         # north-wall bench (7 seats)
HVAC = (288, 338, 316, 380)       # east-wall chase south of beam
LOCKERS = (270, 0, 316, 18)       # NE corner locker run (clear of Storage A)
CLASSROOM = (56, 80, 260, 197.5)  # 2x3 folding-table block (social config)
SERVICE_LANE_X = (265, 300)       # east service lane (green strip)

DOOR_MAIN = (316, 612, 316, 682)   # E wall, south end (cocktail stream origin)
DOOR_KITCHEN = (316, 290, 316, 330)  # E wall, mid (food stream origin)
DOOR_EXIT = (221, 682, 286, 682)   # S wall, east half (egress only)
EXIT_FRONTAGE = (215, 616, 292, 682)  # must stay furniture-free

SEATS_PER_TABLE = 4       # players per pool table
ROUND_D = 48              # folding round diameter
ROUND_COVERS = 5
TWOTOP_SEATS = 2
HIGHTOP_SEATS = 4
RAIL_IN_PER_SEAT = 24
BENCH_SEATS = 7
CLASSROOM_SEATS = 24

# Revenue-proxy defaults ($/hr) — decision makers edit these in the deck.
RATES = {"table": 18.0, "drink_seat": 9.0, "dine_cover": 14.0,
         "spectator": 2.0}


def _rows(y_tops, cols=(XL, XR), prefix="T"):
    out = []
    for i, yt in enumerate(y_tops):
        for j, cx in enumerate(cols):
            out.append((f"{prefix}{i}{'LR'[j % 2] if len(cols) == 2 else j}",
                        cx, yt))
    return out


CONFIGS = [
    dict(
        key="league",
        name="1 · League Hall",
        tagline="Player-max: 8 tables, rail drinks only, no food",
        tables=_rows([100.0, 246.5, 393.0, 539.5]),
        rounds=[], twotops=[], hightops=[],
        rails=[(2, 350, 2, 650, "drink")],          # west-wall drink rail
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        twotop_role=None,
        flip_minutes=0,
        notes=[
            "Maximizes table-hours: 8 tables, 32 player positions.",
            "The SE table narrows the exit approach to a ~54\" corridor "
            "shared with cue swing and the cocktail route.",
            "Row gaps run tight (54–57\"); no in-room dining, and every "
            "west-rail drink delivery crosses active cue zones.",
        ],
    ),
    dict(
        key="social",
        name="2 · Social Hall (current)",
        tagline="The built v15L3 balance: 6 tables + classroom + two-tops",
        tables=_rows([233.5, 392.0, 537.0]),
        rounds=[], hightops=[],
        twotops=[(282, y) for y in (335, 386, 437, 488, 539, 590)],
        twotop_role="flex",                         # drink/eat flex seats
        rails=[],
        bench=True, bench_role="spectate",
        classroom=True, bleachers=[], stage_seats=0,
        flip_minutes=0,
        notes=[
            "The layout as built — the baseline everything else is judged against.",
            "Two-tops flex between drinkers, eaters, and spectators.",
            "Classroom block serves league meetings and lessons.",
        ],
    ),
    dict(
        key="tournament",
        name="3 · Tournament House",
        tagline="Feature table + bleachers; spectators outnumber players",
        tables=[("PracL", XL, 233.5), ("PracR", XR, 233.5),
                ("Feature", XC, 420.0)],
        rounds=[], twotops=[(282, 360), (282, 420)],
        twotop_role="drink",
        hightops=[],
        rails=[],
        bench=True, bench_role="spectate",
        classroom=False,
        bleachers=[(4, 380, 58, 660)],              # 3-row west bleacher
        stage_seats=8,                               # stage = VIP/commentary
        flip_minutes=45,
        notes=[
            "One feature table with protected sightlines from a 3-row west bleacher.",
            "Food reduced to handhelds — trays cannot cross mid-rack sightlines.",
            "Slowest to flip back (bleachers, 45 min).",
        ],
    ),
    dict(
        key="lounge",
        name="4 · Cocktail Lounge",
        tagline="Bar-forward: south third is high-tops, shortest tray runs",
        tables=_rows([100.0, 246.5]),
        rounds=[],
        twotops=[(282, 360), (282, 415), (282, 470)],
        twotop_role="spectate",
        hightops=[(70, 500), (150, 500), (230, 500),
                  (70, 590), (150, 590), (230, 590)],
        rails=[(2, 460, 2, 660, "drink"), (40, 680, 180, 680, "drink")],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=15,
        notes=[
            "Bar staff barely enter the room — the lounge zone is at the door.",
            "37 drink positions; beverage revenue leader.",
            "Player capacity halved vs league hall.",
        ],
    ),
    dict(
        key="bistro",
        name="5 · Billiards Bistro",
        tagline="Dining-forward: rounds wrap the kitchen door, hot 10-step carry",
        tables=[("NL", XL, 100.0), ("NR", XR, 100.0), ("C", XC, 246.5)],
        rounds=[(80, 430), (160, 430), (240, 430),
                (80, 560), (160, 560), (240, 560)],
        twotops=[], hightops=[],
        rails=[(2, 430, 2, 610, "drink")],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "30 covers within a short carry of the kitchen door.",
            "Cocktails have the longest run — wants a mid-room drop station.",
            "Only 12 player positions; pool becomes the amenity, not the anchor.",
        ],
    ),
    dict(
        key="split",
        name="6 · Split-House Flex",
        tagline="Beam line divides: 4 fixed tables north, flex banquet south",
        tables=_rows([98.0, 244.5]),
        rounds=[(68, 420), (148, 420), (228, 420),
                (68, 545), (148, 545), (228, 545),
                (68, 630), (148, 630)],
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "Service never crosses the play zone — both doors land in the flex half.",
            "40 flex covers double as dining, drinking, or overflow spectating.",
            "Most operationally clean; nothing is optimal, everything is possible.",
        ],
    ),
]


def table_rect(cx, y_top):
    return (cx - TBL_W / 2, y_top, cx + TBL_W / 2, y_top + TBL_L)


def playfield_rect(cx, y_top):
    x0, y0, x1, y1 = table_rect(cx, y_top)
    return (x0 + RAIL_W, y0 + RAIL_W, x1 - RAIL_W, y1 - RAIL_W)


def cue_zone(cx, y_top):
    x0, y0, x1, y1 = playfield_rect(cx, y_top)
    return (x0 - CUE, y0 - CUE, x1 + CUE, y1 + CUE)


def obstacles(cfg, exclude_table=None):
    """Static furniture rects for clearance/egress checks."""
    obs = [("stage", STAGE), ("lockers", LOCKERS), ("hvac", HVAC)]
    if cfg.get("bench"):
        obs.append(("bench", BENCH))
    if cfg.get("classroom"):
        obs.append(("classroom", CLASSROOM))
    for name, cx, yt in cfg["tables"]:
        if name != exclude_table:
            obs.append((f"table:{name}", table_rect(cx, yt)))
    for i, (cx, cy) in enumerate(cfg.get("rounds", [])):
        r = ROUND_D / 2 + 10   # + chair ring
        obs.append((f"round{i}", (cx - r, cy - r, cx + r, cy + r)))
    for i, (cx, cy) in enumerate(cfg.get("twotops", [])):
        obs.append((f"twotop{i}", (cx - 17, cy - 17, cx + 17, cy + 17)))
    for i, (cx, cy) in enumerate(cfg.get("hightops", [])):
        obs.append((f"hightop{i}", (cx - 22, cy - 22, cx + 22, cy + 22)))
    for i, bl in enumerate(cfg.get("bleachers", [])):
        obs.append((f"bleacher{i}", bl))
    return obs


def seat_positions(cfg):
    """(kind, x, y) service targets. kinds: drink, dine, flex."""
    seats = []
    for cx, cy in cfg.get("rounds", []):
        kind = cfg.get("round_role", "dine")
        seats.append((kind, cx, cy))
    for cx, cy in cfg.get("twotops", []):
        role = cfg.get("twotop_role") or "drink"
        if role in ("drink", "flex", "dine"):
            seats.append((role, cx, cy))
    for cx, cy in cfg.get("hightops", []):
        seats.append(("drink", cx, cy))
    for x0, y0, x1, y1, _role in cfg.get("rails", []):
        n = max(1, int((abs(x1 - x0) + abs(y1 - y0)) / RAIL_IN_PER_SEAT))
        for i in range(n):
            t = (i + 0.5) / n
            seats.append(("drink", x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return seats


def capacities(cfg):
    n_tables = len(cfg["tables"])
    players = n_tables * SEATS_PER_TABLE
    dine = drink = flex = 0
    for cx, cy in cfg.get("rounds", []):
        if cfg.get("round_role", "dine") == "flex":
            flex += ROUND_COVERS
        else:
            dine += ROUND_COVERS
    tt = cfg.get("twotop_role")
    n_tt = len(cfg.get("twotops", [])) * TWOTOP_SEATS
    spectators = 0
    if tt == "drink":
        drink += n_tt
    elif tt == "flex":
        flex += n_tt
    elif tt == "spectate":
        spectators += n_tt
    drink += len(cfg.get("hightops", [])) * HIGHTOP_SEATS
    for x0, y0, x1, y1, _r in cfg.get("rails", []):
        drink += max(1, int((abs(x1 - x0) + abs(y1 - y0)) / RAIL_IN_PER_SEAT))
    if cfg.get("bench") and cfg.get("bench_role") == "spectate":
        spectators += BENCH_SEATS
    if cfg.get("classroom"):
        spectators += CLASSROOM_SEATS
    for x0, y0, x1, y1 in cfg.get("bleachers", []):
        rows = max(1, int((x1 - x0) / 18))
        spectators += rows * int((y1 - y0) / 22)
    spectators += cfg.get("stage_seats", 0)
    return dict(tables=n_tables, players=players, dine=dine, drink=drink,
                flex=flex, spectators=spectators)
