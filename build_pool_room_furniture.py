"""
ADD-ON SCRIPT v3 -- discrete textured furniture & real Blender lights.

Run AFTER build_pool_room.py. Adds, in dedicated Outliner collections:

  Pool_Tables           - 6 Diamond 7-ft tables (felt-textured beds + wood rails)
                          Layout: 2x1 columns along the room's long axis, 60"
                          apart, centered short-way.  2 in the back room, 4 in
                          the main room.
  Classroom_Tables      - 2x2 classroom tables with chairs facing pool tables
  Two_Tops              - 6 wall-side two-tops (3L + 3R)
  Bench_Seating         - long bench between entry steps and emergency exit
  Lockers_Shelving      - 4 back-wall lockers
  HVAC_Equipment        - left-wall HVAC chase
  Partition_Stow        - retractable partition column at beam, right wall
  Wrought_Iron_Railing  - 2 short railings flanking entry steps
  Pendant_Fixtures      - 6 hanging pool-table pendants (mesh shade + rod)
  Ceiling_Troffers      - 2x4 suspended-ceiling troffers (mesh frame + lens)
  Lights                - REAL Blender lights:
                            * 1 AREA per pool table (pendant downlight)
                            * AREA per troffer (diffused ceiling fill)

Textures
--------
The shell script (build_pool_room.py) created these materials in the .blend:
    MAT_pool_felt   - Diamond blue felt
    MAT_wood_panel  - dark walnut paneling
    MAT_wood_beam   - rough-sawn beam
    MAT_white_plank - white-painted plank siding
    MAT_cmu_wall    - painted CMU
    MAT_ceiling_tile- acoustic 2x2 tile
    MAT_vct_floor   - 12" brown VCT
We reuse those materials here so pool tables get real felt, table tops get
panel/beam wood, etc.  If a material is missing (script run standalone) we
fall back to a tinted Principled BSDF.
"""
import bpy
import math
from mathutils import Vector

IN = 0.0254


# ---------- floor plan constants (must match pool_v11.py / build_pool_room.py)
ROOM_W = 316
ROOM_L = 682
CEIL_H = 108
BEAM_Y = 332
BEAM_BOTTOM = CEIL_H - 12   # 96"

# Pool tables: Diamond Pro-Am 7ft derived from 8ft reference model (v15i).
# Reference: 3ds Max V-Ray Diamond Pro-Am 8ft file supplied by user.
#   8ft real spec: 88" x 44" playfield, 7.25" K-66 rails, 10" wedge corner
#   caps, 5" tapered legs.
# User rule: scale playfield ONLY from 8ft (88x44) to 7ft (78x39).
#   Rail cross-section stays 7.25" (K-66 profile, physical hardware).
#   Corner pocket caps stay 10" (physical castings, not scaled).
#   Legs stay 5" x 5" tapered (physical hardware, not scaled).
# Cabinet becomes: 78 + 2*7.25 = 92.5" long, 39 + 2*7.25 = 53.5" wide.
PLAY_L = 78.0           # v15i: authentic 7ft playfield length (was implicit ~79.5)
PLAY_W = 39.0           # v15i: authentic 7ft playfield width  (was implicit ~39.5)
RAIL_W = 7.25           # K-66 rail cross-section (unchanged from 8ft)
TBL_W = PLAY_W + 2 * RAIL_W   # 53.5"
TBL_L = PLAY_L + 2 * RAIL_W   # 92.5"
TBL_H = 32
TBL_SPACING = 60        # 5 ft between tables

# 2x1 grid centered on X (short axis), tables run long-ways (length along Y).
# Two columns of tables, 60" apart, centered in the 316" wide room.
pair_total_w = TBL_W + TBL_SPACING + TBL_W           # 152
margin_x = (ROOM_W - pair_total_w) / 2               # 82
xL_center = margin_x + TBL_W / 2                     # 105
xR_center = ROOM_W - margin_x - TBL_W / 2            # 211

# Back room (Y = 0..BEAM_Y, length 332"): 1 pair (2 tables), 60" from beam.
# v6: back tables shifted south to match the 5-ft (60") partition gap of the
# main-room tables. back_row_top = BEAM_Y - TBL_SPACING - TBL_L = 332-60-85 = 187
# v12: bottom (back-room) pool tables moved south ~5 ft to almost touch beam.
# Was 187 (60" gap to beam); now 241 (6" gap to beam @ Y=332).
back_row_top = BEAM_Y - 6 - TBL_L                    # 241 (v12: 5-ft shift south)
back_margin_y = back_row_top                         # legacy alias

# Main room (Y = BEAM_Y..ROOM_L, length 350"): 2 pairs (4 tables).
# v7: bottom (south) pair moved as close to partition as possible.
# MainA stays 60" from beam. MainB is now 60" from MainA (5 ft aisle).
main_len = ROOM_L - BEAM_Y                            # 350
main_row1_top = BEAM_Y + 60                           # 392 (60" from beam)
main_row2_top = main_row1_top + TBL_L + TBL_SPACING  # 537 (60" aisle between rows)
# Note: this keeps MainA at 60" from beam and MainB at 60" from MainA,
# which is already as tight as the spec allows. The 5-ft (60") rail spacing
# is the user-defined minimum and prevents collision with MainA's cushion.

POOL_TABLES = [
    # Back room (2)
    ("BackL",  xL_center, back_row_top),
    ("BackR",  xR_center, back_row_top),
    # Main room (4)
    ("MainAL", xL_center, main_row1_top),
    ("MainAR", xR_center, main_row1_top),
    ("MainBL", xL_center, main_row2_top),
    ("MainBR", xR_center, main_row2_top),
]

# Classroom tables (back room, north end behind the back pair)
CLASS_LEN  = 96
# v12: bumped depth to realistic training-table depth (was 20", real ~24-30")
CLASS_W    = 24
# v13: CLASS_GAP_Y increased so the second (north) row of chairs is not jammed
# between the two table backs. Was 14 (=> 2" pull-out behind 12" chair). Now 26
# (=> 14" pull-out behind chair).
CLASS_GAP_X = 12
CHAIR_W = 11
CHAIR_D = 12
CHAIR_H = 32
SEAT_H  = 17
CHAIRS_PER_TABLE = 4
# v15c: classroom reshaped to 2 cols x 3 rows deep (6 tables, same count).
# Tables now 96" long (was 76" to fit 3 cols). Narrower X footprint means the
# east service lane no longer has to wrap around the classroom — it can run
# straight through x=265..295 with the classroom centered at x=56..260.
N_PER_ROW = 2
N_ROWS    = 3
CLASS_LEN = 96
total_row_len  = N_PER_ROW * CLASS_LEN + (N_PER_ROW - 1) * CLASS_GAP_X   # 2*96 + 12 = 204
class_row_x0   = (ROOM_W - total_row_len) / 2                           # (316-204)/2 = 56
# v15c: keep front-row clearance to BackL/BackR (36") and stack 3 rows north.
# Per user: tables may touch stage (stage y=0..48) if necessary; row 2 back
# chairs land at y~63..75 — comfortably clear of the stage.
CLASS_FRONT_BOUND = back_row_top - 36      # 36" / 3 ft clearance to BackL/R
CLASS_GAP_Y = 14                            # chair-back to next table front
# Row 0 = front (south, closest to pool tables); Row N_ROWS-1 = back (north).
CLASS_ROW_PITCH = CLASS_W + 2 + CHAIR_D + CLASS_GAP_Y   # 24+2+12+14 = 52
front_table_bottom_y = CLASS_FRONT_BOUND
front_table_top_y    = front_table_bottom_y - CLASS_W
front_chair_top_y    = front_table_top_y - 2 - CHAIR_D
# Back-most row (used by the path-planner for north-wrap clearance).
back_table_bottom_y  = front_table_bottom_y - (N_ROWS - 1) * CLASS_ROW_PITCH
back_table_top_y     = back_table_bottom_y - CLASS_W
back_chair_top_y     = back_table_top_y - 2 - CHAIR_D

# Bench (v6: NORTH wall, opposite south front-entry).
# v15b: bench RESTORED next to NW stage and clear of Storage A door.
#   Stage occupies x=0..96 at the NW corner; Storage A door is on the N wall
#   at x=276..312. Place bench between them with 6" gaps each side:
#   x0 = 96 + 6 = 102; x1 = 276 - 6 = 270 -> 168" long bench.
LANDING_DEPTH = 18
STAIR_TREAD = 11
STAIR_RUN_X = LANDING_DEPTH + 2 * STAIR_TREAD     # 40"
BENCH_DEPTH = 18
BENCH_H = 18
bench_x0 = 102                                    # 6" east of NW stage
bench_x1 = 270                                    # 6" west of Storage A door (276..312)
bench_y0 = 0                                      # north wall (image-bottom)

# Two-tops
# v15j: two-tops converted to bar/pub height per user reference (Revit family
#   "Chair_Stool_Bar_4_Legs_BackSeat"). Tables raise from 30" to 42", chairs
#   become 4-leg bar stools with back + seat, seat top at 30".
TWOTOP_W = 18
TWOTOP_L = 14
TWOTOP_H = 42                # v15j: bar/pub height (was 30)
TWOTOP_SEAT_H = 30           # v15j: bar-stool seat top (was implicit SEAT_H=17)
TWOTOP_CHAIR_TOTAL_H = 45    # v15j: total stool height incl. backrest (was CHAIR_H=32)

# HVAC chase (v7: moved from left wall to RIGHT wall, above beam)
HVAC_W  = 28
HVAC_L  = 42
HVAC_H_VOL = CEIL_H
HVAC_X = 316 - HVAC_W                              # right wall (ROOM_W - HVAC_W) = 288
HVAC_Y0 = 332 + 6                                  # just south of beam

# Partition stow column (right wall at beam)
STOW_W = 16
STOW_L = 22
STOW_H_VOL = BEAM_BOTTOM

# Lockers (back wall)
# v15k: authentic locker dimensions per user product reference.
# Ball storage locker: 24W x 18D x 72H (3-zone: locked top / open ball display / locked bottom).
# Triple locker:      36W x 18D x 72H (3 vertical narrow doors with key latches, vents top+bot).
BALL_LOCKER_W = 24
TRIPLE_LOCKER_W = 36
LOCKER_L = 18
LOCKER_H = 72
LOCKER_W = BALL_LOCKER_W   # legacy alias (used by any other code that references it)

# Pool-table pendants -- long axis aligned with the table's long axis (Y)
# (rotated 90 from the original cross-wise orientation)
PEND_W = 18      # X (short, across the table's width)
PEND_L = 60      # Y (long, along the table's length)
PEND_H = 8
PEND_Z = CEIL_H - 36                              # bottom of shade at 72" AFF

# Wrought-iron entry railings
ENTRY_Y0 = ROOM_L - 74
ENTRY_Y1 = ROOM_L
RAIL_H = 36
RAIL_T = 2

# Suspended-ceiling troffer grid (2'x4' fixtures, set into 2'x2' ACT grid).
# Skip cells too close to the beam, HVAC chase, partition column or pendants.
TROFFER_W = 24                          # 2'
TROFFER_L = 48                          # 4'
TROFFER_H = 4                           # 4" shallow housing


# ============================================================================
# HELPERS
# ============================================================================

def get_or_create_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def move_to_collection(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def get_or_create_color_material(name, rgba, roughness=0.7, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
            bsdf.inputs["Roughness"].default_value = roughness
            if emission is not None and "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif emission is not None and "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
    return mat


def get_material(name, fallback_rgba=(0.7, 0.7, 0.7, 1.0), fallback_roughness=0.7):
    """Return an existing material (built by the shell script) or a fallback."""
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    return get_or_create_color_material("fallback_" + name, fallback_rgba, fallback_roughness)


def make_box(name, x, y, z, w, l, h,
             color=(0.7, 0.7, 0.7, 1.0),
             material=None,
             collection=None,
             roughness=0.7,
             emission=None,
             emission_strength=0.0):
    """Box at world corner (x,y,z) sized (w,l,h) in inches."""
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(IN * (x + w / 2), IN * (y + l / 2), IN * (z + h / 2))
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (IN * w, IN * l, IN * h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        mat = material
    else:
        mat = get_or_create_color_material(name + "_mat", color, roughness,
                                           emission=emission,
                                           emission_strength=emission_strength)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    if collection:
        move_to_collection(obj, collection)
    return obj


def add_area_light(name, x_in, y_in, z_in, size_w_in, size_l_in,
                   color=(1.0, 0.92, 0.78), energy=200.0, collection=None):
    """Add a rectangular AREA light pointing -Z (down) at the given inch coords."""
    bpy.ops.object.light_add(
        type='AREA',
        location=(IN * x_in, IN * y_in, IN * z_in)
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.shape = 'RECTANGLE'
    obj.data.size = IN * size_w_in
    obj.data.size_y = IN * size_l_in
    obj.data.color = color
    obj.data.energy = energy
    if collection:
        move_to_collection(obj, collection)
    return obj


# ============================================================================
# POOL TABLES (textured)
# ============================================================================

def build_pool_table(name, cx, ty_top, coll):
    """v15i: authentic Diamond Pro-Am 7ft derived from 8ft V-Ray reference.
    Outer footprint 53.5" W x 92.5" L x 32" H. Play area 39" x 78" (real 7ft spec).
    Hardware (rail cross-section 7.25", corner caps 10", tapered legs 5") is
    physical Diamond hardware and stays identical to the 8ft version - only the
    playfield/cabinet length+width scaled 8ft (88x44) -> 7ft (78x39).

    Built from reference photos of the actual Diamond Pro-Am 7ft Charcoal cabinet:
      - Massive 7.25" wide rails (K-66 profile) in charcoal Dymondwood
      - Wedge-block corner pocket housings that are wider than the rails
        (the iconic shape that flares outward at the table corners)
      - Pocket throats as recessed dark slots in the corner caps
      - Side-rail pocket cutouts
      - Square TAPERED solid wood legs (wider at top, slight taper to foot)
        with bevelled tops where they meet the rail (visible corner cleats)
      - Cabinet apron between legs (the dark skirt that hangs to ~apron line)
      - Apron ball-return cutouts (small dark rectangles) on long sides
      - Charcoal Dymondwood color: very dark warm gray, subtle blue undertone
      - DIAMOND-shape (rotated square) inlaid sights, mother-of-pearl color
      - Feather strip + slate-edge bevel below the rail nose
      - Leveling toe (black metal foot) at the bottom of each leg
    """
    # ---- Materials ------------------------------------------------------
    felt_mat = bpy.data.materials.get("Pool_Felt")
    if felt_mat is None:
        felt_mat = get_or_create_color_material(
            "MAT_pool_felt_fallback", (0.06, 0.22, 0.10, 1.0), roughness=0.85)
    # Charcoal Dymondwood - near-black with subtle warm undertone (matches
    # authentic Diamond Pro-Am Charcoal reference photos). Use slightly higher
    # values than (0.04) because the bright room ambient washes very-dark
    # surfaces. Real Dymondwood reads as #1a1518 ~ (0.01, 0.008, 0.009) under
    # studio lighting; bumped to ~ 0.022 for sRGB Cycles ambient compensation.
    rail_mat = get_or_create_color_material(
        "MAT_pool_rail", (0.022, 0.020, 0.022, 1.0), roughness=0.32)
    # Cabinet apron darker than rails (subdued shadow underside)
    apron_mat = get_or_create_color_material(
        "MAT_pool_apron", (0.014, 0.013, 0.015, 1.0), roughness=0.55)
    # Leg blocks - matching the rail Dymondwood
    leg_mat = get_or_create_color_material(
        "MAT_pool_leg", (0.022, 0.020, 0.022, 1.0), roughness=0.4)
    # Pocket throat (black leather/plastic recessed slot)
    pocket_throat_mat = get_or_create_color_material(
        "MAT_pool_pocket_throat", (0.012, 0.012, 0.012, 1.0), roughness=0.85)
    # Pocket leather ring (dark brown)
    leather_mat = get_or_create_color_material(
        "MAT_pool_pocket_leather", (0.05, 0.035, 0.025, 1.0), roughness=0.7)
    # Mother-of-pearl diamond sight color
    sight_mat = get_or_create_color_material(
        "MAT_pool_sight", (0.94, 0.93, 0.88, 1.0), roughness=0.25)
    # Feather strip (slightly warm dark band between cushion and bed)
    feather_mat = get_or_create_color_material(
        "MAT_pool_feather", (0.10, 0.07, 0.04, 1.0), roughness=0.5)
    # Slate edge (visible just below feather strip) - keep dark/subtle
    slate_edge_mat = get_or_create_color_material(
        "MAT_pool_slate_edge", (0.08, 0.08, 0.085, 1.0), roughness=0.85)
    # Leveling foot (black painted metal)
    foot_mat = get_or_create_color_material(
        "MAT_pool_foot", (0.02, 0.02, 0.02, 1.0), roughness=0.6)

    # ---- Geometry constants (matched to real Diamond Pro-Am 7ft) -------
    x0 = cx - TBL_W / 2
    y0 = ty_top
    x1 = x0 + TBL_W
    y1 = y0 + TBL_L

    RAIL_W = 7.25                  # authentic massive K-66 rail width
    BED_THICK = 1.0                # 1" slate
    RAIL_H = 3.5                   # rail block height above the slate
    FEATHER_H = 0.5                # feather strip height
    SLATE_EDGE_H = 0.4             # visible slate edge below feather (subtle)

    # Corner cap is the wedge block at each corner that houses the pocket.
    # In real Diamond it's WIDER than the rail (flares out) and ~10" along
    # each rail direction.
    CAP_LEN = 10.0                 # length of cap along each rail
    CAP_FLARE = 1.25               # how far the cap extends OUT past the rail
    # Side-pocket cap (mid of long rail) is similar but narrower flare
    SIDE_CAP_LEN = 9.0
    SIDE_CAP_FLARE = 1.0

    bed_top_z = TBL_H              # 32" - top of the slate
    rail_top_z = bed_top_z + RAIL_H

    # ---- 1) Slate edge band (visible dark gray sliver beneath rails) ----
    se_z = bed_top_z - BED_THICK
    make_box(f"PoolTable_{name}_SlateEdge_S",
             x=x0 + RAIL_W - 0.4, y=y0 + RAIL_W - 0.4, z=se_z + BED_THICK - SLATE_EDGE_H,
             w=TBL_W - 2 * RAIL_W + 0.8, l=0.4, h=SLATE_EDGE_H,
             material=slate_edge_mat, collection=coll)
    make_box(f"PoolTable_{name}_SlateEdge_N",
             x=x0 + RAIL_W - 0.4, y=y1 - RAIL_W, z=se_z + BED_THICK - SLATE_EDGE_H,
             w=TBL_W - 2 * RAIL_W + 0.8, l=0.4, h=SLATE_EDGE_H,
             material=slate_edge_mat, collection=coll)
    make_box(f"PoolTable_{name}_SlateEdge_W",
             x=x0 + RAIL_W - 0.4, y=y0 + RAIL_W, z=se_z + BED_THICK - SLATE_EDGE_H,
             w=0.4, l=TBL_L - 2 * RAIL_W, h=SLATE_EDGE_H,
             material=slate_edge_mat, collection=coll)
    make_box(f"PoolTable_{name}_SlateEdge_E",
             x=x1 - RAIL_W, y=y0 + RAIL_W, z=se_z + BED_THICK - SLATE_EDGE_H,
             w=0.4, l=TBL_L - 2 * RAIL_W, h=SLATE_EDGE_H,
             material=slate_edge_mat, collection=coll)

    # ---- 2) Slate bed with FELT (top surface, play area) ----------------
    make_box(f"PoolTable_{name}_FeltBed",
             x=x0 + RAIL_W, y=y0 + RAIL_W, z=bed_top_z - BED_THICK,
             w=TBL_W - 2 * RAIL_W, l=TBL_L - 2 * RAIL_W, h=BED_THICK,
             material=felt_mat, collection=coll)

    # ---- 3) Feather strip (dark band between cushion and bed) -----------
    f_z = bed_top_z + 0.02
    make_box(f"PoolTable_{name}_FeatherS",
             x=x0 + RAIL_W, y=y0 + RAIL_W - 0.4, z=f_z,
             w=TBL_W - 2 * RAIL_W, l=0.4, h=FEATHER_H,
             material=feather_mat, collection=coll)
    make_box(f"PoolTable_{name}_FeatherN",
             x=x0 + RAIL_W, y=y1 - RAIL_W, z=f_z,
             w=TBL_W - 2 * RAIL_W, l=0.4, h=FEATHER_H,
             material=feather_mat, collection=coll)
    make_box(f"PoolTable_{name}_FeatherW",
             x=x0 + RAIL_W - 0.4, y=y0 + RAIL_W, z=f_z,
             w=0.4, l=TBL_L - 2 * RAIL_W, h=FEATHER_H,
             material=feather_mat, collection=coll)
    make_box(f"PoolTable_{name}_FeatherE",
             x=x1 - RAIL_W, y=y0 + RAIL_W, z=f_z,
             w=0.4, l=TBL_L - 2 * RAIL_W, h=FEATHER_H,
             material=feather_mat, collection=coll)

    # ---- 4) Main rails (between corner caps and side caps) --------------
    # SOUTH rail = two segments either side of the south side-cap
    long_seg = (TBL_L - 2 * CAP_LEN - SIDE_CAP_LEN) / 2
    # SHORT rails (S and N) - run along X, between two corner caps
    short_seg_x = TBL_W - 2 * CAP_LEN
    if short_seg_x > 0:
        make_box(f"PoolTable_{name}_RailS",
                 x=x0 + CAP_LEN, y=y0, z=bed_top_z,
                 w=short_seg_x, l=RAIL_W, h=RAIL_H,
                 material=rail_mat, collection=coll)
        make_box(f"PoolTable_{name}_RailN",
                 x=x0 + CAP_LEN, y=y1 - RAIL_W, z=bed_top_z,
                 w=short_seg_x, l=RAIL_W, h=RAIL_H,
                 material=rail_mat, collection=coll)
    # LONG rails (W and E) - run along Y, split by side-pocket cap
    if long_seg > 0:
        make_box(f"PoolTable_{name}_RailW_S",
                 x=x0, y=y0 + CAP_LEN, z=bed_top_z,
                 w=RAIL_W, l=long_seg, h=RAIL_H,
                 material=rail_mat, collection=coll)
        make_box(f"PoolTable_{name}_RailW_N",
                 x=x0, y=y1 - CAP_LEN - long_seg, z=bed_top_z,
                 w=RAIL_W, l=long_seg, h=RAIL_H,
                 material=rail_mat, collection=coll)
        make_box(f"PoolTable_{name}_RailE_S",
                 x=x1 - RAIL_W, y=y0 + CAP_LEN, z=bed_top_z,
                 w=RAIL_W, l=long_seg, h=RAIL_H,
                 material=rail_mat, collection=coll)
        make_box(f"PoolTable_{name}_RailE_N",
                 x=x1 - RAIL_W, y=y1 - CAP_LEN - long_seg, z=bed_top_z,
                 w=RAIL_W, l=long_seg, h=RAIL_H,
                 material=rail_mat, collection=coll)

    # ---- 5) Corner-cap pocket housings (wedge blocks flaring outward) ----
    # Real Diamond corners are roughly square caps that extend ~1.25" out past
    # the rail face. Each cap is CAP_LEN x CAP_LEN, but extends OUT in the
    # rail's perpendicular direction.
    corners = [
        ("SW", x0 - CAP_FLARE, y0 - CAP_FLARE),
        ("SE", x1 - CAP_LEN + CAP_FLARE, y0 - CAP_FLARE),
        ("NW", x0 - CAP_FLARE, y1 - CAP_LEN + CAP_FLARE),
        ("NE", x1 - CAP_LEN + CAP_FLARE, y1 - CAP_LEN + CAP_FLARE),
    ]
    for lbl, ccx, ccy in corners:
        make_box(f"PoolTable_{name}_Cap_{lbl}",
                 x=ccx, y=ccy, z=bed_top_z,
                 w=CAP_LEN, l=CAP_LEN, h=RAIL_H,
                 material=rail_mat, collection=coll)
        # Pocket throat - recessed dark slot in the cap
        # angled toward the play area corner
        # Simplified as a small dark square recessed slightly on top
        throat_size = 4.5
        throat_inset = 1.5
        if lbl == "SW":
            tx, ty_t = ccx + CAP_LEN - throat_size - throat_inset, ccy + CAP_LEN - throat_size - throat_inset
        elif lbl == "SE":
            tx, ty_t = ccx + throat_inset, ccy + CAP_LEN - throat_size - throat_inset
        elif lbl == "NW":
            tx, ty_t = ccx + CAP_LEN - throat_size - throat_inset, ccy + throat_inset
        else:  # NE
            tx, ty_t = ccx + throat_inset, ccy + throat_inset
        # Recessed black opening
        make_box(f"PoolTable_{name}_Throat_{lbl}",
                 x=tx, y=ty_t, z=bed_top_z + RAIL_H - 0.3,
                 w=throat_size, l=throat_size, h=0.5,
                 material=pocket_throat_mat, collection=coll)

    # ---- 6) Side-pocket caps (mid of W and E long rails) ----------------
    mid_y = (y0 + y1) / 2 - SIDE_CAP_LEN / 2
    for side_lbl, side_x in (("W", x0 - SIDE_CAP_FLARE),
                              ("E", x1 - RAIL_W)):
        make_box(f"PoolTable_{name}_SideCap_{side_lbl}",
                 x=side_x, y=mid_y, z=bed_top_z,
                 w=RAIL_W + SIDE_CAP_FLARE, l=SIDE_CAP_LEN, h=RAIL_H,
                 material=rail_mat, collection=coll)
        # Throat in side cap
        if side_lbl == "W":
            tx = side_x + RAIL_W + SIDE_CAP_FLARE - 4.5
        else:
            tx = side_x + SIDE_CAP_FLARE
        make_box(f"PoolTable_{name}_SideThroat_{side_lbl}",
                 x=tx, y=mid_y + 1.5, z=bed_top_z + RAIL_H - 0.3,
                 w=3.0, l=SIDE_CAP_LEN - 3.0, h=0.5,
                 material=pocket_throat_mat, collection=coll)

    # ---- 7) Cabinet apron (skirt that hangs between the legs) -----------
    # The apron runs along the inside of the leg outer faces. Leg outer face
    # is at the table's outer edge, so apron is inset by leg_w/2 and a bit.
    LEG_OUTER_W = 5.0        # leg block top width (matches real Diamond)
    LEG_BOT_W = 4.0          # leg block bottom width (taper)
    APRON_INSET = 0.6        # apron is slightly inset from leg outer face
    APRON_H = 12.0           # apron height (hangs ~12" down from rail bottom)
    apron_top_z = bed_top_z - BED_THICK - SLATE_EDGE_H
    apron_bot_z = apron_top_z - APRON_H

    # Apron 4 sides - each is a thin slab between the two legs on that side
    # SOUTH apron
    make_box(f"PoolTable_{name}_Apron_S",
             x=x0 + LEG_OUTER_W - APRON_INSET,
             y=y0 + APRON_INSET, z=apron_bot_z,
             w=TBL_W - 2 * (LEG_OUTER_W - APRON_INSET),
             l=1.0, h=APRON_H,
             material=apron_mat, collection=coll)
    # NORTH apron
    make_box(f"PoolTable_{name}_Apron_N",
             x=x0 + LEG_OUTER_W - APRON_INSET,
             y=y1 - APRON_INSET - 1.0, z=apron_bot_z,
             w=TBL_W - 2 * (LEG_OUTER_W - APRON_INSET),
             l=1.0, h=APRON_H,
             material=apron_mat, collection=coll)
    # WEST apron
    make_box(f"PoolTable_{name}_Apron_W",
             x=x0 + APRON_INSET, y=y0 + LEG_OUTER_W - APRON_INSET,
             z=apron_bot_z,
             w=1.0, l=TBL_L - 2 * (LEG_OUTER_W - APRON_INSET), h=APRON_H,
             material=apron_mat, collection=coll)
    # EAST apron
    make_box(f"PoolTable_{name}_Apron_E",
             x=x1 - APRON_INSET - 1.0, y=y0 + LEG_OUTER_W - APRON_INSET,
             z=apron_bot_z,
             w=1.0, l=TBL_L - 2 * (LEG_OUTER_W - APRON_INSET), h=APRON_H,
             material=apron_mat, collection=coll)

    # Apron ball-return access cutouts (small horizontal black slots on
    # long sides, just below the slate edge) - one per long side
    bra_w = 6.0
    bra_h = 1.5
    bra_z = apron_top_z - bra_h - 1.5
    make_box(f"PoolTable_{name}_Apron_Slot_W",
             x=x0 + APRON_INSET - 0.05, y=(y0 + y1) / 2 - bra_w / 2,
             z=bra_z, w=0.15, l=bra_w, h=bra_h,
             material=pocket_throat_mat, collection=coll)
    make_box(f"PoolTable_{name}_Apron_Slot_E",
             x=x1 - APRON_INSET + 0.95, y=(y0 + y1) / 2 - bra_w / 2,
             z=bra_z, w=0.15, l=bra_w, h=bra_h,
             material=pocket_throat_mat, collection=coll)

    # ---- 8) Four square TAPERED legs ------------------------------------
    # Real Diamond legs: solid wood block, wider at top, slight taper to
    # bottom. Top edge is bevelled where it meets the rail. ~28" tall.
    leg_top_z = apron_top_z      # leg top flush with apron top
    leg_bot_z = 0                # ground
    leg_h = leg_top_z - leg_bot_z
    # We build the leg as a 5-segment box stack to approximate a taper
    # since make_box only does axis-aligned boxes. The visual result reads
    # as a tapered solid wood post when viewed from any angle.
    leg_corners = [
        ("SW", x0,           y0),
        ("SE", x1 - LEG_OUTER_W, y0),
        ("NW", x0,           y1 - LEG_OUTER_W),
        ("NE", x1 - LEG_OUTER_W, y1 - LEG_OUTER_W),
    ]
    N_SEG = 6
    for lbl, lx0, ly0 in leg_corners:
        for seg in range(N_SEG):
            frac_top = seg / N_SEG
            frac_bot = (seg + 1) / N_SEG
            seg_top_z = leg_top_z - frac_top * leg_h
            seg_bot_z = leg_top_z - frac_bot * leg_h
            # Width interpolates between LEG_OUTER_W (top) and LEG_BOT_W (bot).
            # Use the AVERAGE width for this slab to read as taper.
            avg_w = LEG_OUTER_W - (LEG_OUTER_W - LEG_BOT_W) * (frac_top + frac_bot) / 2
            # center the slab over the corner anchor
            center_x = lx0 + LEG_OUTER_W / 2
            center_y = ly0 + LEG_OUTER_W / 2
            make_box(f"PoolTable_{name}_Leg_{lbl}_seg{seg}",
                     x=center_x - avg_w / 2, y=center_y - avg_w / 2,
                     z=seg_bot_z,
                     w=avg_w, l=avg_w, h=seg_top_z - seg_bot_z,
                     material=leg_mat, collection=coll)
        # Leveling foot at bottom (small black metal block)
        center_x = lx0 + LEG_OUTER_W / 2
        center_y = ly0 + LEG_OUTER_W / 2
        foot_w = 3.0
        make_box(f"PoolTable_{name}_LegFoot_{lbl}",
                 x=center_x - foot_w / 2, y=center_y - foot_w / 2, z=0,
                 w=foot_w, l=foot_w, h=0.6,
                 material=foot_mat, collection=coll)

    # ---- 9) Diamond-shape sights (rotated squares) on rail tops --------
    # Real Diamond sights are small diamond-shape inlays. We approximate
    # with small cylinders (8 sides = diamond-ish) inset slightly into
    # the rail.
    sight_size = 0.40
    sight_h = 0.12
    sight_z = bed_top_z + RAIL_H + 0.005
    # Long-rail sights (W and E rails): 3 sights per half, skipping mid (side pocket)
    inner_y0 = y0 + CAP_LEN
    inner_y1 = y1 - CAP_LEN
    mid_y_center = (y0 + y1) / 2
    for frac in (1/8, 2/8, 3/8, 5/8, 6/8, 7/8):
        sy = inner_y0 + frac * (inner_y1 - inner_y0)
        if abs(sy - mid_y_center) < SIDE_CAP_LEN / 2 + 0.5:
            continue
        for side_x, lbl in ((x0 + RAIL_W / 2, "W"),
                            (x1 - RAIL_W / 2, "E")):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=IN * sight_size, depth=IN * sight_h,
                location=(IN * side_x, IN * sy, IN * sight_z),
                vertices=4,            # 4 vertices = diamond/square
            )
            s = bpy.context.active_object
            # rotate 45deg so it reads as a diamond from above
            s.rotation_euler = (0, 0, 0.7853981633974483)
            s.name = f"PoolTable_{name}_Sight_{lbl}_{frac:.3f}"
            if s.data.materials:
                s.data.materials[0] = sight_mat
            else:
                s.data.materials.append(sight_mat)
            move_to_collection(s, coll)

    # Short-rail sights (S and N): 3 sights per rail
    inner_x0 = x0 + CAP_LEN
    inner_x1 = x1 - CAP_LEN
    for frac in (0.25, 0.50, 0.75):
        sx = inner_x0 + frac * (inner_x1 - inner_x0)
        for lbl, sy in (("S", y0 + RAIL_W / 2),
                        ("N", y1 - RAIL_W / 2)):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=IN * sight_size, depth=IN * sight_h,
                location=(IN * sx, IN * sy, IN * sight_z),
                vertices=4,
            )
            s = bpy.context.active_object
            s.rotation_euler = (0, 0, 0.7853981633974483)
            s.name = f"PoolTable_{name}_Sight_{lbl}_{frac:.2f}"
            if s.data.materials:
                s.data.materials[0] = sight_mat
            else:
                s.data.materials.append(sight_mat)
            move_to_collection(s, coll)

    # ---- 10) Leather pocket rings (inside the throat openings) ---------
    # Subtle small torus rings to read as the pocket leather under each
    # throat opening - placed slightly below rail top
    pkt_r_outer = 2.2
    pkt_r_tube = 0.35
    pkts = [
        (x0 + 3.0,         y0 + 3.0),
        (x1 - 3.0,         y0 + 3.0),
        (x0 + 3.0,         y1 - 3.0),
        (x1 - 3.0,         y1 - 3.0),
        (x0 + 2.0,         (y0 + y1) / 2),
        (x1 - 2.0,         (y0 + y1) / 2),
    ]
    for i, (px, py) in enumerate(pkts):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=IN * pkt_r_outer,
            minor_radius=IN * pkt_r_tube,
            location=(IN * px, IN * py, IN * (bed_top_z + RAIL_H - 0.2)),
            major_segments=16,
            minor_segments=6,
        )
        pk = bpy.context.active_object
        pk.name = f"PoolTable_{name}_Leather_{i}"
        if pk.data.materials:
            pk.data.materials[0] = leather_mat
        else:
            pk.data.materials.append(leather_mat)
        move_to_collection(pk, coll)



# ============================================================================
# OTHER FURNITURE (now using textured materials where possible)
# ============================================================================

def build_classroom_table(name, x, y, length, depth, coll):
    """v15k: authentic FOLDING BANQUET TABLE per user Lifetime/Correll-style
    reference (folding-table.zip). White laminate top on TWO INVERTED-U
    BLACK TUBULAR STEEL leg frames (one at each short end), joined by
    a low horizontal cross-brace tube near the floor. Slim (~1.25") top
    with a subtle darker bullnose bumper along the front/back edges.
    Top-of-table Z stays at (CHAIR_H - 2) to preserve all existing
    clearances and chair heights."""
    # Off-white laminate top
    panel_mat = get_or_create_color_material(
        "MAT_class_top", (0.93, 0.91, 0.84, 1.0), roughness=0.38)
    # Matte-black tubular steel legs
    leg_mat = get_or_create_color_material(
        "MAT_class_leg", (0.022, 0.022, 0.026, 1.0), roughness=0.35)
    # Subtle cream/gray bullnose (T-mold vinyl edge banding)
    bump_mat = get_or_create_color_material(
        "MAT_class_bump", (0.78, 0.75, 0.68, 1.0), roughness=0.55)

    top_thick = 1.25
    top_z = CHAIR_H - 2 - top_thick   # top-of-table stays at CHAIR_H - 2
    # ---- Laminate top ----
    make_box(f"ClassTable_{name}_top",
             x=x, y=y, z=top_z,
             w=length, l=depth, h=top_thick,
             material=panel_mat, collection=coll)
    # ---- Vinyl bullnose bumper along front & back edges ----
    bump_h = top_thick + 0.15
    bump_l = 0.25
    make_box(f"ClassTable_{name}_bump_front",
             x=x, y=y - 0.05, z=top_z - 0.08,
             w=length, l=bump_l, h=bump_h,
             material=bump_mat, collection=coll)
    make_box(f"ClassTable_{name}_bump_back",
             x=x, y=y + depth - bump_l + 0.05, z=top_z - 0.08,
             w=length, l=bump_l, h=bump_h,
             material=bump_mat, collection=coll)
    # ---- Two inverted-U tubular leg frames (one at each short end) ----
    # Each frame = 2 vertical tubes + 1 horizontal cross-top tube (fixed to
    # underside of top). Tubes are ~1" square. Set slightly inset from the
    # short ends to look like a real folding table (legs never touch the
    # very edge because they hinge inward when folded).
    tube_w = 1.1                 # tube cross-section (square-ish)
    frame_inset_x = 2.5          # frame is this far in from the short end
    frame_inset_y = 1.5          # tubes are this far from the front/back edges
    frame_h = top_z              # vertical tubes span floor to top underside
    for (frame_label, frame_cx) in (
        ("W", x + frame_inset_x),
        ("E", x + length - frame_inset_x - tube_w),
    ):
        # Two vertical tubes (front + back leg of this frame)
        for (post_label, post_y) in (
            ("F", y + frame_inset_y),
            ("B", y + depth - frame_inset_y - tube_w),
        ):
            make_box(f"ClassTable_{name}_tube_{frame_label}{post_label}",
                     x=frame_cx, y=post_y, z=0,
                     w=tube_w, l=tube_w, h=frame_h,
                     material=leg_mat, collection=coll)
        # Horizontal cross-top tube joining the two vertical tubes (under top)
        make_box(f"ClassTable_{name}_crosstop_{frame_label}",
                 x=frame_cx, y=y + frame_inset_y,
                 z=frame_h - tube_w,
                 w=tube_w,
                 l=(depth - 2 * frame_inset_y),
                 h=tube_w,
                 material=leg_mat, collection=coll)
    # ---- Low horizontal cross-brace running LENGTH-wise near the floor ----
    # (This is the signature folding-table stretcher between the two H-frames.)
    brace_z = 3.5                 # 3.5" off the floor
    brace_length = length - 2 * (frame_inset_x + tube_w / 2)
    brace_x = x + frame_inset_x + tube_w / 2 - 0.4
    brace_y = y + depth / 2 - tube_w / 2
    make_box(f"ClassTable_{name}_stretcher",
             x=brace_x, y=brace_y, z=brace_z,
             w=brace_length + 0.8, l=tube_w, h=tube_w,
             material=leg_mat, collection=coll)


def build_round_table(name, cx, cy, diameter, coll):
    """v15L (updated): STACKING ROUND FOLDING TABLE per user SketchUp reference.
    User request: round-table TOP shares the classroom (folding banquet)
    surface -- same off-white laminate material (MAT_class_top), same 1.25"
    thickness, and the same T-mold bullnose ring around the edge (MAT_class_bump).
    Legs and X-brace remain chrome tubular steel with black plastic foot caps.
    """
    import math as _m
    import mathutils as _mu
    # SHARED with build_classroom_table (matches folding banquet surface)
    top_mat = get_or_create_color_material(
        "MAT_class_top", (0.93, 0.91, 0.84, 1.0), roughness=0.38)
    bump_mat = get_or_create_color_material(
        "MAT_class_bump", (0.78, 0.75, 0.68, 1.0), roughness=0.55)
    chrome_mat = get_or_create_color_material(
        "MAT_roundtbl_leg", (0.72, 0.72, 0.74, 1.0), roughness=0.28)
    black_plastic_mat = get_or_create_color_material(
        "MAT_roundtbl_foot", (0.05, 0.05, 0.06, 1.0), roughness=0.55)
    top_thick = 1.25                       # matches classroom top thickness
    top_z = CHAIR_H - 2 - top_thick        # top-of-table Z stays at CHAIR_H - 2
    top_r = diameter / 2.0
    # ---- Round laminate top (same MAT_class_top as folding banquet) ----
    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * top_r, depth=IN * top_thick, vertices=64,
        location=(IN * cx, IN * cy, IN * (top_z + top_thick / 2)))
    top_obj = bpy.context.active_object
    top_obj.name = f"RoundTbl_{name}_top"
    if top_obj.data.materials: top_obj.data.materials[0] = top_mat
    else: top_obj.data.materials.append(top_mat)
    # Shade smooth so the disc reads as a proper rounded top rather than
    # a faceted cylinder (mirrors the classroom-table look at the top corner).
    for p in top_obj.data.polygons:
        p.use_smooth = True
    move_to_collection(top_obj, coll)
    # ---- Cream T-mold bullnose ring (same MAT_class_bump as folding banquet) ----
    # Matches classroom bump geometry: 0.15" proud of the top, 0.08" drop,
    # 0.25" thick radially. Modeled as a ring: outer cylinder minus inner void
    # emulated by two coaxial cylinders drawn as a shallow band around the top.
    bump_h = top_thick + 0.15
    bump_thick = 0.25
    bump_outer_r = top_r + bump_thick
    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * bump_outer_r, depth=IN * bump_h, vertices=64,
        location=(IN * cx, IN * cy, IN * (top_z + bump_h / 2 - 0.08)))
    band = bpy.context.active_object
    band.name = f"RoundTbl_{name}_edge"
    if band.data.materials: band.data.materials[0] = bump_mat
    else: band.data.materials.append(bump_mat)
    for p in band.data.polygons:
        p.use_smooth = True
    move_to_collection(band, coll)
    # 4 splayed tubular legs
    leg_top_r = 0.6
    leg_bot_r = 0.7
    top_anchor_r  = top_r - diameter * 0.28
    foot_anchor_r = top_r - 3.0
    leg_h = top_z
    for i in range(4):
        theta = _m.pi / 4 + i * _m.pi / 2
        tx = cx + top_anchor_r * _m.cos(theta)
        ty = cy + top_anchor_r * _m.sin(theta)
        fx = cx + foot_anchor_r * _m.cos(theta)
        fy = cy + foot_anchor_r * _m.sin(theta)
        vx = tx - fx; vy = ty - fy; vz = leg_h
        seg_len = _m.sqrt(vx * vx + vy * vy + vz * vz)
        mx = (fx + tx) / 2; my = (fy + ty) / 2; mz = leg_h / 2
        bpy.ops.mesh.primitive_cone_add(
            radius1=IN * leg_bot_r, radius2=IN * leg_top_r,
            depth=IN * seg_len, vertices=14,
            location=(IN * mx, IN * my, IN * mz))
        leg = bpy.context.active_object
        leg.name = f"RoundTbl_{name}_leg_{i}"
        default_axis = _mu.Vector((0.0, 0.0, 1.0))
        target_axis = _mu.Vector((vx, vy, vz)).normalized()
        quat = default_axis.rotation_difference(target_axis)
        leg.rotation_mode = 'QUATERNION'
        leg.rotation_quaternion = quat
        if leg.data.materials: leg.data.materials[0] = chrome_mat
        else: leg.data.materials.append(chrome_mat)
        move_to_collection(leg, coll)
        # Black foot cap
        bpy.ops.mesh.primitive_cylinder_add(
            radius=IN * (leg_bot_r + 0.25), depth=IN * 0.6, vertices=14,
            location=(IN * fx, IN * fy, IN * 0.3))
        foot = bpy.context.active_object
        foot.name = f"RoundTbl_{name}_foot_{i}"
        if foot.data.materials: foot.data.materials[0] = black_plastic_mat
        else: foot.data.materials.append(black_plastic_mat)
        move_to_collection(foot, coll)
    # Underside X cross-brace: two crossing tubes at 90 deg
    brace_z = top_z - 3.0
    brace_r = 0.35
    brace_len = diameter * 0.60
    for j, br_theta in enumerate((0.0, _m.pi / 2)):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=IN * brace_r, depth=IN * brace_len, vertices=10,
            location=(IN * cx, IN * cy, IN * brace_z),
            rotation=(0, _m.pi / 2, br_theta))
        br = bpy.context.active_object
        br.name = f"RoundTbl_{name}_brace_{j}"
        if br.data.materials: br.data.materials[0] = chrome_mat
        else: br.data.materials.append(chrome_mat)
        move_to_collection(br, coll)


def build_chair(name, x, y, coll):
    """Classroom chair: contoured back, padded seat, four tapered legs.
    v15c-quality: keeps overall CHAIR_W x CHAIR_D footprint and seat-top at
    SEAT_H so all clearances/layouts are unchanged. Footprint anchor is the
    NW (lo-x, lo-y) corner -- same as previous version.
    """
    seat_mat = get_or_create_color_material(
        "MAT_chair", (0.30, 0.04, 0.06, 1.0), roughness=0.55)
    leg_mat = get_or_create_color_material(
        "MAT_chair_leg", (0.16, 0.11, 0.07, 1.0), roughness=0.55)

    # ----- 4 tapered legs from floor to underside of seat -----
    leg_top_r = 0.45
    leg_bot_r = 0.65
    leg_inset = 0.9
    leg_height = SEAT_H - 1.5  # seat pad is 1.5" thick
    anchors = [
        (x + leg_inset,           y + leg_inset),
        (x + CHAIR_W - leg_inset, y + leg_inset),
        (x + leg_inset,           y + CHAIR_D - leg_inset),
        (x + CHAIR_W - leg_inset, y + CHAIR_D - leg_inset),
    ]
    for i, (lcx, lcy) in enumerate(anchors):
        bpy.ops.mesh.primitive_cone_add(
            radius1=IN * leg_bot_r,
            radius2=IN * leg_top_r,
            depth=IN * leg_height,
            location=(IN * lcx, IN * lcy, IN * (leg_height / 2)),
            vertices=12,
        )
        lg = bpy.context.active_object
        lg.name = f"Chair_{name}_leg_{i}"
        if lg.data.materials:
            lg.data.materials[0] = leg_mat
        else:
            lg.data.materials.append(leg_mat)
        move_to_collection(lg, coll)

    # ----- Padded seat cushion -----
    seat_pad_h = 1.8
    make_box(f"Chair_{name}_seat",
             x=x, y=y, z=SEAT_H - seat_pad_h,
             w=CHAIR_W, l=CHAIR_D, h=seat_pad_h,
             material=seat_mat, collection=coll)

    # ----- Contoured back: 3 short segments forming a slight curve -----
    back_total_h = CHAIR_H - SEAT_H
    seg_h = back_total_h / 3.0
    seg_thick = 1.6
    # Curve depths (Y-offset from rear edge): outer segments are flush, middle
    # segment is recessed forward slightly to suggest lumbar curve.
    rear_y = y + CHAIR_D - seg_thick
    # Bottom seg sits just behind seat top edge (slight back-cushion overhang)
    for i, depth_offset in enumerate((0.0, -0.6, 0.0)):
        seg_y = rear_y + depth_offset
        make_box(f"Chair_{name}_back_seg{i}",
                 x=x + 0.6, y=seg_y, z=SEAT_H + i * seg_h,
                 w=CHAIR_W - 1.2, l=seg_thick, h=seg_h * 0.85,
                 material=seat_mat, collection=coll)

    # ----- Two back posts (vertical supports, leg color) -----
    post_w = 1.0
    post_h = back_total_h
    for px in (x + 0.2, x + CHAIR_W - post_w - 0.2):
        make_box(f"Chair_{name}_back_post_{px:.1f}",
                 x=px, y=y + CHAIR_D - seg_thick - 0.2, z=SEAT_H,
                 w=post_w, l=post_w, h=post_h,
                 material=leg_mat, collection=coll)


def build_two_top(name, y, wall_side, coll):
    """Pub-style two-top dining table with single pedestal base + two club chairs.

    Footprint, positions, and overall heights match v15c exactly so layout/
    clearances are unchanged. The CONSTANT TWOTOP_W=18 is the WALL-FACING
    slot width; the actual table top occupies (TWOTOP_W-4) x TWOTOP_L = 14x14.

    v15d detail upgrades:
      - rounded-rectangle dark walnut top (slab + corner cylinders + thin
        bullnose lip just below for a chamfered look)
      - single center pedestal in matte black (column + wide foot disc)
      - two BRG club chairs with padded seat, 3-segment contoured back,
        two back posts, and four tapered cylindrical legs
    """
    # v15j: pub-table + ladder-back bar stool per user SketchUp reference.
    # Palette: cherry wood tops & seat pads on matte-black metal frames.
    top_mat = get_or_create_color_material(
        "MAT_twotop_top", (0.28, 0.10, 0.045, 1.0), roughness=0.45)   # cherry wood
    bullnose_mat = get_or_create_color_material(
        "MAT_twotop_bullnose", (0.22, 0.08, 0.035, 1.0), roughness=0.40)  # cherry, slightly darker edge
    pedestal_mat = get_or_create_color_material(
        "MAT_twotop_pedestal", (0.020, 0.020, 0.022, 1.0), roughness=0.35)  # matte black metal
    chair_mat = get_or_create_color_material(
        "MAT_twotop_chair", (0.28, 0.10, 0.045, 1.0), roughness=0.50)  # cherry seat pad (matches top)
    chair_leg_mat = get_or_create_color_material(
        "MAT_twotop_chair_leg", (0.020, 0.020, 0.022, 1.0), roughness=0.35)  # matte black frame

    if wall_side == 'L':
        tx = 0
    else:
        tx = ROOM_W - TWOTOP_W

    CHAIR_GAP = 2
    chairs_x = tx + 2
    table_y0 = y + CHAIR_D + CHAIR_GAP                  # 14
    chair_S_y0 = table_y0 + TWOTOP_L + CHAIR_GAP        # 30

    # ------------------------------------------------------------------
    # TABLE (centered in the wall-facing slot)
    # ------------------------------------------------------------------
    table_x0 = tx + 2
    table_w = TWOTOP_W - 4                              # 14
    table_l = TWOTOP_L                                  # 14
    top_thick = 1.0
    bullnose_thick = 0.7
    top_z0 = TWOTOP_H - top_thick - bullnose_thick
    # Main top slab
    make_box(f"TwoTop_{name}_top_slab",
             x=table_x0, y=table_y0, z=TWOTOP_H - top_thick,
             w=table_w, l=table_l, h=top_thick,
             material=top_mat, collection=coll)
    # Bullnose lip (slightly larger, sits just under the slab) -- gives a
    # chamfered/profiled edge look without expensive geometry.
    over = 0.4
    make_box(f"TwoTop_{name}_top_bullnose",
             x=table_x0 - over, y=table_y0 - over, z=top_z0,
             w=table_w + 2 * over, l=table_l + 2 * over, h=bullnose_thick,
             material=bullnose_mat, collection=coll)
    # Corner round-ish caps (4 tall thin cylinders) sitting on top corners to
    # soften the silhouette when seen from above/oblique.
    corner_r = 1.2
    for (cx_in, cy_in) in [
        (table_x0 + corner_r,                table_y0 + corner_r),
        (table_x0 + table_w - corner_r,      table_y0 + corner_r),
        (table_x0 + corner_r,                table_y0 + table_l - corner_r),
        (table_x0 + table_w - corner_r,      table_y0 + table_l - corner_r),
    ]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=IN * corner_r, depth=IN * (top_thick + bullnose_thick),
            location=(IN * cx_in, IN * cy_in,
                      IN * (top_z0 + (top_thick + bullnose_thick) / 2)),
            vertices=16,
        )
        c = bpy.context.active_object
        c.name = f"TwoTop_{name}_corner_{cx_in:.0f}_{cy_in:.0f}"
        if c.data.materials:
            c.data.materials[0] = top_mat
        else:
            c.data.materials.append(top_mat)
        move_to_collection(c, coll)

    # ------------------------------------------------------------------
    # v15j: Pedestal per SketchUp reference "Three Top High Bar Table.png":
    #   central black metal column with a CROSS-SHAPED foot (two crossed
    #   rectangular bars) instead of a round disc.
    # ------------------------------------------------------------------
    center_x = table_x0 + table_w / 2
    center_y = table_y0 + table_l / 2
    foot_bar_len = 11.0     # cross-arm length (each bar)
    foot_bar_w = 1.6        # cross-arm width
    foot_h = 1.0            # cross-arm thickness/height
    col_r = 1.8
    col_h = top_z0 - foot_h
    # Cross foot: two rectangular bars centered on pedestal, crossed at 90 deg
    make_box(f"TwoTop_{name}_ped_footX",
             x=center_x - foot_bar_len / 2, y=center_y - foot_bar_w / 2, z=0,
             w=foot_bar_len, l=foot_bar_w, h=foot_h,
             material=pedestal_mat, collection=coll)
    make_box(f"TwoTop_{name}_ped_footY",
             x=center_x - foot_bar_w / 2, y=center_y - foot_bar_len / 2, z=0,
             w=foot_bar_w, l=foot_bar_len, h=foot_h,
             material=pedestal_mat, collection=coll)
    # Column
    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * col_r, depth=IN * col_h,
        location=(IN * center_x, IN * center_y, IN * (foot_h + col_h / 2)),
        vertices=20,
    )
    cc = bpy.context.active_object
    cc.name = f"TwoTop_{name}_ped_col"
    if cc.data.materials:
        cc.data.materials[0] = pedestal_mat
    else:
        cc.data.materials.append(pedestal_mat)
    move_to_collection(cc, coll)

    # ------------------------------------------------------------------
    # v15j: bar stools (4 legs, straight, back + seat) per user reference.
    # Two stools per two-top (N stool and S stool). Seat is 30" off floor,
    # backrest extends to 45" total. Simpler than the old club-chair shape:
    #   4 straight tapered legs, flat seat pad, straight vertical back with
    #   two thin cross-slats (matches typical 4-leg back-seat bar stool).
    # ------------------------------------------------------------------
    chair_W = 16                # bar stool seat width (slightly narrower than club chair)
    chair_D = 14                # bar stool seat depth (deeper than dining chair)
    chair_seat_h = TWOTOP_SEAT_H         # v15j: 30" bar-stool seat height
    chair_back_top = TWOTOP_CHAIR_TOTAL_H  # v15j: 45" total
    chair_back_h = chair_back_top - chair_seat_h

    def _build_one_chair(label, x0, y0):
        # 4 tapered legs floor -> seat underside
        leg_top_r = 0.50
        leg_bot_r = 0.75
        leg_inset = 1.0
        seat_pad_h = 1.8
        leg_height = chair_seat_h - seat_pad_h
        anchors = [
            (x0 + leg_inset,           y0 + leg_inset),
            (x0 + chair_W - leg_inset, y0 + leg_inset),
            (x0 + leg_inset,           y0 + chair_D - leg_inset),
            (x0 + chair_W - leg_inset, y0 + chair_D - leg_inset),
        ]
        for i, (lcx, lcy) in enumerate(anchors):
            bpy.ops.mesh.primitive_cone_add(
                radius1=IN * leg_bot_r, radius2=IN * leg_top_r,
                depth=IN * leg_height,
                location=(IN * lcx, IN * lcy, IN * (leg_height / 2)),
                vertices=12,
            )
            lg = bpy.context.active_object
            lg.name = f"TwoTop_{name}_{label}_leg_{i}"
            if lg.data.materials:
                lg.data.materials[0] = chair_leg_mat
            else:
                lg.data.materials.append(chair_leg_mat)
            move_to_collection(lg, coll)
        # v15L: FOOTREST RING -- 4 black metal bars connecting the 4 legs, ~4" off floor.
        # Matches SketchUp Bar Stool reference (single wraparound ring near base).
        fr_z = 4.0                     # bar-stool footrest height off floor
        fr_thick = 0.7                 # bar thickness (square profile)
        fr_len_x = chair_W - 2 * leg_inset   # span between E and W legs
        fr_len_y = chair_D - 2 * leg_inset   # span between N and S legs
        # Front bar (south side, y=leg_inset)
        make_box(f"TwoTop_{name}_{label}_footrest_S",
                 x=x0 + leg_inset, y=y0 + leg_inset - fr_thick / 2, z=fr_z,
                 w=fr_len_x, l=fr_thick, h=fr_thick,
                 material=chair_leg_mat, collection=coll)
        # Back bar (north side)
        make_box(f"TwoTop_{name}_{label}_footrest_N",
                 x=x0 + leg_inset, y=y0 + chair_D - leg_inset - fr_thick / 2, z=fr_z,
                 w=fr_len_x, l=fr_thick, h=fr_thick,
                 material=chair_leg_mat, collection=coll)
        # West bar
        make_box(f"TwoTop_{name}_{label}_footrest_W",
                 x=x0 + leg_inset - fr_thick / 2, y=y0 + leg_inset, z=fr_z,
                 w=fr_thick, l=fr_len_y, h=fr_thick,
                 material=chair_leg_mat, collection=coll)
        # East bar
        make_box(f"TwoTop_{name}_{label}_footrest_E",
                 x=x0 + chair_W - leg_inset - fr_thick / 2, y=y0 + leg_inset, z=fr_z,
                 w=fr_thick, l=fr_len_y, h=fr_thick,
                 material=chair_leg_mat, collection=coll)
        # v15j: cherry-wood seat pad (matches table top color)
        make_box(f"TwoTop_{name}_{label}_seat",
                 x=x0, y=y0, z=chair_seat_h - seat_pad_h,
                 w=chair_W, l=chair_D, h=seat_pad_h,
                 material=chair_mat, collection=coll)
        # v15j: LADDER-BACK -- two vertical black posts + 3 horizontal cross-slats
        # (per user SketchUp reference "Bar Stool.png"). Posts run from seat to
        # backrest top; slats are the same black metal color, evenly spaced.
        post_w = 1.0
        post_l = 1.0
        back_y = y0 + chair_D - post_l - 0.2   # back plane is just inside rear seat edge
        # Two vertical posts (full back height)
        for post_x in (x0 + 0.3, x0 + chair_W - post_w - 0.3):
            make_box(f"TwoTop_{name}_{label}_backpost_{post_x:.1f}",
                     x=post_x, y=back_y, z=chair_seat_h,
                     w=post_w, l=post_l, h=chair_back_h,
                     material=chair_leg_mat, collection=coll)
        # 3 horizontal cross-slats spanning between the posts
        slat_thick = 0.9        # slat vertical height
        slat_depth = 0.7        # slat front-back depth
        slat_w = chair_W - 2 * (0.3 + post_w) + 0.2  # span between post inner edges
        slat_x = x0 + 0.3 + post_w - 0.1
        # Distribute 3 slats: lower ~1/4 up, middle ~1/2, upper ~3/4 of back height
        for i, frac in enumerate((0.25, 0.55, 0.85)):
            slat_z = chair_seat_h + frac * chair_back_h
            make_box(f"TwoTop_{name}_{label}_slat{i}",
                     x=slat_x, y=back_y + (post_l - slat_depth) / 2, z=slat_z,
                     w=slat_w, l=slat_depth, h=slat_thick,
                     material=chair_leg_mat, collection=coll)

    _build_one_chair("chair_N", chairs_x, y)
    _build_one_chair("chair_S", chairs_x, chair_S_y0)


def build_bench():
    """v15L: bench REPLACED by 3 diner-style booth sections along the north wall.
    Plain BLACK VINYL upholstery (per user reference photo of the actual room --
    solid black bench, NO cream piping, NO diner red). Each section: black vinyl
    seat cushion + tall channel-tufted seatback rising ~30" from seat top.
    Total span 168" (x=102..270) split into 3 equal ~56" wide sections with
    a 1" divider gap between neighbors so the tufted separations are visible.
    """
    coll = get_or_create_collection("Bench_Seating")
    # Plain matte black vinyl (matches original room photo bench).
    vinyl_mat = get_or_create_color_material(
        "MAT_booth_black_vinyl", (0.03, 0.03, 0.035, 1.0), roughness=0.35)
    # Slightly darker gap between tuft channels (fake shadow line).
    tuft_shadow_mat = get_or_create_color_material(
        "MAT_booth_tuft_shadow", (0.01, 0.01, 0.012, 1.0), roughness=0.6)
    # Chrome/black plinth base under the booth.
    plinth_mat = get_or_create_color_material(
        "MAT_booth_plinth", (0.05, 0.05, 0.06, 1.0), roughness=0.4)

    total_span = bench_x1 - bench_x0            # 168"
    n_sections = 3
    divider_gap = 1.0                            # visible seam between sections
    section_w = (total_span - divider_gap * (n_sections - 1)) / n_sections  # ~55.33
    seat_top_z = BENCH_H                         # 18"
    seat_thick = BENCH_H - 4                     # 14" upholstered cushion above plinth
    back_h = 30                                  # tall channel-tufted back, 30" above seat
    back_thick = 3                               # back cushion depth (front-to-back)
    plinth_h = 4                                 # small black plinth under cushion

    for i in range(n_sections):
        sx0 = bench_x0 + i * (section_w + divider_gap)
        # Plinth (dark, matte)
        make_box(f"Booth_{i}_plinth",
                 x=sx0, y=bench_y0, z=0,
                 w=section_w, l=BENCH_DEPTH, h=plinth_h,
                 material=plinth_mat, collection=coll)
        # Seat cushion (plain black vinyl -- no piping)
        make_box(f"Booth_{i}_seat",
                 x=sx0, y=bench_y0, z=plinth_h,
                 w=section_w, l=BENCH_DEPTH, h=seat_thick,
                 material=vinyl_mat, collection=coll)
        # Seat-back main slab (attached at north wall side, front-facing south)
        back_y0 = bench_y0 + BENCH_DEPTH - back_thick
        make_box(f"Booth_{i}_back",
                 x=sx0, y=back_y0, z=seat_top_z,
                 w=section_w, l=back_thick, h=back_h,
                 material=vinyl_mat, collection=coll)
        # CHANNEL TUFTING: 5 vertical shadow grooves across the back panel.
        # Each groove is a thin dark rectangle inset ~0.4" from the back's south face.
        n_grooves = 5
        groove_w = 0.5
        groove_pitch = section_w / (n_grooves + 1)
        groove_inset = 0.35   # protrudes slightly south of back face to be visible
        for g in range(n_grooves):
            gx = sx0 + groove_pitch * (g + 1) - groove_w / 2
            make_box(f"Booth_{i}_groove_{g}",
                     x=gx, y=back_y0 - groove_inset, z=seat_top_z + 2,
                     w=groove_w, l=groove_inset + 0.05, h=back_h - 4,
                     material=tuft_shadow_mat, collection=coll)
        # Section divider caps at east/west edges (except at booth-run ends).
        # These are the tall vertical pillars that separate booths visually.
        cap_w = 1.5
        if i < n_sections - 1:
            # Divider between this section and the next
            dx = sx0 + section_w - cap_w / 2
            make_box(f"Booth_{i}_divider_E",
                     x=dx, y=bench_y0 + BENCH_DEPTH - back_thick - 1, z=plinth_h,
                     w=cap_w + divider_gap, l=back_thick + 1, h=seat_thick + back_h,
                     material=vinyl_mat, collection=coll)


def build_buffet():
    """v15f: hotel banquet-style buffet.
    Built on the same classroom-table base (off-white laminate top + dark legs)
    placed along the east wall, aligned with the FRONT classroom row. Then
    DRAPED with a pleated white banquet skirt on the 3 exposed sides, COVERED
    with an overhanging white tablecloth, and TOPPED with a full hotel coffee
    service: 2 coffee urns, sugar/cream caddy, cups, saucers, tea selection,
    stirrers, napkins, water pitcher, flower vase, and signage placards.
    Geometry/position of the underlying table unchanged from v15e.
    """
    coll = get_or_create_collection("Buffet")
    BUFFET_L = 60          # along Y (north-south length along east wall)
    BUFFET_D = 18          # along X (depth from east wall)
    BUFFET_X0 = ROOM_W - BUFFET_D                # x=298..316 (east wall flush)
    row0_table_center_y = (front_table_top_y + front_table_bottom_y) / 2
    BUFFET_Y0 = row0_table_center_y - BUFFET_L / 2

    # --- 1. Underlying classroom-style table (laminate top + dark legs) -----
    build_classroom_table("Buffet", BUFFET_X0, BUFFET_Y0, BUFFET_D, BUFFET_L, coll)

    # Classroom-table top sits z = (CHAIR_H - 2) .. (CHAIR_H)  -> 30..32"
    TABLE_TOP_Z = CHAIR_H              # top surface of laminate (=32)
    TABLE_TOP_BOT_Z = CHAIR_H - 2      # bottom of laminate slab (=30)

    # --- 2. Materials for the hotel banquet linens & service ----------------
    cloth_mat = get_or_create_color_material(
        "MAT_buffet_cloth", (0.95, 0.93, 0.86, 1.0), roughness=0.88)
    cloth_shadow_mat = get_or_create_color_material(
        "MAT_buffet_cloth_shadow", (0.86, 0.83, 0.74, 1.0), roughness=0.9)
    chrome_mat = get_or_create_color_material(
        "MAT_buffet_chrome", (0.86, 0.86, 0.88, 1.0), roughness=0.22)
    urn_black_mat = get_or_create_color_material(
        "MAT_buffet_urn_black", (0.06, 0.06, 0.06, 1.0), roughness=0.40)
    ceramic_mat = get_or_create_color_material(
        "MAT_buffet_ceramic", (0.96, 0.95, 0.91, 1.0), roughness=0.30)
    glass_mat = get_or_create_color_material(
        "MAT_buffet_glass", (0.85, 0.92, 0.95, 0.55), roughness=0.10)
    placard_mat = get_or_create_color_material(
        "MAT_buffet_placard", (0.97, 0.96, 0.92, 1.0), roughness=0.55)
    placard_text_mat = get_or_create_color_material(
        "MAT_buffet_placard_text", (0.08, 0.08, 0.10, 1.0), roughness=0.6)
    flower_red_mat = get_or_create_color_material(
        "MAT_buffet_flower_red", (0.72, 0.10, 0.12, 1.0), roughness=0.55)
    flower_yellow_mat = get_or_create_color_material(
        "MAT_buffet_flower_yellow", (0.93, 0.78, 0.18, 1.0), roughness=0.55)
    leaf_mat = get_or_create_color_material(
        "MAT_buffet_leaf", (0.12, 0.32, 0.13, 1.0), roughness=0.7)
    lemon_mat = get_or_create_color_material(
        "MAT_buffet_lemon", (0.96, 0.86, 0.18, 1.0), roughness=0.55)
    tea_box_mat = get_or_create_color_material(
        "MAT_buffet_tea_box", (0.55, 0.40, 0.25, 1.0), roughness=0.6)
    coffee_brown_mat = get_or_create_color_material(
        "MAT_buffet_coffee_brown", (0.18, 0.10, 0.06, 1.0), roughness=0.4)

    # --- 3. Pleated banquet skirt (3 exposed sides) -------------------------
    # Skirt hangs from ~1" below the tablecloth top down to the floor.
    # East side is against the wall -> no skirt there.
    SKIRT_TOP_Z = TABLE_TOP_BOT_Z + 1.0         # =31  (just below cloth overhang)
    SKIRT_BOTTOM_Z = 0.5                        # just above the floor
    SKIRT_H = SKIRT_TOP_Z - SKIRT_BOTTOM_Z
    PLEAT_W = 4.0                               # nominal pleat panel width
    PLEAT_DEPTH_OUT = 0.6                       # bulge outward
    PLEAT_DEPTH_BACK = 0.25                     # recessed pleat depth

    # South-facing skirt (runs along X from BUFFET_X0..BUFFET_X0+BUFFET_D),
    # hangs at y = BUFFET_Y0 (south edge of table)
    skirt_S_y = BUFFET_Y0
    n_pleats_S = max(1, int(round(BUFFET_D / PLEAT_W)))
    pleat_w_S = BUFFET_D / n_pleats_S
    for i in range(n_pleats_S):
        x0 = BUFFET_X0 + i * pleat_w_S
        bulge = PLEAT_DEPTH_OUT if (i % 2 == 0) else PLEAT_DEPTH_BACK
        mat = cloth_mat if (i % 2 == 0) else cloth_shadow_mat
        make_box(f"Buffet_SkirtS_{i}",
                 x=x0, y=skirt_S_y - bulge, z=SKIRT_BOTTOM_Z,
                 w=pleat_w_S, l=bulge + 0.25, h=SKIRT_H,
                 material=mat, collection=coll)

    # North-facing skirt at y = BUFFET_Y0 + BUFFET_L
    skirt_N_y = BUFFET_Y0 + BUFFET_L
    for i in range(n_pleats_S):
        x0 = BUFFET_X0 + i * pleat_w_S
        bulge = PLEAT_DEPTH_OUT if (i % 2 == 0) else PLEAT_DEPTH_BACK
        mat = cloth_mat if (i % 2 == 0) else cloth_shadow_mat
        make_box(f"Buffet_SkirtN_{i}",
                 x=x0, y=skirt_N_y - 0.25, z=SKIRT_BOTTOM_Z,
                 w=pleat_w_S, l=bulge + 0.25, h=SKIRT_H,
                 material=mat, collection=coll)

    # West-facing skirt (the long exposed face — runs along Y).
    # hangs at x = BUFFET_X0 (west edge of table, the side facing the room)
    skirt_W_x = BUFFET_X0
    n_pleats_W = max(1, int(round(BUFFET_L / PLEAT_W)))
    pleat_l_W = BUFFET_L / n_pleats_W
    for i in range(n_pleats_W):
        y0 = BUFFET_Y0 + i * pleat_l_W
        bulge = PLEAT_DEPTH_OUT if (i % 2 == 0) else PLEAT_DEPTH_BACK
        mat = cloth_mat if (i % 2 == 0) else cloth_shadow_mat
        make_box(f"Buffet_SkirtW_{i}",
                 x=skirt_W_x - bulge, y=y0, z=SKIRT_BOTTOM_Z,
                 w=bulge + 0.25, l=pleat_l_W, h=SKIRT_H,
                 material=mat, collection=coll)

    # Top valance band (smooth, hides the seam between table edge and pleats)
    VAL_H = 3.0
    val_z = TABLE_TOP_BOT_Z - VAL_H + 0.5
    # south band
    make_box("Buffet_Valance_S",
             x=BUFFET_X0 - 0.5, y=BUFFET_Y0 - PLEAT_DEPTH_OUT - 0.25,
             z=val_z, w=BUFFET_D + 1.0, l=0.6, h=VAL_H,
             material=cloth_mat, collection=coll)
    # north band
    make_box("Buffet_Valance_N",
             x=BUFFET_X0 - 0.5, y=BUFFET_Y0 + BUFFET_L + 0.25 - 0.35,
             z=val_z, w=BUFFET_D + 1.0, l=0.6, h=VAL_H,
             material=cloth_mat, collection=coll)
    # west band (long)
    make_box("Buffet_Valance_W",
             x=BUFFET_X0 - PLEAT_DEPTH_OUT - 0.25, y=BUFFET_Y0 - 0.5,
             z=val_z, w=0.6, l=BUFFET_L + 1.0, h=VAL_H,
             material=cloth_mat, collection=coll)

    # --- 4. White tablecloth top with overhang ------------------------------
    CLOTH_OVERHANG = 1.5
    CLOTH_THICK = 0.4
    cloth_x0 = BUFFET_X0 - CLOTH_OVERHANG      # west overhang
    cloth_y0 = BUFFET_Y0 - CLOTH_OVERHANG      # south overhang
    cloth_w = BUFFET_D + CLOTH_OVERHANG        # east edge flush to wall
    cloth_l = BUFFET_L + 2 * CLOTH_OVERHANG    # north+south overhang
    make_box("Buffet_Tablecloth",
             x=cloth_x0, y=cloth_y0, z=TABLE_TOP_Z,
             w=cloth_w, l=cloth_l, h=CLOTH_THICK,
             material=cloth_mat, collection=coll)

    # Tablecloth top surface plane (where service items sit)
    CLOTH_TOP_Z = TABLE_TOP_Z + CLOTH_THICK    # =32.4

    # --- 5. Coffee service items on top ------------------------------------
    # Layout (looking from west toward east wall, along buffet from south to north):
    #   y = BUFFET_Y0 .. BUFFET_Y0+BUFFET_L  (60" total along buffet length)
    #   x lane: items hug the east half of the table (closer to wall)
    #
    #   y-station bands (approx, from south to north along the 60" buffet):
    #     [0..8]   : "COFFEE" placard + flower vase (south end)
    #     [8..22]  : Regular coffee urn (urn A)
    #     [22..32] : creamer/sugar caddy + stirrer holder + napkins
    #     [32..46] : Decaf coffee urn (urn B)
    #     [46..56] : tea box + hot water pitcher / lemon water pitcher
    #     [56..60] : cups+saucers stacks + flower vase (north end)
    Y = BUFFET_Y0
    X_WALL = BUFFET_X0 + BUFFET_D              # against east wall
    Z0 = CLOTH_TOP_Z

    # --- helpers (local closures) -----
    def _cyl(name, cx, cy, cz, radius, height, mat):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius * IN, depth=height * IN,
            location=(cx * IN, cy * IN, (cz + height / 2) * IN))
        obj = bpy.context.active_object
        obj.name = name
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        move_to_collection(obj, coll)
        return obj

    def _cone(name, cx, cy, cz, r1, r2, height, mat):
        bpy.ops.mesh.primitive_cone_add(
            radius1=r1 * IN, radius2=r2 * IN, depth=height * IN,
            location=(cx * IN, cy * IN, (cz + height / 2) * IN))
        obj = bpy.context.active_object
        obj.name = name
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        move_to_collection(obj, coll)
        return obj

    # ------- (a) "COFFEE" placard (south end) -------
    p_y = Y + 2.0
    p_cx = X_WALL - 9.0
    make_box("Buffet_Placard_Coffee_base",
             x=p_cx - 3.0, y=p_y - 1.0, z=Z0,
             w=6.0, l=2.0, h=0.4, material=placard_mat, collection=coll)
    make_box("Buffet_Placard_Coffee_face",
             x=p_cx - 3.0, y=p_y - 1.0, z=Z0 + 0.4,
             w=6.0, l=0.3, h=3.0, material=placard_mat, collection=coll)
    make_box("Buffet_Placard_Coffee_text",
             x=p_cx - 2.2, y=p_y - 1.05, z=Z0 + 1.0,
             w=4.4, l=0.05, h=1.4, material=placard_text_mat, collection=coll)

    # ------- (b) South-end flower vase (tall, slim) -------
    vase_cx = X_WALL - 4.0
    vase_cy = Y + 4.0
    _cyl("Buffet_Vase_S_body", vase_cx, vase_cy, Z0, 1.6, 7.0, glass_mat)
    # flowers (cluster of small spheres on stems)
    for k, (dx, dy, col_mat) in enumerate([
            (0.0, 0.0, flower_red_mat),
            (0.7, 0.4, flower_yellow_mat),
            (-0.6, 0.3, flower_red_mat),
            (0.2, -0.6, flower_yellow_mat),
            (-0.3, -0.4, flower_red_mat)]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.6 * IN,
            location=((vase_cx + dx) * IN, (vase_cy + dy) * IN,
                      (Z0 + 8.4) * IN))
        obj = bpy.context.active_object
        obj.name = f"Buffet_Vase_S_flower_{k}"
        obj.data.materials.append(col_mat)
        move_to_collection(obj, coll)
    # leaves
    for k, (dx, dy) in enumerate([(1.0, 0.0), (-1.0, 0.2), (0.0, 0.9)]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.45 * IN,
            location=((vase_cx + dx) * IN, (vase_cy + dy) * IN,
                      (Z0 + 7.6) * IN))
        obj = bpy.context.active_object
        obj.name = f"Buffet_Vase_S_leaf_{k}"
        obj.data.materials.append(leaf_mat)
        move_to_collection(obj, coll)

    # ------- (c) Urn A — Regular coffee (south-center) -------
    urnA_cx = X_WALL - 7.0
    urnA_cy = Y + 15.0
    # base disc (chrome)
    _cyl("Buffet_UrnA_base", urnA_cx, urnA_cy, Z0, 5.0, 0.4, chrome_mat)
    # body (chrome cylinder, taller)
    _cyl("Buffet_UrnA_body", urnA_cx, urnA_cy, Z0 + 0.4, 4.0, 11.0, chrome_mat)
    # top dome (slight cone)
    _cone("Buffet_UrnA_dome", urnA_cx, urnA_cy, Z0 + 11.4, 4.0, 2.0, 1.5, chrome_mat)
    # finial knob
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.5 * IN,
        location=(urnA_cx * IN, urnA_cy * IN, (Z0 + 13.2) * IN))
    obj = bpy.context.active_object
    obj.name = "Buffet_UrnA_finial"
    obj.data.materials.append(chrome_mat)
    move_to_collection(obj, coll)
    # spigot (small black box on west side)
    make_box("Buffet_UrnA_spigot",
             x=urnA_cx - 5.0, y=urnA_cy - 0.7, z=Z0 + 2.0,
             w=1.2, l=1.4, h=1.4, material=urn_black_mat, collection=coll)
    # spigot lever
    make_box("Buffet_UrnA_lever",
             x=urnA_cx - 5.6, y=urnA_cy - 0.2, z=Z0 + 2.5,
             w=0.8, l=0.4, h=0.5, material=urn_black_mat, collection=coll)
    # handles (two black blocks on N/S sides)
    make_box("Buffet_UrnA_handle_S",
             x=urnA_cx - 0.8, y=urnA_cy - 4.6, z=Z0 + 5.0,
             w=1.6, l=0.8, h=2.5, material=urn_black_mat, collection=coll)
    make_box("Buffet_UrnA_handle_N",
             x=urnA_cx - 0.8, y=urnA_cy + 3.8, z=Z0 + 5.0,
             w=1.6, l=0.8, h=2.5, material=urn_black_mat, collection=coll)
    # "Coffee" label band
    make_box("Buffet_UrnA_label",
             x=urnA_cx - 2.4, y=urnA_cy - 4.05, z=Z0 + 7.5,
             w=4.8, l=0.05, h=1.4, material=placard_text_mat, collection=coll)

    # ------- (d) Creamer/Sugar caddy + stirrers + napkins (mid) -------
    cad_cx = X_WALL - 5.5
    cad_cy = Y + 27.0
    # caddy tray (ceramic)
    make_box("Buffet_Caddy_tray",
             x=cad_cx - 4.5, y=cad_cy - 3.0, z=Z0,
             w=9.0, l=6.0, h=0.6, material=ceramic_mat, collection=coll)
    # cream pitcher (ceramic, small)
    _cyl("Buffet_Cream_pitcher", cad_cx - 2.6, cad_cy - 1.2, Z0 + 0.6,
         1.2, 3.5, ceramic_mat)
    _cyl("Buffet_Cream_pitcher_lid", cad_cx - 2.6, cad_cy - 1.2,
         Z0 + 4.1, 1.0, 0.4, chrome_mat)
    # sugar bowl
    _cyl("Buffet_Sugar_bowl", cad_cx + 0.4, cad_cy - 1.2, Z0 + 0.6,
         1.4, 2.2, ceramic_mat)
    _cyl("Buffet_Sugar_bowl_lid", cad_cx + 0.4, cad_cy - 1.2,
         Z0 + 2.8, 1.3, 0.5, chrome_mat)
    # sugar packet holder
    make_box("Buffet_SugarPacket_holder",
             x=cad_cx + 2.2, y=cad_cy - 2.4, z=Z0 + 0.6,
             w=2.0, l=2.5, h=1.6, material=cloth_mat, collection=coll)
    # stirrer cup
    _cyl("Buffet_Stirrer_cup", cad_cx - 3.2, cad_cy + 1.5, Z0 + 0.6,
         0.9, 2.5, chrome_mat)
    # stirrers poking out
    for k in range(5):
        ang_off = (k - 2) * 0.15
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.06 * IN, depth=3.0 * IN,
            location=((cad_cx - 3.2 + ang_off) * IN, (cad_cy + 1.5) * IN,
                      (Z0 + 4.5) * IN))
        obj = bpy.context.active_object
        obj.name = f"Buffet_Stirrer_{k}"
        obj.data.materials.append(coffee_brown_mat)
        move_to_collection(obj, coll)
    # napkin stack
    make_box("Buffet_Napkins_S1",
             x=cad_cx - 0.8, y=cad_cy + 0.6, z=Z0 + 0.6,
             w=4.0, l=2.0, h=0.6, material=cloth_mat, collection=coll)
    make_box("Buffet_Napkins_S2",
             x=cad_cx - 0.6, y=cad_cy + 0.8, z=Z0 + 1.2,
             w=3.6, l=1.6, h=0.5, material=cloth_mat, collection=coll)

    # ------- (e) Urn B — Decaf (north-center) -------
    urnB_cx = X_WALL - 7.0
    urnB_cy = Y + 39.0
    _cyl("Buffet_UrnB_base", urnB_cx, urnB_cy, Z0, 5.0, 0.4, chrome_mat)
    _cyl("Buffet_UrnB_body", urnB_cx, urnB_cy, Z0 + 0.4, 4.0, 11.0, chrome_mat)
    _cone("Buffet_UrnB_dome", urnB_cx, urnB_cy, Z0 + 11.4, 4.0, 2.0, 1.5, chrome_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.5 * IN,
        location=(urnB_cx * IN, urnB_cy * IN, (Z0 + 13.2) * IN))
    obj = bpy.context.active_object
    obj.name = "Buffet_UrnB_finial"
    obj.data.materials.append(chrome_mat)
    move_to_collection(obj, coll)
    make_box("Buffet_UrnB_spigot",
             x=urnB_cx - 5.0, y=urnB_cy - 0.7, z=Z0 + 2.0,
             w=1.2, l=1.4, h=1.4, material=urn_black_mat, collection=coll)
    make_box("Buffet_UrnB_lever",
             x=urnB_cx - 5.6, y=urnB_cy - 0.2, z=Z0 + 2.5,
             w=0.8, l=0.4, h=0.5, material=urn_black_mat, collection=coll)
    make_box("Buffet_UrnB_handle_S",
             x=urnB_cx - 0.8, y=urnB_cy - 4.6, z=Z0 + 5.0,
             w=1.6, l=0.8, h=2.5, material=urn_black_mat, collection=coll)
    make_box("Buffet_UrnB_handle_N",
             x=urnB_cx - 0.8, y=urnB_cy + 3.8, z=Z0 + 5.0,
             w=1.6, l=0.8, h=2.5, material=urn_black_mat, collection=coll)
    # "Decaf" orange label band (use lemon-ish for visibility but recolor)
    decaf_label_mat = get_or_create_color_material(
        "MAT_buffet_decaf_label", (0.85, 0.45, 0.10, 1.0), roughness=0.55)
    make_box("Buffet_UrnB_label",
             x=urnB_cx - 2.4, y=urnB_cy - 4.05, z=Z0 + 7.5,
             w=4.8, l=0.05, h=1.4, material=decaf_label_mat, collection=coll)

    # ------- (f) Tea selection + hot water pitcher + lemon water -------
    tea_cx = X_WALL - 5.5
    tea_cy = Y + 51.0
    # tea box (wooden)
    make_box("Buffet_Tea_box",
             x=tea_cx - 4.0, y=tea_cy - 3.0, z=Z0,
             w=8.0, l=6.0, h=1.4, material=tea_box_mat, collection=coll)
    # tea compartments (subtle dividers, thin cream strips)
    for k in range(3):
        make_box(f"Buffet_Tea_divider_{k}",
                 x=tea_cx - 4.0 + (k + 1) * 2.0, y=tea_cy - 3.0, z=Z0 + 1.0,
                 w=0.15, l=6.0, h=0.5, material=cloth_mat, collection=coll)
    # hot water pitcher (chrome carafe)
    _cyl("Buffet_HotWater_pitcher", tea_cx + 0.2, tea_cy + 4.0, Z0,
         1.6, 8.0, chrome_mat)
    _cyl("Buffet_HotWater_pitcher_lid", tea_cx + 0.2, tea_cy + 4.0,
         Z0 + 8.0, 1.4, 0.5, chrome_mat)
    # handle
    make_box("Buffet_HotWater_handle",
             x=tea_cx + 1.5, y=tea_cy + 3.7, z=Z0 + 2.0,
             w=0.4, l=0.6, h=4.0, material=urn_black_mat, collection=coll)
    # lemon water pitcher (glass)
    _cyl("Buffet_LemonWater_pitcher", tea_cx - 3.0, tea_cy + 4.0, Z0,
         1.8, 7.5, glass_mat)
    # lemon slices visible at top
    for k, (dx, dy) in enumerate([(0.0, 0.4), (0.7, -0.3), (-0.6, 0.1)]):
        _cyl(f"Buffet_LemonWater_slice_{k}",
             tea_cx - 3.0 + dx, tea_cy + 4.0 + dy, Z0 + 6.5,
             0.5, 0.2, lemon_mat)

    # ------- (g) North end: cups + saucers + flower vase ---------------
    # saucer stack (low cylinder stack)
    sau_cx = X_WALL - 4.0
    sau_cy = Y + 55.5
    for k in range(5):
        _cyl(f"Buffet_Saucer_{k}", sau_cx, sau_cy, Z0 + k * 0.3,
             2.0, 0.3, ceramic_mat)
    # cup stack (inverted-looking small cylinders, double stack)
    cup_cx = X_WALL - 8.5
    cup_cy = Y + 55.5
    for k in range(4):
        _cyl(f"Buffet_Cup_A_{k}", cup_cx, cup_cy, Z0 + k * 2.6,
             1.4, 2.4, ceramic_mat)
    for k in range(4):
        _cyl(f"Buffet_Cup_B_{k}", cup_cx, cup_cy - 3.2, Z0 + k * 2.6,
             1.4, 2.4, ceramic_mat)

    # North-end flower vase (matches south)
    vaseN_cx = X_WALL - 4.0
    vaseN_cy = Y + 58.0
    _cyl("Buffet_Vase_N_body", vaseN_cx, vaseN_cy, Z0, 1.6, 7.0, glass_mat)
    for k, (dx, dy, col_mat) in enumerate([
            (0.0, 0.0, flower_yellow_mat),
            (0.7, 0.4, flower_red_mat),
            (-0.6, 0.3, flower_yellow_mat),
            (0.2, -0.6, flower_red_mat),
            (-0.3, -0.4, flower_yellow_mat)]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.6 * IN,
            location=((vaseN_cx + dx) * IN, (vaseN_cy + dy) * IN,
                      (Z0 + 8.4) * IN))
        obj = bpy.context.active_object
        obj.name = f"Buffet_Vase_N_flower_{k}"
        obj.data.materials.append(col_mat)
        move_to_collection(obj, coll)



def build_pool_tables():
    coll = get_or_create_collection("Pool_Tables")
    for (name, cx, ty) in POOL_TABLES:
        build_pool_table(name, cx, ty, coll)


def build_classroom():
    coll = get_or_create_collection("Classroom_Tables")
    # v15c: 2 cols x N_ROWS deep. Build front -> back (south -> north).
    # v15L: BACK ROW (row_idx == N_ROWS-1, northernmost) is REPLACED by two
    # round stacking tables (build_round_tables). We only build rows 0..N_ROWS-2
    # here so that space is free for the round tables between stage and Storage A.
    rows = []
    for row_idx in range(N_ROWS - 1):     # skip the last (northernmost) row
        table_bottom_y = front_table_bottom_y - row_idx * CLASS_ROW_PITCH
        ty_table = table_bottom_y - CLASS_W              # table top edge y
        ty_chair = ty_table - 2 - CHAIR_D                # chair top edge y
        rows.append((row_idx, ty_table, ty_chair))
    for row_idx, ty_table, ty_chair in rows:
        for col_idx in range(N_PER_ROW):
            tx = class_row_x0 + col_idx * (CLASS_LEN + CLASS_GAP_X)
            tag = f"R{row_idx}C{col_idx}"
            build_classroom_table(tag, tx, ty_table, CLASS_LEN, CLASS_W, coll)
            for j in range(CHAIRS_PER_TABLE):
                chair_cx = tx + CLASS_LEN * ((j + 0.5) / CHAIRS_PER_TABLE)
                build_chair(f"{tag}_c{j}",
                            chair_cx - CHAIR_W / 2, ty_chair, coll)


def build_round_tables():
    """v15L: 2 stacking round folding tables between the NW stage and the
    Storage A door on the north wall (occupying the former Row-2 classroom
    zone). Stage occupies x=0..96 at y=0..48; Storage A door is on the N wall
    at x=276..312. Corridor between them: x=96..276 (180" wide).
    Two 48"-dia tables centered at 1/3 and 2/3 of the corridor, north-clamped
    so the tables stay 6" south of the north wall for wall clearance.
    Chairs at south edge (facing south into the room, backs to north wall).
    """
    coll = get_or_create_collection("Round_Tables")
    ROUND_DIA = 48.0            # 48" diameter (standard 4-5 seat stacking round)
    N_CHAIRS_PER = 4            # 4 chairs per round table
    corridor_x0 = 96 + 6        # 6" east of NW stage
    corridor_x1 = 276 - 6       # 6" west of Storage A door
    corridor_w = corridor_x1 - corridor_x0     # 168"
    # 2 tables spaced so each has ROUND_DIA + margin around it.
    # Place centers at 1/4 and 3/4 of corridor.
    cx_left  = corridor_x0 + corridor_w * 0.25
    cx_right = corridor_x0 + corridor_w * 0.75
    # Center Y: must clear the booth run along the north wall.
    # Booth occupies y=0..BENCH_DEPTH (18) and back extends to y=18 as well.
    # 6" clearance south of booth front edge -> table north edge = 18+6 = 24.
    # Center Y = 24 + radius = 24 + 24 = 48.
    # Row-1 chair fronts sit at chair_y_top = 107.5, so south edge of table (72)
    # still gives 35" clearance -- ample walking room.
    cy = BENCH_DEPTH + 6 + ROUND_DIA / 2      # 48"

    import math as _m
    for (label, cxv) in (("RoundW", cx_left), ("RoundE", cx_right)):
        build_round_table(label, cxv, cy, ROUND_DIA, coll)
        # 4 chairs around each round, at 0/90/180/270 degrees from center.
        # Only place chairs on the S/E/W sides (skip NORTH -- backs against wall).
        seat_r = ROUND_DIA / 2 + 4    # chair front-edge 4" out from table edge
        # Coord convention: high Y = SOUTH (image-top), low Y = NORTH (near wall).
        # In math angles (0=+X, 90=+Y=SOUTH), we want chairs on the +Y (south) side
        # so the chair BACKS face north wall / table and seats face south into room.
        # 4 chairs fanned across the south half at 20, 70, 110, 160 deg.
        chair_angles_deg = [20, 70, 110, 160]
        for i, ang_deg in enumerate(chair_angles_deg):
            ang = _m.radians(ang_deg)
            # Chair CENTER = table center + (seat_r + CHAIR_D/2) * unit_vec
            r_center = seat_r + CHAIR_D / 2
            chr_cx = cxv + r_center * _m.cos(ang)
            chr_cy = cy + r_center * _m.sin(ang)
            # NW corner of chair footprint
            chr_x0 = chr_cx - CHAIR_W / 2
            chr_y0 = chr_cy - CHAIR_D / 2
            build_chair(f"{label}_chr{i}", chr_x0, chr_y0, coll)


def build_two_tops():
    coll = get_or_create_collection("Two_Tops")
    # Place a two-top to the wall side of each pool table, centered along its length.
    # v14 (corrected): BackR two-top was overlapping the new Kitchen door
    # (y=290..330). The user wants its IMAGE-BOTTOM chair (i.e. chair_S in the
    # stack, which sits at the HIGHEST y of the stack) aligned with the IMAGE-
    # BOTTOM edge of the BackR pool table. Image-bottom = lowest world Y because
    # the topdown camera has +Y pointing DOWN-IN-IMAGE inverted... actually:
    #   image-top = high Y = SOUTH (Main Entry side)
    #   image-bottom = low Y = NORTH (Back tables / classroom / stage side)
    # So "bottom of bottom-right pool table" = BackR's NORTH edge = y=241.
    # The stack chair closest to the image-bottom is chair_S (at y0+30..y0+42).
    # Align chair_S south edge (y0+42) to BackR north edge (y=241):
    #   y0 + 42 = 241  ->  y0 = 199.
    # Stack y = 199..241. Clears Kitchen door (y=290..330) with 49" gap.
    # v14c: move BackR two-top UP another 36" (3 ft) per user; was y0=199, now 163.
    #   Stack y=163..205 (chair_N=163..175, table=177..191, chair_S=193..205).
    #   Gap to BackR north edge (y=241) is 36" (matches classroom-to-BackR
    #   clearance after classroom shift).
    KITCHEN_Y0, KITCHEN_Y1 = 290, 330
    TWOTOP_STACK_LEN = CHAIR_D + 18 + CHAIR_D                     # 42
    # v15b: move BackR two-top CLOSER to the Kitchen door per user.
    # Place the stack's south (image-up) edge 6" north of the Kitchen door,
    # so y0 + 42 = 284 -> y0 = 242. Stack y=242..284. Aligns alongside the
    # BackR pool table (x=188..234) with no X conflict (two-top at x=298..316).
    BACKR_RELOCATE_Y0 = KITCHEN_Y0 - 6 - TWOTOP_STACK_LEN         # 242
    for (label, cx, ty) in POOL_TABLES:
        wall = 'L' if cx == xL_center else 'R'
        table_cy = ty + TBL_L / 2
        y0 = table_cy - TWOTOP_L / 2 - 14
        # v14 relocate: BackR's right-wall two-top moves to MainBR alignment.
        if wall == 'R' and label == 'BackR':
            y0 = BACKR_RELOCATE_Y0
            label = 'BackR_relocated'
        build_two_top(f"{wall}_{label}", y0, wall, coll)


# v15: stage parameters used by both build_lockers and build_stage.
STAGE_X0 = 0       # west wall (west-wall storage door REMOVED in v15)
STAGE_Y0 = 0       # against north wall
STAGE_W  = 96      # 8 ft long (along x)
STAGE_D  = 48      # 4 ft deep (along y)
STAGE_H  = 12      # 1 ft tall


def build_lockers():
    """v15k: authentic locker geometry per user product-photo reference.
    One BALL STORAGE LOCKER (24W x 18D x 72H, 3-zone: locked-top cabinet /
    open mesh ball-display middle / locked-bottom cabinet with padlock hasp)
    + one TRIPLE LOCKER (36W x 18D x 72H, 3 vertical narrow doors with key
    latches, vent slots top and bottom). Matte-black steel. Placed side-by-
    side, centered on the NW stage's north edge. Bookshelf sits in front."""
    coll = get_or_create_collection("Lockers_Shelving")
    metal_mat = get_or_create_color_material(
        "MAT_locker", (0.020, 0.020, 0.025, 1.0), roughness=0.45)
    door_mat = get_or_create_color_material(
        "MAT_locker_door", (0.030, 0.030, 0.035, 1.0), roughness=0.35)
    handle_mat = get_or_create_color_material(
        "MAT_locker_handle", (0.55, 0.55, 0.58, 1.0), roughness=0.20)
    interior_mat = get_or_create_color_material(
        "MAT_locker_interior", (0.05, 0.05, 0.06, 1.0), roughness=0.85)
    book_mat = get_or_create_color_material(
        "MAT_bookshelf", (0.14, 0.09, 0.05, 1.0), roughness=0.55)

    # ---------- placement -----------------------------------------------------
    lockers_total_w = BALL_LOCKER_W + TRIPLE_LOCKER_W       # 24 + 36 = 60
    locker_x_start = STAGE_X0 + (STAGE_W - lockers_total_w) / 2  # center on 96" stage
    door_thick = 0.4
    door_inset = 0.6

    # ---------- BALL STORAGE LOCKER (left, 24W) -------------------------------
    lx = locker_x_start
    ly = STAGE_Y0
    lz = STAGE_H
    make_box("Locker_Ball_shell",
             x=lx, y=ly, z=lz,
             w=BALL_LOCKER_W, l=LOCKER_L, h=LOCKER_H,
             material=metal_mat, collection=coll)
    TOP_H = 18.0
    MID_H = 30.0
    BOT_H = LOCKER_H - TOP_H - MID_H   # 24.0
    door_y = ly + LOCKER_L - door_thick - door_inset
    door_w_inset = 0.5
    door_w = BALL_LOCKER_W - 2 * door_w_inset
    # Top locked cabinet door
    top_z0 = lz + BOT_H + MID_H
    make_box("Locker_Ball_door_top",
             x=lx + door_w_inset, y=door_y, z=top_z0 + 0.5,
             w=door_w, l=door_thick, h=TOP_H - 1.0,
             material=door_mat, collection=coll)
    # Small silver lock cylinder on top door
    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * 0.5, depth=IN * 0.3,
        location=(IN * (lx + BALL_LOCKER_W / 2),
                  IN * (door_y + door_thick + 0.15),
                  IN * (top_z0 + TOP_H / 2)),
        rotation=(1.5707963, 0, 0),
        vertices=12,
    )
    lc = bpy.context.active_object
    lc.name = "Locker_Ball_lock_top"
    if lc.data.materials:
        lc.data.materials[0] = handle_mat
    else:
        lc.data.materials.append(handle_mat)
    move_to_collection(lc, coll)
    # Middle open ball-display cavity: dark interior back panel + balls + mesh bars
    mid_z0 = lz + BOT_H
    make_box("Locker_Ball_interior",
             x=lx + 1.0, y=ly + 1.0, z=mid_z0 + 0.5,
             w=BALL_LOCKER_W - 2.0, l=LOCKER_L - 2.5, h=MID_H - 1.0,
             material=interior_mat, collection=coll)
    ball_colors = [
        (0.85, 0.55, 0.15),  # basketball orange
        (0.95, 0.95, 0.95),  # soccer/volleyball white
        (0.35, 0.20, 0.10),  # football brown
    ]
    ball_r = 4.5
    ball_z = mid_z0 + 4.0 + ball_r
    ball_positions_x = [
        lx + BALL_LOCKER_W * 0.25,
        lx + BALL_LOCKER_W * 0.55,
        lx + BALL_LOCKER_W * 0.78,
    ]
    for i, (bx, bcolor) in enumerate(zip(ball_positions_x, ball_colors)):
        ball_mat_i = get_or_create_color_material(
            f"MAT_locker_ball_{i}",
            (bcolor[0], bcolor[1], bcolor[2], 1.0), roughness=0.55)
        by = ly + LOCKER_L / 2 + 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=IN * ball_r,
            location=(IN * bx, IN * by, IN * ball_z),
            segments=16, ring_count=10,
        )
        b = bpy.context.active_object
        b.name = f"Locker_Ball_ball_{i}"
        if b.data.materials:
            b.data.materials[0] = ball_mat_i
        else:
            b.data.materials.append(ball_mat_i)
        move_to_collection(b, coll)
    # Grille bars for the open display opening (5 vertical + top/bottom horizontal)
    bar_w = 0.25
    n_bars = 5
    for i in range(n_bars):
        frac = (i + 1) / (n_bars + 1)
        bar_x = lx + frac * BALL_LOCKER_W - bar_w / 2
        make_box(f"Locker_Ball_barV_{i}",
                 x=bar_x, y=ly + LOCKER_L - 0.5, z=mid_z0 + 0.3,
                 w=bar_w, l=0.3, h=MID_H - 0.6,
                 material=metal_mat, collection=coll)
    for zy_lbl, zy in (("bot", mid_z0), ("top", mid_z0 + MID_H - 0.5)):
        make_box(f"Locker_Ball_barH_{zy_lbl}",
                 x=lx, y=ly + LOCKER_L - 0.5, z=zy,
                 w=BALL_LOCKER_W, l=0.3, h=0.5,
                 material=metal_mat, collection=coll)
    # Bottom locked cabinet door + padlock hasp
    bot_z0 = lz
    make_box("Locker_Ball_door_bot",
             x=lx + door_w_inset, y=door_y, z=bot_z0 + 0.5,
             w=door_w, l=door_thick, h=BOT_H - 1.0,
             material=door_mat, collection=coll)
    make_box("Locker_Ball_hasp",
             x=lx + BALL_LOCKER_W / 2 - 0.75,
             y=door_y + door_thick + 0.05,
             z=bot_z0 + BOT_H - 6.0,
             w=1.5, l=0.4, h=2.0,
             material=handle_mat, collection=coll)

    # ---------- TRIPLE LOCKER (right, 36W) ------------------------------------
    tlx = locker_x_start + BALL_LOCKER_W
    tly = STAGE_Y0
    tlz = STAGE_H
    make_box("Locker_Triple_shell",
             x=tlx, y=tly, z=tlz,
             w=TRIPLE_LOCKER_W, l=LOCKER_L, h=LOCKER_H,
             material=metal_mat, collection=coll)
    n_doors = 3
    door_inset_side = 0.5
    door_top_inset = 2.5
    door_bot_inset = 2.5
    door_gap = 0.4
    total_gap = (n_doors - 1) * door_gap + 2 * door_inset_side
    each_door_w = (TRIPLE_LOCKER_W - total_gap) / n_doors
    door_h = LOCKER_H - door_top_inset - door_bot_inset
    door_y_t = tly + LOCKER_L - door_thick - door_inset
    for di in range(n_doors):
        dx = tlx + door_inset_side + di * (each_door_w + door_gap)
        make_box(f"Locker_Triple_door_{di}",
                 x=dx, y=door_y_t, z=tlz + door_bot_inset,
                 w=each_door_w, l=door_thick, h=door_h,
                 material=door_mat, collection=coll)
        # Key latch handle mid-door
        handle_w = 1.8
        handle_h = 1.2
        make_box(f"Locker_Triple_handle_{di}",
                 x=dx + each_door_w / 2 - handle_w / 2,
                 y=door_y_t + door_thick + 0.05,
                 z=tlz + LOCKER_H / 2 - handle_h / 2,
                 w=handle_w, l=0.3, h=handle_h,
                 material=handle_mat, collection=coll)
        # Vent slots (3 top + 3 bottom on each door)
        vent_slot_w = each_door_w * 0.6
        vent_slot_h = 0.25
        vent_slot_x = dx + (each_door_w - vent_slot_w) / 2
        for vi in range(3):
            vent_z_top = tlz + LOCKER_H - door_top_inset + 0.4 + vi * 0.5
            vent_z_bot = tlz + 0.4 + vi * 0.5
            for tag, vz in (("top", vent_z_top), ("bot", vent_z_bot)):
                make_box(f"Locker_Triple_vent_{tag}_{di}_{vi}",
                         x=vent_slot_x, y=door_y_t + door_thick + 0.02,
                         z=vz,
                         w=vent_slot_w, l=0.05, h=vent_slot_h,
                         material=interior_mat, collection=coll)

    # Bookshelf: 60" wide x 12" deep x 48" tall. Sits on stage in front of
    # lockers, centered along the stage's long axis. Gap to lockers ~6".
    BOOK_W = 60
    BOOK_L = 12
    BOOK_H = 48
    book_x = STAGE_X0 + (STAGE_W - BOOK_W) / 2
    book_y = STAGE_Y0 + LOCKER_L + 6              # 18 + 6 = 24
    make_box("Bookshelf",
             x=book_x, y=book_y, z=STAGE_H,
             w=BOOK_W, l=BOOK_L, h=BOOK_H,
             material=book_mat, collection=coll)


def build_stage():
    """v15: 4'x8'x1' demo/instructor stage at NW corner (image bottom-left).
    West-wall storage door was removed in v15, so the stage now sits flush
    against the west wall. Lockers + bookshelf sit ON TOP of this stage.
    Painted matte black."""
    coll = get_or_create_collection("Stage")
    stage_mat = get_or_create_color_material(
        "MAT_stage_black", (0.01, 0.01, 0.01, 1.0), roughness=0.85)
    make_box("Stage_Platform",
             x=STAGE_X0, y=STAGE_Y0, z=0,
             w=STAGE_W, l=STAGE_D, h=STAGE_H,
             material=stage_mat, collection=coll)


def build_hvac():
    coll = get_or_create_collection("HVAC_Equipment")
    chase_mat = get_or_create_color_material(
        "MAT_hvac_chase", (0.85, 0.85, 0.82, 1.0), roughness=0.6)
    grille_mat = get_or_create_color_material(
        "MAT_hvac_grille", (0.40, 0.40, 0.42, 1.0), roughness=0.3)
    make_box("HVAC_Chase",
             x=HVAC_X, y=HVAC_Y0, z=0,
             w=HVAC_W, l=HVAC_L, h=HVAC_H_VOL,
             material=chase_mat, collection=coll)
    make_box("HVAC_Grille",
             x=HVAC_W - 0.5, y=HVAC_Y0 + 6, z=72,
             w=1, l=HVAC_L - 12, h=24,
             material=grille_mat, collection=coll)


def build_stow_column():
    coll = get_or_create_collection("Partition_Stow")
    wood_mat = get_material("MAT_wood_panel",
                            fallback_rgba=(0.42, 0.28, 0.16, 1.0),
                            fallback_roughness=0.55)
    stow_x = ROOM_W - STOW_W
    stow_y = BEAM_Y - STOW_L / 2
    make_box("Partition_Stow",
             x=stow_x, y=stow_y, z=0,
             w=STOW_W, l=STOW_L, h=STOW_H_VOL,
             material=wood_mat, collection=coll)


def build_railing():
    coll = get_or_create_collection("Wrought_Iron_Railing")
    iron_mat = get_or_create_color_material(
        "MAT_wrought_iron", (0.05, 0.05, 0.05, 1.0), roughness=0.45)
    rail_x_start = 0
    rail_x_end   = STAIR_RUN_X
    make_box("Railing_N",
             x=rail_x_start, y=ENTRY_Y0 - RAIL_T, z=0,
             w=rail_x_end - rail_x_start, l=RAIL_T, h=RAIL_H,
             material=iron_mat, collection=coll)
    make_box("Railing_S",
             x=rail_x_start, y=ENTRY_Y1, z=0,
             w=rail_x_end - rail_x_start, l=RAIL_T, h=RAIL_H,
             material=iron_mat, collection=coll)


# ============================================================================
# LIGHT FIXTURES (mesh shades) + REAL BLENDER LIGHTS
# ============================================================================

def build_pendant_fixtures_and_lights():
    """One green-shade pendant box + hanging rod per pool table, plus a real
    AREA light inside each shade pointing straight down."""
    coll_mesh  = get_or_create_collection("Pendant_Fixtures")
    coll_light = get_or_create_collection("Lights")

    shade_mat = get_or_create_color_material(
        "MAT_pendant_shade", (0.05, 0.20, 0.08, 1.0), roughness=0.4,
        emission=(0.05, 0.20, 0.08, 1.0), emission_strength=0.2)
    rod_mat = get_or_create_color_material(
        "MAT_pendant_rod", (0.10, 0.10, 0.10, 1.0), roughness=0.4)
    bulb_mat = get_or_create_color_material(
        "MAT_pendant_bulb", (1.0, 0.95, 0.80, 1.0), roughness=0.1,
        emission=(1.0, 0.92, 0.65, 1.0), emission_strength=6.0)

    for (name, cx, ty) in POOL_TABLES:
        center_y = ty + TBL_L / 2
        # Shade
        make_box(f"Pendant_{name}_shade",
                 x=cx - PEND_W / 2, y=center_y - PEND_L / 2, z=PEND_Z,
                 w=PEND_W, l=PEND_L, h=PEND_H,
                 material=shade_mat, collection=coll_mesh)
        # Bulb plate (interior) -- glows
        make_box(f"Pendant_{name}_bulbplate",
                 x=cx - PEND_W / 2 + 2, y=center_y - PEND_L / 2 + 2,
                 z=PEND_Z + 0.5,
                 w=PEND_W - 4, l=PEND_L - 4, h=0.5,
                 material=bulb_mat, collection=coll_mesh)
        # Hanging rod
        make_box(f"Pendant_{name}_rod",
                 x=cx - 0.5, y=center_y - 0.5, z=PEND_Z + PEND_H,
                 w=1, l=1, h=CEIL_H - PEND_Z - PEND_H,
                 material=rod_mat, collection=coll_mesh)
        # Real Blender AREA light just below the shade
        add_area_light(
            name=f"Light_Pendant_{name}",
            x_in=cx,
            y_in=center_y,
            z_in=PEND_Z - 0.5,
            size_w_in=PEND_W - 6,
            size_l_in=PEND_L - 6,
            color=(1.0, 0.92, 0.78),    # warm tungsten-ish
            energy=800.0,
            collection=coll_light,
        )


def build_ceiling_troffers_and_lights():
    """Suspended-ceiling 2'x4' troffer grid with mesh frames + diffusing lenses
    + a real AREA light below each lens for diffused ceiling fill."""
    coll_mesh  = get_or_create_collection("Ceiling_Troffers")
    coll_light = get_or_create_collection("Lights")

    frame_mat = get_or_create_color_material(
        "MAT_troffer_frame", (0.92, 0.92, 0.92, 1.0), roughness=0.45)
    lens_mat = get_or_create_color_material(
        "MAT_troffer_lens", (0.96, 0.96, 0.96, 1.0), roughness=0.65,
        emission=(1.0, 0.97, 0.92, 1.0), emission_strength=2.5)

    z_frame_top = CEIL_H - 0.5            # housing sits in ceiling plane
    z_frame_bot = z_frame_top - TROFFER_H

    # 2'x2' acoustic grid -- 2'x4' fixtures align on the long axis (Y) so each
    # fixture replaces two adjacent grid cells.
    # Avoid the beam zone (BEAM_Y -/+ 8), HVAC chase, partition stow column,
    # and the pendant footprint over pool tables.

    # x-positions for fixtures (2 ft on center)
    troffer_centers_x = []
    x = 12 + TROFFER_W / 2
    while x + TROFFER_W / 2 <= ROOM_W - 12:
        troffer_centers_x.append(x)
        x += TROFFER_W + 24       # space between fixtures (24") to keep budget reasonable

    # y-positions (4-ft fixtures on 8-ft centers along Y)
    troffer_centers_y = []
    y = 24 + TROFFER_L / 2
    while y + TROFFER_L / 2 <= ROOM_L - 24:
        troffer_centers_y.append(y)
        y += TROFFER_L + 48       # 4-ft gap

    pendant_footprints = []
    for (name, cx, ty) in POOL_TABLES:
        pendant_footprints.append((
            cx - PEND_W / 2 - 8, cx + PEND_W / 2 + 8,
            ty + TBL_L / 2 - PEND_L / 2 - 8, ty + TBL_L / 2 + PEND_L / 2 + 8,
        ))

    def conflicts(cx, cy):
        if abs(cy - BEAM_Y) < 14:
            return True
        # HVAC chase footprint
        if cx - TROFFER_W / 2 < HVAC_W and HVAC_Y0 - 6 < cy < HVAC_Y0 + HVAC_L + 6:
            return True
        # Partition stow footprint
        if cx + TROFFER_W / 2 > ROOM_W - STOW_W and BEAM_Y - STOW_L/2 - 6 < cy < BEAM_Y + STOW_L/2 + 6:
            return True
        # Pendant footprint
        for (px0, px1, py0, py1) in pendant_footprints:
            if px0 < cx < px1 and py0 < cy < py1:
                return True
        return False

    count = 0
    for cx in troffer_centers_x:
        for cy in troffer_centers_y:
            if conflicts(cx, cy):
                continue
            # Frame
            make_box(f"Troffer_{count:02d}_frame",
                     x=cx - TROFFER_W / 2, y=cy - TROFFER_L / 2, z=z_frame_bot,
                     w=TROFFER_W, l=TROFFER_L, h=TROFFER_H,
                     material=frame_mat, collection=coll_mesh)
            # Lens (thin, slightly lower) -- emissive
            make_box(f"Troffer_{count:02d}_lens",
                     x=cx - TROFFER_W / 2 + 1, y=cy - TROFFER_L / 2 + 1,
                     z=z_frame_bot - 0.25,
                     w=TROFFER_W - 2, l=TROFFER_L - 2, h=0.25,
                     material=lens_mat, collection=coll_mesh)
            # Real AREA light
            add_area_light(
                name=f"Light_Troffer_{count:02d}",
                x_in=cx, y_in=cy, z_in=z_frame_bot - 0.5,
                size_w_in=TROFFER_W - 2, size_l_in=TROFFER_L - 2,
                color=(1.0, 0.97, 0.92),       # neutral fluorescent-ish
                energy=180.0,
                collection=coll_light,
            )
            count += 1
    return count


# v11: One standard 58" cue per pool table -- tip resting on felt near the
#      wall-side rail, butt pointing toward the matching two-top. This shows
#      the physical encroachment of a player's cue stroke into the service lane.
def build_cues():
    # v15L3: cue geometry realistic-rest update.
    #   - Whole cue shifted 12" (1 ft) closer to the table (deeper onto felt)
    #   - Tip Z lowered to TBL_H (32") so tip touches the felt.
    #   - Butt Z raised to 38" (2.5" above 35.5" rail top) so cue clears rail.
    #   - Rendered as two rotated tapered cylinders (was axis-aligned boxes).
    import math
    from mathutils import Vector
    coll = get_or_create_collection("Cues")
    shaft_mat = get_or_create_color_material(
        "MAT_cue_shaft", (0.85, 0.72, 0.50, 1.0), roughness=0.35)
    butt_mat = get_or_create_color_material(
        "MAT_cue_butt", (0.20, 0.12, 0.08, 1.0), roughness=0.40)
    CUE_LEN = 58.0            # standard playing cue
    CUE_TIP_R = 0.30          # ~12.75mm tip radius
    CUE_BUTT_R = 0.625        # ~31mm butt radius
    CUE_TIP_Z = TBL_H         # 32" - tip touches the felt
    CUE_BUTT_Z = 38.0         # 2.5" above 35.5" rail top
    INSET_FROM_RAIL = 16      # was 4"; shifted 12" closer to table (deeper onto felt)

    def _make_cue_seg(name, p0, p1, radius, mat):
        """Cylinder mesh between two inch-coord 3D points."""
        dx = p1[0]-p0[0]; dy = p1[1]-p0[1]; dz = p1[2]-p0[2]
        length_in = math.sqrt(dx*dx + dy*dy + dz*dz)
        mid = (IN*((p0[0]+p1[0])/2), IN*((p0[1]+p1[1])/2), IN*((p0[2]+p1[2])/2))
        bpy.ops.mesh.primitive_cylinder_add(
            radius=IN*radius, depth=IN*length_in,
            vertices=16, location=mid)
        obj = bpy.context.active_object
        obj.name = name
        v = Vector((dx, dy, dz))
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = v.to_track_quat('Z', 'Y')
        for p in obj.data.polygons:
            p.use_smooth = True
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        move_to_collection(obj, coll)
        return obj

    rise = CUE_BUTT_Z - CUE_TIP_Z                # 6.0"
    run  = math.sqrt(CUE_LEN*CUE_LEN - rise*rise)  # ~57.69"

    for (label, cx, ty) in POOL_TABLES:
        cy = ty + TBL_L / 2
        wall = 'L' if cx == xL_center else 'R'
        if wall == 'L':
            tip_x  = cx - TBL_W/2 + INSET_FROM_RAIL  # 16" onto felt (was 4")
            butt_x = tip_x - run                     # butt west of tip
        else:
            tip_x  = cx + TBL_W/2 - INSET_FROM_RAIL
            butt_x = tip_x + run
        # Split at 2/3 along cue: shaft (tip-side 2/3) + butt (outer 1/3)
        t = 2.0 / 3.0
        sx = tip_x + (butt_x - tip_x) * t
        sy = cy
        sz = CUE_TIP_Z + (CUE_BUTT_Z - CUE_TIP_Z) * t
        split_r = CUE_TIP_R + (CUE_BUTT_R - CUE_TIP_R) * t
        _make_cue_seg(f"Cue_{label}_shaft",
                      (tip_x, cy, CUE_TIP_Z), (sx, sy, sz),
                      radius=(CUE_TIP_R + split_r)/2, mat=shaft_mat)
        _make_cue_seg(f"Cue_{label}_butt",
                      (sx, sy, sz), (butt_x, cy, CUE_BUTT_Z),
                      radius=(split_r + CUE_BUTT_R)/2, mat=butt_mat)


# ============================================================================
# RUN
# ============================================================================

build_pool_tables()
build_cues()
build_classroom()
build_round_tables()
build_two_tops()
build_buffet()
# v15b: bench restored next to NW stage, clear of Storage A door.
build_bench()
build_lockers()
build_stage()
build_hvac()
build_stow_column()
build_railing()
build_pendant_fixtures_and_lights()
troffer_count = build_ceiling_troffers_and_lights()

# v11: SERVICE LOOPS pushed OUTWARD to almost touch the two-tops, away from
#      pool tables. Door stubs now connect to RIGHT wall (Main Entry at top-
#      right corner stair landing, Kitchen on right wall just below HVAC).
#      No left-wall stubs.
def build_clearance_paths():
    coll = get_or_create_collection("Clearance_Paths")
    mat = bpy.data.materials.new("MAT_clearance")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.0, 1.0, 0.2, 1.0)
        bsdf.inputs["Alpha"].default_value = 0.45
        bsdf.inputs["Roughness"].default_value = 0.9
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.0, 1.0, 0.2, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.6
    PATH_Z = 0.10
    LANE_W = 30  # 30" service lane

    def path_seg(name, x, y, w, l):
        if w <= 0 or l <= 0:
            return
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(IN * (x + w/2), IN * (y + l/2), IN * (PATH_Z + 0.05))
        )
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (IN * w, IN * l, IN * 0.1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        move_to_collection(obj, coll)

    # --- Outward lane centerlines (v15) ---
    # v15 changes: west-wall storage door REMOVED, stage flush against west wall
    # at x=0..96, y=0..48. Lockers + bookshelf on top of stage. TWO new Storage
    # doors at NE corner: Storage A on N wall x=276..312, Storage B on E wall
    # y=4..40. Lanes now wrap around the classroom ends and exit at the
    # NE-corner Storage doors instead of the old west-wall door.
    west_x0 = 18
    west_x1 = west_x0 + LANE_W                              # 48

    east_x0 = 265
    east_x1 = east_x0 + LANE_W                              # 295
    east_jog_x0 = 258
    east_jog_x1 = east_jog_x0 + LANE_W                      # 288
    HVAC_Y0, HVAC_Y1 = 338, 380

    south_y0 = 637
    south_y1 = south_y0 + LANE_W                            # 667

    # North classroom-wrap lane: just south of back classroom chairs
    # (back_chair_top_y = 103). Lane y=70..100 (3" clearance to chairs).
    nclass_y0 = 70
    nclass_y1 = nclass_y0 + LANE_W                          # 100

    # West-of-classroom narrow vertical: between west wall and classroom west
    # edge (classroom x0 = 32). Lane x=2..32. Connects nclass to west lane.
    wclass_x0 = 2
    wclass_x1 = wclass_x0 + LANE_W                          # 32

    # --- West vertical (south of classroom only) ---
    # Stage at x=0..96 y=0..48 and classroom at x=32..284 y=103..205 both
    # block the natural west lane x=18..48 in the north half. Run it from
    # north of BackL (y=235) down to the south corridor.
    path_seg("Path_WestCorridor",
             x=west_x0, y=235, w=LANE_W, l=south_y1 - 235)

    # --- West-of-classroom vertical (connects nclass wrap to west vertical) ---
    path_seg("Path_WestOfClassroom",
             x=wclass_x0, y=nclass_y1, w=LANE_W, l=235 - nclass_y1)

    # --- East vertical: split around HVAC ---
    # v15c: classroom narrowed to x=56..260, so east lane x=265..295 is now
    # clear of the classroom and runs full-length from N wall to S corridor.
    path_seg("Path_EastCorridor_N",
             x=east_x0, y=0, w=LANE_W, l=HVAC_Y0)
    path_seg("Path_EastCorridor_jog",
             x=east_jog_x0, y=HVAC_Y0, w=LANE_W, l=HVAC_Y1 - HVAC_Y0)
    path_seg("Path_EastCorridor_S",
             x=east_x0, y=HVAC_Y1, w=LANE_W, l=south_y1 - HVAC_Y1)
    if east_x0 < east_jog_x1:
        path_seg("Path_EastCorridor_connect_N",
                 x=east_jog_x0, y=HVAC_Y0 - 6, w=east_x1 - east_jog_x0, l=12)
        path_seg("Path_EastCorridor_connect_S",
                 x=east_jog_x0, y=HVAC_Y1 - 6, w=east_x1 - east_jog_x0, l=12)

    # --- Horizontal lanes ---
    # North-of-classroom wrap: spans from west-of-classroom lane to east lane.
    path_seg("Path_NorthClassWrap",
             x=wclass_x0, y=nclass_y0, w=east_x1 - wclass_x0, l=LANE_W)
    # South lane: from west corridor to right wall (Main Entry).
    path_seg("Path_SouthCorridor",
             x=west_x0, y=south_y0, w=ROOM_W - west_x0, l=LANE_W)

    # --- Door stubs ---
    # Kitchen (E wall y=290..330): stub from east lane to right wall.
    path_seg("Path_door_Kitchen_stub",
             x=east_x1, y=295, w=ROOM_W - east_x1, l=LANE_W)
    # Storage B (E wall y=4..40, NE-corner east door): stub east lane -> wall.
    path_seg("Path_door_StorageB_stub",
             x=east_x1, y=4, w=ROOM_W - east_x1, l=36)
    # Storage A (N wall x=276..312, NE-corner north door): east lane already
    # overlaps x=276..295; cover the rest (x=295..316) with a small stub.
    path_seg("Path_door_StorageA_stub",
             x=east_x1, y=0, w=ROOM_W - east_x1, l=LANE_W)

build_clearance_paths()

# ===== v15h humans start =====
# Procedural low-poly human figures for scale + activity.
# Two poses: standing pool player (holding a cue) and seated two-top patron.
# All measurements in inches (converted via IN scalar). Figure height ~68".

import math as _math_v15h

# Palette (RGBA)
SKIN_TONES = [
    (0.86, 0.72, 0.58, 1.0),  # light warm
    (0.66, 0.48, 0.34, 1.0),  # medium
    (0.42, 0.28, 0.18, 1.0),  # dark
]
SHIRT_COLORS = [
    (0.15, 0.28, 0.55, 1.0),  # navy
    (0.55, 0.10, 0.10, 1.0),  # crimson
    (0.10, 0.35, 0.20, 1.0),  # forest
    (0.85, 0.75, 0.35, 1.0),  # mustard
    (0.55, 0.55, 0.60, 1.0),  # steel gray
    (0.05, 0.05, 0.08, 1.0),  # black
]
PANT_COLORS = [
    (0.10, 0.12, 0.18, 1.0),  # dark denim
    (0.28, 0.22, 0.14, 1.0),  # khaki
    (0.06, 0.06, 0.07, 1.0),  # black slacks
]
HAIR_COLORS = [
    (0.10, 0.08, 0.05, 1.0),  # black-brown
    (0.28, 0.18, 0.08, 1.0),  # brown
    (0.55, 0.42, 0.20, 1.0),  # dirty blond
    (0.20, 0.20, 0.22, 1.0),  # salt-and-pepper
]

def _mat(name, rgba, rough=0.65):
    return get_or_create_color_material(name, rgba, roughness=rough)

def _add_cylinder(name, x_center_in, y_center_in, z_bottom_in, r_in, h_in,
                  material, coll, verts=12):
    """Add an upright cylinder standing on its bottom face."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * r_in, depth=IN * h_in,
        location=(IN * x_center_in, IN * y_center_in,
                  IN * (z_bottom_in + h_in / 2)),
        vertices=verts,
    )
    o = bpy.context.active_object
    o.name = name
    if o.data.materials:
        o.data.materials[0] = material
    else:
        o.data.materials.append(material)
    move_to_collection(o, coll)
    return o

def _add_sphere(name, x_in, y_in, z_in, r_in, material, coll, segs=14):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=IN * r_in,
        location=(IN * x_in, IN * y_in, IN * z_in),
        segments=segs, ring_count=segs // 2,
    )
    o = bpy.context.active_object
    o.name = name
    if o.data.materials:
        o.data.materials[0] = material
    else:
        o.data.materials.append(material)
    move_to_collection(o, coll)
    return o

def _add_oriented_cylinder(name, x0_in, y0_in, z0_in, x1_in, y1_in, z1_in,
                            r_in, material, coll, verts=10):
    """Cylinder from point A to point B (used for arms/legs in any direction)."""
    dx = x1_in - x0_in
    dy = y1_in - y0_in
    dz = z1_in - z0_in
    length = _math_v15h.sqrt(dx*dx + dy*dy + dz*dz)
    if length < 1e-6:
        return None
    cx = (x0_in + x1_in) / 2
    cy = (y0_in + y1_in) / 2
    cz = (z0_in + z1_in) / 2
    # Default cylinder axis is +Z. Rotate to align with (dx,dy,dz).
    # We need rotation that maps (0,0,1) -> (dx/L, dy/L, dz/L).
    ux, uy, uz = dx/length, dy/length, dz/length
    # Use axis-angle: axis = (0,0,1) x u, angle = acos(uz)
    ax = -uy
    ay = ux
    az = 0.0
    ang = _math_v15h.acos(max(-1.0, min(1.0, uz)))
    axis_len = _math_v15h.sqrt(ax*ax + ay*ay)
    if axis_len < 1e-6:
        # Already vertical (up or down)
        rot_axis = (1.0, 0.0, 0.0)
        ang = 0.0 if uz > 0 else _math_v15h.pi
    else:
        rot_axis = (ax/axis_len, ay/axis_len, az/axis_len)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=IN * r_in, depth=IN * length,
        location=(IN * cx, IN * cy, IN * cz),
        vertices=verts,
    )
    o = bpy.context.active_object
    o.rotation_mode = 'AXIS_ANGLE'
    o.rotation_axis_angle = (ang, rot_axis[0], rot_axis[1], rot_axis[2])
    o.name = name
    if o.data.materials:
        o.data.materials[0] = material
    else:
        o.data.materials.append(material)
    move_to_collection(o, coll)
    return o

def build_pool_player(name, cx_in, cy_in, facing_yaw_rad, palette_seed, coll):
    """Standing pool player at (cx, cy) with feet on floor.
    facing_yaw_rad: angle in radians. 0 = facing +X (east), pi/2 = facing +Y (south),
    pi = facing -X (west), -pi/2 = facing -Y (north).
    The figure stands with legs together; the cue-holding arm extends FORWARD
    (in the facing direction) to grip the cue butt; the bridge arm points slightly
    forward and to the side over the table.
    palette_seed: int used to deterministically pick shirt/pants/skin/hair.
    """
    # Deterministic palette pick
    skin = _mat(f"MAT_person_skin_{palette_seed % len(SKIN_TONES)}",
                SKIN_TONES[palette_seed % len(SKIN_TONES)])
    shirt = _mat(f"MAT_person_shirt_{palette_seed % len(SHIRT_COLORS)}",
                 SHIRT_COLORS[palette_seed % len(SHIRT_COLORS)])
    pants = _mat(f"MAT_person_pants_{palette_seed % len(PANT_COLORS)}",
                 PANT_COLORS[palette_seed % len(PANT_COLORS)])
    hair = _mat(f"MAT_person_hair_{palette_seed % len(HAIR_COLORS)}",
                HAIR_COLORS[palette_seed % len(HAIR_COLORS)])
    shoe = _mat("MAT_person_shoe", (0.03, 0.03, 0.03, 1.0), rough=0.5)

    # Body proportions (inches) for a ~68" (5'8") figure
    FOOT_H = 1.2
    LEG_LEN = 32
    LEG_R = 2.2
    HIP_H = 5
    HIP_W = 10
    HIP_D = 6
    TORSO_H = 20
    TORSO_W = 13
    TORSO_D = 7
    NECK_H = 2
    NECK_R = 1.7
    HEAD_R = 4.2
    ARM_UP_LEN = 11
    ARM_LO_LEN = 12
    ARM_R = 1.5

    # Z levels (feet on floor at z=0)
    z_foot_bottom = 0
    z_leg_bottom = FOOT_H
    z_leg_top = z_leg_bottom + LEG_LEN
    z_hip_bottom = z_leg_top
    z_hip_top = z_hip_bottom + HIP_H
    z_torso_bottom = z_hip_top
    z_torso_top = z_torso_bottom + TORSO_H
    z_neck_bottom = z_torso_top
    z_neck_top = z_neck_bottom + NECK_H
    z_head_center = z_neck_top + HEAD_R
    z_shoulder = z_torso_top - 2   # slightly below top of torso

    # Facing basis: forward vector (fx, fy), right vector (rx, ry)
    fx = _math_v15h.cos(facing_yaw_rad)
    fy = _math_v15h.sin(facing_yaw_rad)
    rx = _math_v15h.cos(facing_yaw_rad - _math_v15h.pi/2)
    ry = _math_v15h.sin(facing_yaw_rad - _math_v15h.pi/2)

    def offset(cx, cy, forward, right):
        return (cx + forward * fx + right * rx,
                cy + forward * fy + right * ry)

    # Feet (two small dark boxes)
    for side, sign in [("L", -1), ("R", +1)]:
        fx_c, fy_c = offset(cx_in, cy_in, 0, sign * 2.5)
        _add_cylinder(f"P_{name}_foot_{side}", fx_c, fy_c, z_foot_bottom,
                      1.8, FOOT_H, shoe, coll, verts=8)
    # Legs (two cylinders)
    for side, sign in [("L", -1), ("R", +1)]:
        lx, ly = offset(cx_in, cy_in, 0, sign * 2.5)
        _add_cylinder(f"P_{name}_leg_{side}", lx, ly, z_leg_bottom,
                      LEG_R, LEG_LEN, pants, coll, verts=10)
    # Hips
    hcx, hcy = cx_in, cy_in
    make_box(f"P_{name}_hips",
             x=hcx - HIP_W/2, y=hcy - HIP_D/2, z=z_hip_bottom,
             w=HIP_W, l=HIP_D, h=HIP_H,
             material=pants, collection=coll)
    # Torso (rotated to face forward -- but since it's roughly a square-ish
    # cross section we'll just make a box aligned with the facing frame)
    # For simplicity, use a box in world coords; the width axis is "right" and
    # depth axis is "forward". We'll add it as a box then rotate.
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(IN * hcx, IN * hcy, IN * (z_torso_bottom + TORSO_H/2)),
    )
    torso = bpy.context.active_object
    torso.scale = (IN * TORSO_W, IN * TORSO_D, IN * TORSO_H)
    torso.rotation_euler = (0, 0, facing_yaw_rad - _math_v15h.pi/2)
    torso.name = f"P_{name}_torso"
    if torso.data.materials:
        torso.data.materials[0] = shirt
    else:
        torso.data.materials.append(shirt)
    move_to_collection(torso, coll)

    # Neck
    _add_cylinder(f"P_{name}_neck", cx_in, cy_in, z_neck_bottom,
                  NECK_R, NECK_H, skin, coll, verts=10)
    # Head
    _add_sphere(f"P_{name}_head", cx_in, cy_in, z_head_center,
                HEAD_R, skin, coll, segs=14)
    # Hair (slightly larger cap on top rear of head)
    hair_x, hair_y = offset(cx_in, cy_in, -0.6, 0)
    _add_sphere(f"P_{name}_hair", hair_x, hair_y, z_head_center + 1.2,
                HEAD_R * 0.9, hair, coll, segs=14)

    # Arms -- shooting stance:
    #   BACK arm (cue-holding): shoulder -> elbow (down/back) -> hand (forward-down)
    #     gripping the cue butt. Hand extends about 8-10" behind body at ~hip-plus level.
    #   FRONT arm (bridge): shoulder -> elbow -> hand extending FORWARD onto the table
    #     rail at table height.
    # We pick which arm is which by facing convention: right hand is on the
    # +right side. For our purposes, always: right = cue butt, left = bridge.
    r_sh_x, r_sh_y = offset(cx_in, cy_in, 0, +TORSO_W/2)
    l_sh_x, l_sh_y = offset(cx_in, cy_in, 0, -TORSO_W/2)

    # BACK/CUE hand target: pulled back and slightly down
    r_elbow_x, r_elbow_y = offset(r_sh_x, r_sh_y, -4, +2)
    r_elbow_z = z_shoulder - ARM_UP_LEN * 0.8
    r_hand_x, r_hand_y = offset(r_elbow_x, r_elbow_y, -6, +1)
    r_hand_z = z_shoulder - 8  # ~hip level; grips the cue butt

    # BRIDGE hand target: forward onto table, at table height (TBL_H = 32)
    l_elbow_x, l_elbow_y = offset(l_sh_x, l_sh_y, 4, -1)
    l_elbow_z = z_shoulder - 4
    l_hand_x, l_hand_y = offset(l_elbow_x, l_elbow_y, 10, -1)
    l_hand_z = TBL_H + 2  # bridge sits just above rail

    # Right arm (cue) -- upper + lower
    _add_oriented_cylinder(f"P_{name}_arm_R_up",
        r_sh_x, r_sh_y, z_shoulder, r_elbow_x, r_elbow_y, r_elbow_z,
        ARM_R, shirt, coll, verts=8)
    _add_oriented_cylinder(f"P_{name}_arm_R_lo",
        r_elbow_x, r_elbow_y, r_elbow_z, r_hand_x, r_hand_y, r_hand_z,
        ARM_R * 0.85, skin, coll, verts=8)
    _add_sphere(f"P_{name}_hand_R", r_hand_x, r_hand_y, r_hand_z,
                ARM_R * 1.1, skin, coll, segs=10)

    # Left arm (bridge)
    _add_oriented_cylinder(f"P_{name}_arm_L_up",
        l_sh_x, l_sh_y, z_shoulder, l_elbow_x, l_elbow_y, l_elbow_z,
        ARM_R, shirt, coll, verts=8)
    _add_oriented_cylinder(f"P_{name}_arm_L_lo",
        l_elbow_x, l_elbow_y, l_elbow_z, l_hand_x, l_hand_y, l_hand_z,
        ARM_R * 0.85, skin, coll, verts=8)
    _add_sphere(f"P_{name}_hand_L", l_hand_x, l_hand_y, l_hand_z,
                ARM_R * 1.1, skin, coll, segs=10)

    # Return grip locations so caller can attach a cue butt / bridge point
    return {
        "cue_hand": (r_hand_x, r_hand_y, r_hand_z),
        "bridge_hand": (l_hand_x, l_hand_y, l_hand_z),
    }


def build_seated_patron(name, seat_cx_in, seat_cy_in, facing_yaw_rad,
                        seat_z_in, palette_seed, coll):
    """Seated figure. Butt on the seat at (seat_cx, seat_cy, seat_z), thighs
    forward, shins vertical down, torso upright, arms slightly forward as if
    resting hands on the table edge / lap.
    """
    skin = _mat(f"MAT_person_skin_{palette_seed % len(SKIN_TONES)}",
                SKIN_TONES[palette_seed % len(SKIN_TONES)])
    shirt = _mat(f"MAT_person_shirt_{palette_seed % len(SHIRT_COLORS)}",
                 SHIRT_COLORS[palette_seed % len(SHIRT_COLORS)])
    pants = _mat(f"MAT_person_pants_{palette_seed % len(PANT_COLORS)}",
                 PANT_COLORS[palette_seed % len(PANT_COLORS)])
    hair = _mat(f"MAT_person_hair_{palette_seed % len(HAIR_COLORS)}",
                HAIR_COLORS[palette_seed % len(HAIR_COLORS)])
    shoe = _mat("MAT_person_shoe", (0.03, 0.03, 0.03, 1.0), rough=0.5)

    # Facing basis
    fx = _math_v15h.cos(facing_yaw_rad)
    fy = _math_v15h.sin(facing_yaw_rad)
    rx = _math_v15h.cos(facing_yaw_rad - _math_v15h.pi/2)
    ry = _math_v15h.sin(facing_yaw_rad - _math_v15h.pi/2)
    def offset(cx, cy, forward, right):
        return (cx + forward * fx + right * rx,
                cy + forward * fy + right * ry)

    HIP_H = 5
    HIP_W = 10
    HIP_D = 8
    TORSO_H = 20
    TORSO_W = 13
    TORSO_D = 7
    NECK_H = 2
    NECK_R = 1.7
    HEAD_R = 4.2
    THIGH_LEN = 15  # horizontal
    SHIN_LEN = 15   # vertical down from knee
    LEG_R = 2.2
    ARM_UP_LEN = 11
    ARM_LO_LEN = 12
    ARM_R = 1.5

    # Hips center on seat top
    z_hip_bottom = seat_z_in
    z_hip_top = z_hip_bottom + HIP_H
    z_torso_bottom = z_hip_top
    z_torso_top = z_torso_bottom + TORSO_H
    z_neck_bottom = z_torso_top
    z_neck_top = z_neck_bottom + NECK_H
    z_head_center = z_neck_top + HEAD_R
    z_shoulder = z_torso_top - 2

    # Hips block
    make_box(f"P_{name}_hips",
             x=seat_cx_in - HIP_W/2, y=seat_cy_in - HIP_D/2, z=z_hip_bottom,
             w=HIP_W, l=HIP_D, h=HIP_H,
             material=pants, collection=coll)

    # Torso (rotated)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(IN * seat_cx_in, IN * seat_cy_in,
                  IN * (z_torso_bottom + TORSO_H/2)),
    )
    torso = bpy.context.active_object
    torso.scale = (IN * TORSO_W, IN * TORSO_D, IN * TORSO_H)
    torso.rotation_euler = (0, 0, facing_yaw_rad - _math_v15h.pi/2)
    torso.name = f"P_{name}_torso"
    if torso.data.materials:
        torso.data.materials[0] = shirt
    else:
        torso.data.materials.append(shirt)
    move_to_collection(torso, coll)

    # Neck + Head
    _add_cylinder(f"P_{name}_neck", seat_cx_in, seat_cy_in, z_neck_bottom,
                  NECK_R, NECK_H, skin, coll, verts=10)
    _add_sphere(f"P_{name}_head", seat_cx_in, seat_cy_in, z_head_center,
                HEAD_R, skin, coll, segs=14)
    hair_x, hair_y = offset(seat_cx_in, seat_cy_in, -0.6, 0)
    _add_sphere(f"P_{name}_hair", hair_x, hair_y, z_head_center + 1.2,
                HEAD_R * 0.9, hair, coll, segs=14)

    # Thighs: from hip-front to knee (forward & at seat level)
    for side, sign in [("L", -1), ("R", +1)]:
        # Hip attach point at seat height, at hip-front edge
        hip_x, hip_y = offset(seat_cx_in, seat_cy_in, HIP_D/2 - 1, sign * 3)
        knee_x, knee_y = offset(hip_x, hip_y, THIGH_LEN, 0)
        _add_oriented_cylinder(f"P_{name}_thigh_{side}",
            hip_x, hip_y, z_hip_bottom + 1,
            knee_x, knee_y, z_hip_bottom + 1,
            LEG_R, pants, coll, verts=10)
        # Shin: knee down to ankle (vertical)
        ankle_z = 3.0
        _add_oriented_cylinder(f"P_{name}_shin_{side}",
            knee_x, knee_y, z_hip_bottom + 1,
            knee_x, knee_y, ankle_z,
            LEG_R * 0.95, pants, coll, verts=10)
        # Foot / shoe
        foot_x, foot_y = offset(knee_x, knee_y, 2, 0)
        _add_cylinder(f"P_{name}_foot_{side}", foot_x, foot_y, 0,
                      1.9, ankle_z, shoe, coll, verts=8)

    # Arms: hang slightly forward, hands resting near thigh/table
    r_sh_x, r_sh_y = offset(seat_cx_in, seat_cy_in, 0, +TORSO_W/2)
    l_sh_x, l_sh_y = offset(seat_cx_in, seat_cy_in, 0, -TORSO_W/2)
    for side, sh_x, sh_y, sgn in [("L", l_sh_x, l_sh_y, -1),
                                   ("R", r_sh_x, r_sh_y, +1)]:
        elbow_x, elbow_y = offset(sh_x, sh_y, 3, sgn * 0.5)
        elbow_z = z_shoulder - ARM_UP_LEN
        hand_x, hand_y = offset(elbow_x, elbow_y, 6, 0)
        hand_z = z_hip_top + 3
        _add_oriented_cylinder(f"P_{name}_arm_{side}_up",
            sh_x, sh_y, z_shoulder, elbow_x, elbow_y, elbow_z,
            ARM_R, shirt, coll, verts=8)
        _add_oriented_cylinder(f"P_{name}_arm_{side}_lo",
            elbow_x, elbow_y, elbow_z, hand_x, hand_y, hand_z,
            ARM_R * 0.85, skin, coll, verts=8)
        _add_sphere(f"P_{name}_hand_{side}", hand_x, hand_y, hand_z,
                    ARM_R * 1.1, skin, coll, segs=10)


def build_humans():
    """Place one standing pool player per pool table and one seated patron
    per two-top. Not every table gets a player -- to keep the scene lively
    without crowding, put players at only 3 of the 6 tables. Every two-top
    gets one seated patron in the outer chair.
    """
    coll = get_or_create_collection("Humans")

    # Players stand on the "wall" side of each table -- i.e. between the table
    # and the wall two-top -- facing the table (inward).
    #   L-side tables (xL_center): player on the west side of the table,
    #     x = table_west_edge - PLAYER_OFFSET, facing EAST (+X)
    #   R-side tables (xR_center): player on the east side of the table,
    #     x = table_east_edge + PLAYER_OFFSET, facing WEST (-X)
    #
    # Pick 3 tables to occupy: BackL, MainAR, MainBL (spread across the room).
    OCCUPIED = {"BackL", "MainAR", "MainBL"}
    PLAYER_OFFSET = 5   # inches from the rail
    seed = 0
    for (label, cx, ty) in POOL_TABLES:
        if label not in OCCUPIED:
            continue
        wall = 'L' if cx == xL_center else 'R'
        table_cy = ty + TBL_L / 2
        if wall == 'L':
            player_x = cx - TBL_W/2 - PLAYER_OFFSET - 4
            facing = 0.0  # facing east (+X)
        else:
            player_x = cx + TBL_W/2 + PLAYER_OFFSET + 4
            facing = _math_v15h.pi  # facing west (-X)
        # Offset the player along Y so they align with the cue tip location
        # (existing cues run along the table center-Y, tip near west/east
        # rail). Placing player at table_cy - 4" puts them slightly offset
        # from cue center for a natural shooting stance.
        player_y = table_cy - 6
        build_pool_player(f"player_{label}", player_x, player_y, facing,
                          seed, coll)
        seed += 1

    # Seated patrons -- one per two-top, in the OUTER chair (chair_N, which sits
    # at y0..y0+CHAIR_D). This chair is the "top-of-image" chair (image-top =
    # SOUTH is high Y, so chair_N at LOW y is the NORTH-facing chair).
    # v15j: two-tops are now bar-height; patron seat cushion at TWOTOP_SEAT_H=30".
    KITCHEN_Y0 = 290
    TWOTOP_STACK_LEN = CHAIR_D + 18 + CHAIR_D  # 42
    BACKR_RELOCATE_Y0 = KITCHEN_Y0 - 6 - TWOTOP_STACK_LEN  # 242
    seat_z = TWOTOP_SEAT_H  # v15j: bar-stool seat top (was SEAT_H=17)

    for (label, cx, ty) in POOL_TABLES:
        wall = 'L' if cx == xL_center else 'R'
        table_cy = ty + TBL_L / 2
        y0 = table_cy - TWOTOP_L / 2 - 14
        if wall == 'R' and label == 'BackR':
            y0 = BACKR_RELOCATE_Y0
            label_used = 'BackR_relocated'
        else:
            label_used = label
        # chair_N center: chair sits at (chairs_x .. chairs_x+CHAIR_W) x (y0 .. y0+CHAIR_D)
        # We set chairs_x = tx + 2 where tx = 0 for L or ROOM_W - TWOTOP_W for R
        if wall == 'L':
            chairs_x0 = 0 + 2
        else:
            chairs_x0 = ROOM_W - TWOTOP_W + 2
        seat_cx = chairs_x0 + CHAIR_W / 2
        seat_cy_N = y0 + CHAIR_D / 2
        # facing toward the table (higher Y direction, since chair_N is at low Y)
        facing = _math_v15h.pi / 2  # +Y (south, toward image-top / table)
        build_seated_patron(f"patron_{wall}_{label_used}",
                            seat_cx, seat_cy_N, facing,
                            seat_z, seed, coll)
        seed += 1

build_humans()
# ===== v15h humans end =====

print("=" * 60)
print("v3 furniture + lighting added.")
print(f"  Pool tables:        {len(POOL_TABLES)}   (2 back room + 4 main room)")
print(f"  Table spacing:      {TBL_SPACING}\" between tables, centered short-way")
print(f"  Classroom tables:   {(N_ROWS-1) * N_PER_ROW}   (chairs: {(N_ROWS-1)*N_PER_ROW*CHAIRS_PER_TABLE})  [v15L: back row replaced by round tables]")
print(f"  Round tables:       2   (48\" dia, 4 chairs each; between stage and Storage A)")
print(f"  Two-tops:           {len(POOL_TABLES)}")
print(f"  Bench seating:      3 black-vinyl booth sections, north wall (v15L)")
print(f"  Lockers/shelving:   4 units, back wall")
print(f"  HVAC chase:         1 volume, left wall")
print(f"  Partition stow:     1 column at beam, right wall")
print(f"  Entry railings:     2 short rails flanking steps")
print(f"  Pool-table pendants:{len(POOL_TABLES)} (mesh shade + bulb + AREA light)")
print(f"  Ceiling troffers:   {troffer_count} (mesh fixture + lens + AREA light)")
print()
print("Pool table layout (long axis along +Y, centered short-way):")
for (name, cx, ty) in POOL_TABLES:
    print(f"  {name:7s}  center X={cx:6.1f}\"  top Y={ty:6.1f}\"  "
          f"(end Y={ty+TBL_L:6.1f}\")")
print("=" * 60)
