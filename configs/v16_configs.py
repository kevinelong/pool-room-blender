"""v16 configuration study — six floor-plan variants of the pool room.

FIXED SPECS (user-locked, 2026-07-03 — do not change):
  * Every option has EXACTLY SIX pool tables. Never any other quantity.
  * Round tables: 5 ft (60") diameter stacking folding rounds.
  * Classroom tables: 2.5 x 8 ft (30" x 96").
  * Two-tops: 22" x 28" tops, standard bar height (~42").

With the table count fixed, the options differ in where the six tables sit
and what fills the freed floor: rail drinking (league), classroom (social),
a north spectator gallery (tournament), an entry-end high-top lounge
(lounge), permanent dining rounds (bistro), or a folding flex zone (split).

Coordinates are room inches: x 0..316 (west->east), y 0..682 (north->south,
y=0 north). Table tuples are (name, cabinet_center_x, cabinet_top_y).
"""

# ---- shared geometry (mirrors the build scripts) ---------------------------
ROOM_W, ROOM_L = 316, 682
BEAM_Y = 332
PLAY_W, PLAY_L, RAIL_W = 39.0, 78.0, 7.25
TBL_W, TBL_L = PLAY_W + 2 * RAIL_W, PLAY_L + 2 * RAIL_W   # 53.5 x 92.5
CUE = 58.0                       # full cue-swing clearance from playfield edge
CUE_TIGHT = 54.0                 # "playable but tight" threshold

XL, XR, XC = 105.0, 211.0, 158.0  # west column, east column, center

STAGE = (0, 0, 96, 48)            # NW corner stage
BENCH = (102, 0, 270, 18)         # north-wall bench (7 seats)
HVAC = (288, 338, 316, 380)       # east-wall chase south of beam
LOCKERS = (270, 0, 316, 18)       # NE corner locker run
CLASSROOM = (56, 40, 260, 197.5)  # 2x3 block of 30"-deep folding tables
SERVICE_LANE_X = (265, 300)       # east service lane (green strip)

DOOR_MAIN = (316, 612, 316, 682)   # E wall, south end (cocktail stream)
DOOR_KITCHEN = (316, 290, 316, 330)  # E wall, mid (food stream)
DOOR_EXIT = (221, 682, 286, 682)   # S wall, east half (egress only)
EXIT_FRONTAGE = (215, 616, 292, 682)  # egress approach band

SEATS_PER_TABLE = 4       # players per pool table
N_TABLES = 6              # LOCKED: every option has exactly six tables
ROUND_D = 60              # LOCKED: 5 ft rounds
ROUND_COVERS = 8          # a 60" round seats eight
TWOTOP_SEATS = 2
HIGHTOP_SEATS = 2         # free-standing 22x28 two-top (bar height)
RAIL_IN_PER_SEAT = 24
BENCH_SEATS = 7
CLASSROOM_SEATS = 24

# Revenue-proxy defaults ($/hr) — decision makers edit these in the deck.
RATES = {"table": 18.0, "drink_seat": 9.0, "dine_cover": 14.0,
         "spectator": 2.0}

# Standard 3-row layout (the current build): back pair + two main pairs.
ROWS_CURRENT = [233.5, 392.0, 537.0]
# North-compressed 3-row layout: frees the south third (y > ~500).
ROWS_NORTH = [100.0, 246.5, 393.0]
# Spread 3-row layout: generous ~77" aisles across the full room.
ROWS_SPREAD = [130.0, 300.0, 470.0]


def _rows(y_tops, cols=(XL, XR)):
    out = []
    for i, yt in enumerate(y_tops):
        for j, cx in enumerate(cols):
            out.append((f"T{i}{'LR'[j]}", cx, yt))
    return out


CONFIGS = [
    dict(
        key="league",
        name="1 · League Hall",
        tagline="Player-first: six tables at maximum elbow room, rail drinks",
        tables=_rows(ROWS_SPREAD),
        rounds=[], twotops=[], hightops=[],
        rails=[(2, 120, 2, 660, "drink")],          # west-wall drink rail
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        twotop_role=None,
        flip_minutes=0,
        notes=[
            "The six tables spread across the full room — the widest aisles "
            "of any option.",
            "Drinks live on the west rail; deliveries cross active play.",
            "No in-room dining and nowhere to host a crowd.",
        ],
    ),
    dict(
        key="social",
        name="2 · Social Hall (current)",
        tagline="The built layout: six tables + classroom + wall two-tops",
        tables=_rows(ROWS_CURRENT),
        rounds=[], hightops=[],
        twotops=[(282, y) for y in (335, 386, 437, 488, 539, 590)],
        twotop_role="flex",
        rails=[],
        bench=True, bench_role="spectate",
        classroom=True, bleachers=[], stage_seats=0,
        flip_minutes=0,
        notes=[
            "The room as built — the baseline every option is judged against.",
            "Two-tops flex between drinkers, eaters, and spectators.",
            "Classroom block serves league meetings and lessons.",
        ],
    ),
    dict(
        key="tournament",
        name="3 · Tournament House",
        tagline="North gallery: bleachers + stage face the feature row",
        tables=_rows(ROWS_CURRENT),
        rounds=[], hightops=[],
        twotops=[(282, 340), (282, 400)],
        twotop_role="drink",
        rails=[],
        bench=False, bench_role=None,
        classroom=False,
        bleachers=[(102, 20, 270, 74)],   # 3-row gallery on the north wall
        stage_seats=8,                     # stage = VIP/commentary
        flip_minutes=45,
        notes=[
            "The bench gives way to a three-row gallery; the back pair "
            "becomes the feature row under the audience's nose.",
            "Food drops to handhelds while racks are in play.",
            "Slowest to flip back (bleachers).",
        ],
    ),
    dict(
        key="lounge",
        name="4 · Cocktail Lounge",
        tagline="Bar-forward: tables compress north, high-tops own the entry end",
        tables=_rows(ROWS_NORTH),
        rounds=[],
        twotops=[(282, 460), (282, 512)],
        twotop_role="spectate",
        hightops=[(70, 560), (150, 560), (230, 560), (70, 630), (150, 630)],
        rails=[(2, 470, 2, 660, "drink"), (40, 680, 180, 680, "drink")],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=15,
        notes=[
            "Bar staff barely enter the room — the lounge zone is at the door.",
            "Standard bar-height two-tops and wall rails fill the south third.",
            "Same six tables, tighter aisles than league spacing.",
        ],
    ),
    dict(
        key="bistro",
        name="5 · Billiards Bistro",
        tagline="Dining-forward: five-foot rounds fill the south third",
        tables=_rows(ROWS_NORTH),
        rounds=[(70, 580), (160, 580), (250, 580), (70, 648), (155, 648)],
        twotops=[], hightops=[],
        rails=[(2, 470, 2, 640, "drink")],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "Forty covers on five-foot rounds, all south of the play zone.",
            "Food routes down the east lane past the kitchen door; cocktails "
            "have the longest run and want a drop station.",
            "Pool keeps all six tables but loses its walking room to dining.",
        ],
    ),
    dict(
        key="split",
        name="6 · Split-House Flex",
        tagline="Fixed play north, folding flex zone south of the aisle",
        tables=_rows(ROWS_NORTH),
        rounds=[(70, 580), (160, 580), (250, 580), (70, 648), (155, 648)],
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=True, bench_role="spectate",
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "Same footprint as the bistro but the rounds fold and stack — "
            "the south third flips between banquet, dining, and overflow.",
            "Service never crosses the play zone.",
            "Nothing is purpose-built; everything is possible.",
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
        obs.append((f"twotop{i}", (cx - 17, cy - 20, cx + 17, cy + 20)))
    for i, (cx, cy) in enumerate(cfg.get("hightops", [])):
        obs.append((f"hightop{i}", (cx - 20, cy - 23, cx + 20, cy + 23)))
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
    assert n_tables == N_TABLES, \
        f"{cfg['key']}: {n_tables} tables — every option must have exactly 6"
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
        depth, length = min(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0)
        rows = max(1, int(depth / 18))
        spectators += rows * int(length / 22)
    spectators += cfg.get("stage_seats", 0)
    return dict(tables=n_tables, players=players, dine=dine, drink=drink,
                flex=flex, spectators=spectators)
