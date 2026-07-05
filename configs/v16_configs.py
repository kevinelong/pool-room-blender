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
# v26: per user — the Emergency Exit and storage doors need LESS frontage
# than the kitchen door (which sees carts and tray traffic all night).
# EE band trimmed to 36"; the kitchen frontage is the deep one (54").
EXIT_FRONTAGE = (24, 646, 101, 682)

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


# v26: every 2x3 layout gets a bar two-top on BOTH walls, aligned with each
# table row's END LINES (the tables' north/south short sides), pushed
# against the wall; each top's two stools sit north and south, facing it.
# East-wall exceptions: the row-2 north end nudges 4" south to clear the
# HVAC chase; the row-3 south end is SKIPPED (it would sit in the sunken
# Main Entry well); the top by the kitchen door partially fronts it —
# user-accepted, noted.
TT_ROW_ENDS = [233.5, 326.0, 392.0, 484.5, 537.0, 629.5]
TWOTOPS_2X3 = ([(12.0, y) for y in TT_ROW_ENDS]
               + [(304.0, y) for y in (233.5, 326.0, 396.0, 484.5, 537.0)])

CONFIGS = [
    dict(
        key="social",
        name="1 · Social Hall",
        tagline="The built layout: six tables, wall two-tops, north quincunx",
        tables=_rows(ROWS_CURRENT),
        # v26: four aligned north rounds + a central fifth in PLUS chair
        # orientation (user) — the quincunx is deliberately tight, so the
        # grid fill is off and the fifth is forced
        rounds=[], hightops=[],
        rounds_forced=[(105.0, 47.0), (211.0, 47.0), (105.0, 143.0),
                       (211.0, 143.0), (158.0, 95.0)],
        rounds_plus=[(158.0, 95.0)],
        pack_grid=False,
        round_role="flex",
        twotops=TWOTOPS_2X3,
        twotop_role="flex",
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=0,
        notes=[
            "The room as built — the baseline every option is judged against.",
            "Wall two-tops at every table end flex between drinkers, "
            "eaters, and spectators; stools face the tops.",
            "The center round of the north quincunx runs tight to its four "
            "neighbours — deliberate, for one big social cluster.",
            "The two-top by the kitchen door partially fronts it (accepted).",
        ],
    ),
    dict(
        key="tournament",
        name="2 · Tournament House",
        tagline="North gallery of five rounds faces the feature row",
        tables=_rows(ROWS_CURRENT),
        # v26: bleachers removed (user) — the gallery is five 5-ft rounds:
        # four aligned + the same forced center round as Social
        rounds=[],   # auto-packed below
        rounds_forced=[(105.0, 47.0), (211.0, 47.0), (105.0, 143.0),
                       (211.0, 143.0), (158.0, 95.0)],
        rounds_plus=[(158.0, 95.0)],
        round_role="flex",
        hightops=[],
        twotops=TWOTOPS_2X3,
        twotop_role="drink",
        rails=[],
        bench=False, bench_role=None,
        classroom=False,
        bleachers=[],
        stage_seats=0,
        flip_minutes=10,
        notes=[
            "Five rounds pack the cleared north end and face the feature "
            "row — gallery seating without bleachers.",
            "Food drops to handhelds while racks are in play.",
            "The two-top by the kitchen door partially fronts it (accepted).",
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
        aisle_x=65.0,    # v26: feeder aisle east of the west hightop file
        # v26: the spine moves inboard — an east-wall lane threaded a 16"
        # squeeze between the east hightops (path audit); it now runs
        # between the table ends and the hightop file
        lane_x=241.0,
        hightops=([(25, cy) for cy in
                   (97.75, 198.75, 299.75, 400.75, 501.75, 590)]
                  + [(291, cy) for cy in
                     (97.75, 198.75, 265, 410, 501.75, 545)]),
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
        # v26: the sixth round moves IN LINE with the column (user), on
        # table 6's centerline — it pinches the Emergency Exit approach,
        # which is accepted and called out below
        aisle_x=110.0,   # v26: feeder aisle between the round line and tables
        rounds=[],   # auto-packed below
        rounds_forced=[(47.0, 602.75)],
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=20,
        notes=[
            "The west side becomes a 9-ft hospitality strip the full length "
            "of the room — six rounds in one line, each on its table's "
            "centerline.",
            "FLAG: the sixth (south) round partially narrows the Emergency "
            "Exit approach — the corridor bends around it.",
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
        # v26: ALL SIX tables get their round (user). Rows 1-3 and 5 reach
        # the wall (row 3 partially fronts the kitchen door — accepted,
        # noted); row 4 pulls inboard of the HVAC chase; row 6 is forced
        # inboard beside the entry well and crowds the Main Entry approach
        # — accepted, noted.
        rounds=[],   # auto-packed below
        rounds_forced=[(228.3, 602.75)],
        round_role="flex",
        twotops=[], hightops=[],
        rails=[],
        bench=False, bench_role=None,
        classroom=False, bleachers=[], stage_seats=0,
        flip_minutes=25,
        notes=[
            "Each of the six tables gets its own 5-ft round at matching "
            "height on the east side — table service at arm's reach.",
            "FLAG: the sixth (south) round crowds the Main Entry approach "
            "beside the stair rail.",
            "FLAG: the third round sits partially in front of the kitchen "
            "door (user-accepted).",
            "The fourth round pulls inboard of the HVAC chase.",
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
# v26: chair-aware collision model, X orientation. The 4 hotel stacking
# chairs (11x12") now sit at the DIAGONALS (user: X shape, not +), still
# reaching ~46" from the round's center along the diagonal directions.
#   ROUND_RING     bounding radius incl. chairs — walls, doors, path clips
#   ROUND_BODY     disc + tucked-chair radius — furniture/table margins
#   ROUND_MIN_CC   floor for any two rounds (axis-aligned packing OK —
#                  X chairs interleave between axis neighbours)
#   ROUND_DIAG_CC  floor when two rounds face chair-to-chair diagonally
ROUND_RING = 46.0
ROUND_BODY = 38.0          # chairs pushed in tuck to ~38" from center
ROUND_MIN_CC = 84.0
ROUND_DIAG_CC = 96.0       # 46+46 diagonal chair reach + air
ROUND_DIAG_BAND = 34.0     # |dx-dy| band where the diagonal rule applies

# Two keep-out tiers. Life-safety egress is checked against the FULL chair
# ring — a chair leg in an exit path is an egress obstruction. Service
# frontages and the HVAC chase are checked against the tucked-chair body.
# v26: kitchen keeps the deepest frontage (54"); EE and storage doors get
# less (user). Wall rounds MAY partially front the kitchen door — allowed
# for the per-table aligned rounds and noted in the layout notes.
KITCHEN_FRONT = (262, 282, 316, 338)   # kitchen door frontage, 54" deep
KEEPOUTS_EGRESS = [
    (250, 596, 316, 682),   # Main Entry well + rails + approach
    EXIT_FRONTAGE,          # Emergency Exit corridor (36", v26)
]
KEEPOUTS_FRONTAGE = [
    KITCHEN_FRONT,
    (268, 0, 316, 36),      # Storage A door frontage (N wall, east end)
    (280, 0, 316, 42),      # Storage B door frontage (E wall, north end)
    HVAC,
]
KEEPOUTS = KEEPOUTS_EGRESS + KEEPOUTS_FRONTAGE   # for path clipping et al.
ENTRY_WELL = (276, 612, 316, 682)   # sunken entry: floor cut, treads, landing


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
        # v26: a mandated per-table round may partially front the kitchen
        # door (user-accepted, noted in the layout notes)
        if aligned and ko is KITCHEN_FRONT:
            continue
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
        # v26: chairs sit on the diagonals, so DIAGONAL neighbours face
        # chair-to-chair and need the wider spacing; axis-aligned
        # neighbours interleave safely at the disc minimum
        if abs(dx - dy) < ROUND_DIAG_BAND and \
                dx * dx + dy * dy < ROUND_DIAG_CC ** 2:
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
    # 0) user-mandated rounds are placed unconditionally (their compromises
    #    — pinched exit approach, entry-well crowding, tight quincunx —
    #    are deliberate and called out in the layout notes)
    placed = [(float(px), float(py)) for px, py in cfg.get("rounds_forced", [])]
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
    # 2) greedy grid fill of everything else (configs with a hand-set
    #    round count — e.g. social's quincunx — turn this off)
    if cfg.get("pack_grid", True):
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
    """Green staff pathways: a service spine, door stubs, and per-seat
    feeders. v26: a feeder NEVER crosses a pool table — when a straight
    run is blocked it turns down the near-side aisle and crosses through
    the gap BETWEEN tables. Strips still clip around every obstacle (and
    the entry-well floor cut). Returns floor rects."""
    lane_x = cfg.get("lane_x", 298.0)
    rot = cfg.get("rot90", False)
    trects = [table_rect(tx, ty, rot) for _n, tx, ty in cfg["tables"]]
    obs = list(trects)
    obs += [(cx - ROUND_RING, cy - ROUND_RING, cx + ROUND_RING, cy + ROUND_RING)
            for cx, cy in cfg.get("rounds", [])]
    obs += [(hx - 26, hy - 29, hx + 26, hy + 29)
            for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", []))]
    obs += [HVAC] + list(cfg.get("bleachers", []))
    # v25: the Main Entry well is a real floor cut (two treads down to the
    # landing) — painted path must stop at the top step, not float over it
    obs += [ENTRY_WELL]

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

    # --- gaps between table rows: the legal service crossings -------------
    ivals = sorted((t[1], t[3]) for t in trects)
    merged = []
    for a, b in ivals:
        if merged and a <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    gaps = []
    prev = 40.0
    for a, b in merged:
        if a - prev >= 32:
            gaps.append((prev, a))
        prev = b
    if 682 - prev >= 32:
        gaps.append((prev, 682.0))

    def _tables_block(x0, y0, x1, y1):
        return any(_rect_overlap((x0, y0, x1, y1), t) for t in trects)

    def _cross_y(cy):
        """Pick a y to cross the room at: inside the nearest gap, nudged
        until the crossing strip is clear of everything but wall trim."""
        if not gaps:
            return cy
        g = min(gaps, key=lambda g_: abs((g_[0] + g_[1]) / 2 - cy))
        lo, hi = g[0] + 12, g[1] - 12
        cands = sorted({max(lo, min(hi, cy)), (lo + hi) / 2, lo, hi},
                       key=lambda v: abs(v - cy))
        return cands[0] if cands else (g[0] + g[1]) / 2

    aisle_x = cfg.get("aisle_x", 52.0)

    def feeder(edge_x, cy):
        """Route from a seat's lane-side edge to the spine. Straight when
        clear; otherwise turn down the aisle and cross between tables."""
        a, b = sorted((edge_x, lane_x))
        if not _tables_block(a, cy - 10, b, cy + 10):
            return clip_strip(a, cy - 10, b, cy + 10)
        gy = _cross_y(cy)
        out = []
        aa, ab = sorted((edge_x, aisle_x))
        out += clip_strip(aa, cy - 10, ab + 10, cy + 10)          # to aisle
        ya, yb = sorted((cy, gy))
        out += clip_strip(aisle_x - 10, ya - 10, aisle_x + 10, yb + 10)
        ca, cb = sorted((aisle_x, lane_x))
        out += clip_strip(ca, gy - 10, cb, gy + 10)               # crossing
        return out

    paths = []
    paths += clip_strip(lane_x - 12, 30, lane_x + 12, 660)       # spine
    # ME approach runs along the well's NORTH curb to the top step
    paths += clip_strip(min(lane_x - 12, 250), 588, 316, 612)    # ME stub
    paths += clip_strip(min(lane_x, 290), 298, 316, 322)         # kitchen stub
    # v26: the EE link rides the south-wall band (it used to cut straight
    # across the table field), bridged to the ME stub west of the well
    paths += clip_strip(50, 645, 276, 669)                       # S corridor
    paths += clip_strip(254, 612, 274, 669)                      # bridge
    paths += clip_strip(50, 646, 74, 682)                        # EE stub
    for cx, cy in cfg.get("rounds", []):
        edge = cx + ROUND_RING if cx < lane_x else cx - ROUND_RING
        paths += feeder(edge, cy)
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        edge = hx + 26 if hx < lane_x else hx - 26
        paths += feeder(edge, hy)
    return paths


# post-process: pack rounds into every config, then freeze
for _cfg in CONFIGS:
    _cfg["rounds"] = pack_rounds(_cfg)
    _cfg.setdefault("round_role", "flex")
    _cfg["paths"] = compute_paths(_cfg)
