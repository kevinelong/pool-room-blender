"""v16 configuration study — six floor-plan variants of the pool room.

FIXED SPECS (user-locked, 2026-07-03 — do not change):
  * Every option has EXACTLY SIX pool tables. Never any other quantity.
  * Round tables: 5 ft (60") diameter stacking folding rounds.
  * Classroom tables: 2.5 x 8 ft (30" x 96").
  * Two-tops: 22" x 28" tops, standard bar height (~42").

With the table count fixed, the options differ in where the six tables sit
and what fills the freed floor: rail drinking (league), classroom (social),
a north spectator gallery (tournament), or — v20 — the tables turn 90°
into a single file (rot90 layouts): down the middle (centerline) or hugging
the west wall with a full-length hospitality strip east (westline). The
north-compressed 4-tables-at-one-end layouts were removed per user review.

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
DOOR_EXIT = (30, 682, 95, 682)     # v18: S wall, WEST end (per video)
# v25: egress approach band = the 44" maintained code corridor in front of
# the door span (was 66" deep — deeper than code and inconsistent with the
# packer's keep-out, so the two disagreed about the same layout)
EXIT_FRONTAGE = (24, 638, 101, 682)

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
        key="social",
        name="1 · Social Hall",
        tagline="The built layout: six tables + wall two-tops",
        tables=_rows(ROWS_CURRENT),
        rounds=[], hightops=[],
        twotops=[(282, y) for y in (335, 386, 437, 488, 539, 590)],
        twotop_role="flex",
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=0,
        notes=[
            "The room as built — the baseline every option is judged against.",
            "Two-tops flex between drinkers, eaters, and spectators.",
        ],
    ),
    dict(
        key="tournament",
        name="2 · Tournament House",
        tagline="North gallery: bleachers + stage face the feature row",
        tables=_rows(ROWS_CURRENT),
        # v23: with the stage and lockers gone, the north end packs four
        # 5-ft rounds around the gallery
        rounds=[],   # v24: auto-packed below
        round_role="flex",
        hightops=[],
        twotops=[(282, 340), (282, 400)],
        twotop_role="drink",
        rails=[],
        bench=False, bench_role=None,
        classroom=False,
        bleachers=[(102, 20, 270, 74)],   # 3-row gallery on the north wall
        stage_seats=0,
        flip_minutes=45,
        notes=[
            "A three-row gallery faces the feature row; four rounds pack "
            "the cleared north end around it.",
            "Food drops to handhelds while racks are in play.",
            "Slowest to flip back (bleachers).",
        ],
    ),
    dict(
        key="centerline",
        name="3 · Center Line",
        tagline="Six tables turned 90°, end-to-end down the middle",
        rot90=True,
        # single file: cabinet gaps ~47.5" -> side swings land at the
        # playable-but-tight 54.75"; both row ends get full clearance
        tables=[(f"Line{i}", 158.0, yt)
                for i, yt in enumerate([71, 172, 273, 374, 475, 576])],
        rounds=[],
        # v23: a bar two-top at BOTH ends of every table, against the west
        # and east walls (the table-end swings stop 61" short of the walls,
        # so the wall seats sit outside them). East-side y-nudges clear the
        # kitchen frontage, HVAC chase, and entry well.
        hightops=([(25, cy) for cy in
                   (97.75, 198.75, 299.75, 400.75, 501.75, 590)]
                  + [(291, cy) for cy in
                     (97.75, 198.75, 265, 410, 501.75, 585)]),
        twotops=[],
        twotop_role=None,
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=0,
        notes=[
            "Every table on display: the side aisles run the full length, "
            "so one walk covers all six tables.",
            "Side-to-side swings between neighbouring tables run tight; "
            "the table ends get full room.",
            "West-rail drink deliveries cross the line at every table.",
        ],
    ),
    dict(
        key="eastline",
        name="4 · East Line + West Lounge",
        tagline="Tables single-file on the east; full-length hospitality strip west",
        rot90=True,
        # cx=206 keeps the playfield clear of the NW stage (which blocks a
        # west-hugging file) and clear of the east service lane and entry well
        # v23: the top (south) table shifts west, centered between the
        # sixth round and the entry-stair railing (well edge x=276)
        tables=([(f"Line{i}", 206.0, yt)
                 for i, yt in enumerate([71, 172, 273, 374, 475])]
                + [("Line5", 185.5, 576)]),
        # v23: six rounds at an even 90" pitch — the sixth at the south top
        # of the column, clear of the Emergency Exit approach
        rounds=[],   # v24: auto-packed below
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "The west side becomes a 9-ft hospitality strip the full length "
            "of the room — folding rounds and a high-top under the windows-"
            "side wall, clear of the Emergency Exit approach.",
            "Same tight side-to-side swings as the center line; table ends "
            "get full room.",
            "Every delivery crosses the table line — the price of putting "
            "all hospitality opposite the doors.",
        ],
    ),
    dict(
        key="westline",
        name="5 · West Line + Wall Rounds",
        tagline="Tables single-file west; a round beside each table on the east wall",
        rot90=True,
        # v23: stage removed entirely (user) — the west file needs no
        # stage relocation any more
        # v25: the spine threads BETWEEN the table swing and the wall rounds
        # — an east-wall spine (298) forced the packer to pull every round
        # 58" off the wall, defeating this layout's whole idea
        lane_x=213.0,
        tables=[(f"Line{i}", 110.0, yt)
                for i, yt in enumerate([71, 172, 273, 374, 475, 576])],
        # v23: one round per table against the east wall, centered on its
        # table where possible — pulled inboard/nudged only where the
        # kitchen frontage, HVAC chase, or entry well forces it
        rounds=[],   # v24: auto-packed below
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=25,
        notes=[
            "Each table gets its own 5-ft round on the east wall at the "
            "same height — table service at arm's reach.",
            "Three rounds pull inboard where the kitchen door, HVAC chase, "
            "and entry well need clearance.",
            "The aisle between play and rounds runs narrow; servers "
            "thread it.",
        ],
    ),
]


def table_rect(cx, y_top, rot90=False):
    """Cabinet rect. rot90=True: long axis east-west (v20 line layouts) —
    y_top is then the NORTH edge of the rotated (53.5\" deep) cabinet."""
    if rot90:
        return (cx - TBL_L / 2, y_top, cx + TBL_L / 2, y_top + TBL_W)
    return (cx - TBL_W / 2, y_top, cx + TBL_W / 2, y_top + TBL_L)


def playfield_rect(cx, y_top, rot90=False):
    x0, y0, x1, y1 = table_rect(cx, y_top, rot90)
    return (x0 + RAIL_W, y0 + RAIL_W, x1 - RAIL_W, y1 - RAIL_W)


def cue_zone(cx, y_top, rot90=False):
    x0, y0, x1, y1 = playfield_rect(cx, y_top, rot90)
    return (x0 - CUE, y0 - CUE, x1 + CUE, y1 + CUE)


def obstacles(cfg, exclude_table=None):
    """Static furniture rects for clearance/egress checks."""
    # v23: stage and storage lockers removed from ALL layouts (user)
    obs = [("hvac", HVAC)]
    if cfg.get("bench"):
        obs.append(("bench", BENCH))
    if cfg.get("classroom"):
        obs.append(("classroom", CLASSROOM))
    rot = cfg.get("rot90", False)
    for name, cx, yt in cfg["tables"]:
        if name != exclude_table:
            obs.append((f"table:{name}", table_rect(cx, yt, rot)))
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


# ============================================================================
# v24: round auto-packing + precise staff pathways (user 2026-07-05)
# ============================================================================
# v25: chair-aware collision model. The 4 hotel stacking chairs (11x12")
# sit at the cardinal points and reach 46" from the round's center (the
# driver seats them at +/-46 on each axis, tucked 4" off the 60" top).
# A single 46" circle over-blocks (diagonal neighbours interleave chairs
# safely at 84" cc), so:
#   ROUND_RING     bounding radius incl. chairs — walls, doors, path clips
#   ROUND_BODY     disc + tucked-chair radius — furniture/table margins
#   ROUND_MIN_CC   floor for any two rounds (diagonal packing OK)
#   ROUND_AXIS_CC  floor when two rounds face chair-to-chair on an axis
ROUND_RING = 46.0
ROUND_BODY = 38.0          # chairs pushed in tuck to ~38" from center
ROUND_MIN_CC = 84.0
ROUND_AXIS_CC = 96.0       # 45+45 chair reach + 6" air
ROUND_AXIS_BAND = 17.0     # facing-chair rule applies inside this offset

# Two keep-out tiers. Life-safety egress is checked against the FULL chair
# ring — a chair leg in an exit path is an egress obstruction (the EE band
# depth is exactly the 44" code corridor). Service frontages and the HVAC
# chase are checked against the tucked-chair body: a chair back grazing a
# kitchen-door approach is v23-accepted practice, an exit path is not.
KEEPOUTS_EGRESS = [
    (250, 596, 316, 682),   # Main Entry well + rails + approach
    EXIT_FRONTAGE,          # Emergency Exit 44" egress corridor
]
KEEPOUTS_FRONTAGE = [
    (268, 282, 316, 338),   # kitchen door frontage
    (268, 0, 316, 48),      # Storage A door frontage (N wall, east end)
    (272, 0, 316, 48),      # Storage B door frontage (E wall, north end)
    HVAC,
]
KEEPOUTS = KEEPOUTS_EGRESS + KEEPOUTS_FRONTAGE   # for path clipping et al.


def _rect_overlap(a, b):
    return (min(a[2], b[2]) - max(a[0], b[0]) > 0
            and min(a[3], b[3]) - max(a[1], b[1]) > 0)


def _round_ok(cx, cy, cfg, placed, lane_x, aligned=False):
    w = ROUND_RING + 1
    if not (w <= cx <= ROOM_W - w and w <= cy <= ROOM_L - w):
        return False
    ring = (cx - ROUND_RING, cy - ROUND_RING, cx + ROUND_RING, cy + ROUND_RING)
    body = (cx - ROUND_BODY, cy - ROUND_BODY, cx + ROUND_BODY, cy + ROUND_BODY)
    rot = cfg.get("rot90", False)
    for _n, tx, ty in cfg["tables"]:
        x0, y0, x1, y1 = table_rect(tx, ty, rot)
        if _rect_overlap(body, (x0 - 32, y0 - 32, x1 + 32, y1 + 32)):
            return False
    for ko in KEEPOUTS_EGRESS:
        if _rect_overlap(ring, ko):
            return False
    for ko in KEEPOUTS_FRONTAGE:
        if _rect_overlap(body, ko):
            return False
    for hx, hy in cfg.get("hightops", []):
        if _rect_overlap(body, (hx - 26, hy - 29, hx + 26, hy + 29)):
            return False
    for tx, ty in cfg.get("twotops", []):
        if _rect_overlap(body, (tx - 26, ty - 29, tx + 26, ty + 29)):
            return False
    for bl in cfg.get("bleachers", []):
        if _rect_overlap(body, bl):
            return False
    # reserved service spine — the mandated per-table (aligned) rounds
    # trump it; the paths clip around whatever lands there
    if not aligned:
        if lane_x - 16 < cx + ROUND_BODY and cx - ROUND_BODY < lane_x + 16:
            if abs(cx - lane_x) < ROUND_BODY + 16:
                return False
    for px_, py_ in placed:
        dx, dy = abs(cx - px_), abs(cy - py_)
        if dx * dx + dy * dy < ROUND_MIN_CC ** 2:
            return False
        # facing chairs collide long before the discs do
        if dx < ROUND_AXIS_CC and dy < ROUND_AXIS_BAND:
            return False
        if dy < ROUND_AXIS_CC and dx < ROUND_AXIS_BAND:
            return False
    return True


def _sweep(start, stop, step):
    """Inclusive walk from start toward stop (step sign gives direction)."""
    out, v = [], start
    while (v >= stop) if step < 0 else (v <= stop):
        out.append(v)
        v += step
    return out


def pack_rounds(cfg):
    """Fill every zone away from the tables with rounds. Rounds at the
    table ends are seeded FIRST, centered on the table's long axis (the
    user's alignment rule), preferring the wall-adjacent spot and sliding
    inboard along the centerline only where a chase/door/well blocks it.
    A greedy grid fill takes whatever space remains."""
    lane_x = cfg.get("lane_x", 298.0)
    rot = cfg.get("rot90", False)
    placed = []
    # 1) alignment-seeded candidates on each table's centerline: sweep from
    #    the wall inboard to table-adjacent; first legal spot per side wins
    for _n, tx, ty in cfg["tables"]:
        x0, y0, x1, y1 = table_rect(tx, ty, rot)
        if rot:
            mid = (y0 + y1) / 2
            sides = [[(x, mid) for x in
                      _sweep(ROOM_W - ROUND_RING - 1, x1 + 32 + ROUND_BODY, -1)],
                     [(x, mid) for x in
                      _sweep(ROUND_RING + 1, x0 - 32 - ROUND_BODY, 1)]]
        else:
            mid = (x0 + x1) / 2
            sides = [[(mid, y) for y in
                      _sweep(ROUND_RING + 1, y0 - 32 - ROUND_BODY, 1)],
                     [(mid, y) for y in
                      _sweep(ROOM_L - ROUND_RING - 1, y1 + 32 + ROUND_BODY, -1)]]
        for cands in sides:
            for cx, cy in cands:
                if _round_ok(cx, cy, cfg, placed, lane_x, aligned=True):
                    placed.append((round(cx, 1), round(cy, 1)))
                    break
    # 2) greedy grid fill of everything else
    y = ROUND_RING + 1
    while y <= ROOM_L - ROUND_RING - 1:
        x = ROUND_RING + 1
        while x <= ROOM_W - ROUND_RING - 1:
            if _round_ok(x, y, cfg, placed, lane_x):
                placed.append((float(x), float(y)))
            x += 4
        y += 4
    return placed


def compute_paths(cfg):
    """Green staff pathways, clipped precisely between obstacles: a service
    spine plus door stubs and per-seat feeders. Returns floor rects."""
    lane_x = cfg.get("lane_x", 298.0)
    rot = cfg.get("rot90", False)
    obs = [table_rect(tx, ty, rot) for _n, tx, ty in cfg["tables"]]
    obs += [(cx - ROUND_RING, cy - ROUND_RING, cx + ROUND_RING, cy + ROUND_RING)
            for cx, cy in cfg.get("rounds", [])]
    obs += [(hx - 26, hy - 29, hx + 26, hy + 29)
            for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", []))]
    obs += [HVAC] + list(cfg.get("bleachers", []))

    def clip_strip(x0, y0, x1, y1):
        """Axis-aligned strip minus obstacle intervals along its long axis."""
        out = []
        if x1 - x0 >= y1 - y0:            # horizontal strip
            cuts = sorted((max(o[0], x0), min(o[2], x1)) for o in obs
                          if _rect_overlap((x0, y0, x1, y1), o))
            cur = x0
            for a, b in cuts:
                if a > cur:
                    out.append((cur, y0, a, y1))
                cur = max(cur, b)
            if cur < x1:
                out.append((cur, y0, x1, y1))
        else:                              # vertical strip
            cuts = sorted((max(o[1], y0), min(o[3], y1)) for o in obs
                          if _rect_overlap((x0, y0, x1, y1), o))
            cur = y0
            for a, b in cuts:
                if a > cur:
                    out.append((x0, cur, x0 + (x1 - x0), a))
                cur = max(cur, b)
            if cur < y1:
                out.append((x0, cur, x1, y1))
        return [r for r in out if r[2] - r[0] > 6 and r[3] - r[1] > 6]

    paths = []
    paths += clip_strip(lane_x - 12, 30, lane_x + 12, 660)      # spine
    paths += clip_strip(min(lane_x, 276), 624, 316, 648)        # ME stub
    paths += clip_strip(min(lane_x, 290), 298, 316, 322)        # kitchen stub
    paths += clip_strip(50, 600, 74, 682)                        # EE stub
    paths += clip_strip(50, 600, lane_x, 624)                    # EE link
    for cx, cy in cfg.get("rounds", []):
        a, b = sorted((cx + ROUND_RING, lane_x))
        paths += clip_strip(a, cy - 10, b, cy + 10)
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        a, b = sorted((hx + 26, lane_x))
        paths += clip_strip(a, hy - 10, b, hy + 10)
    return paths


# post-process: pack rounds into every config, then freeze
for _cfg in CONFIGS:
    _cfg["rounds"] = pack_rounds(_cfg)
    _cfg.setdefault("round_role", "flex")
    _cfg["paths"] = compute_paths(_cfg)
