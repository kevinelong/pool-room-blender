"""
Blender 4.x build script for the pool/billiards room shell.

USAGE
  1. Copy this file and all *.png textures (cmu_wall_*, wood_panel_*,
     white_plank_*, ceiling_tile_*, vct_floor_*, wood_beam_*, felt_*) to a
     single folder on your machine.
  2. Edit TEXTURE_DIR below if needed.
  3. Open Blender 4.x, Scripting workspace, open this file, click Run Script.

WHAT IT BUILDS (NOT placed):
  - Floor (316" x 682") with VCT material
  - Four perimeter walls (108" tall) -- mixed CMU + paneling + plank
  - Door openings cut in the walls (boolean-style by skipping geometry)
  - Entry alcove with landing + 2 steps (no railings -- can add manually)
  - Rough-sawn wood beam across room at y=BEAM_Y, dropping to 96"
  - Drop-ceiling at 108" with acoustic tile material
  - (No pool tables, chairs, posters, signage -- pool felt material is created
    for you to apply to your own pool-table mesh.)

UNITS
  Display = Imperial. Internal scene unit = meters (Blender default).
  1 inch = 0.0254 m.

After running, you should see the geometry. Drop in your own pool tables,
chairs, lighting, etc., on top of this shell.
"""
import bpy
import os
import math
from mathutils import Vector

# ============================================================================
# CONFIG
# ============================================================================
TEXTURE_DIR = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else "/tmp"
# If your .blend isn't saved yet, set TEXTURE_DIR manually:
# TEXTURE_DIR = "/path/to/your/textures"

IN = 0.0254  # inches to meters

# Floor plan dimensions (inches)
ROOM_W = 316         # X width  (left wall to right wall)
ROOM_L = 682         # Y length (back wall to front wall)
CEIL_H = 108         # ceiling height, inches
BEAM_DROP = 12       # beam hangs 12" below ceiling -> beam bottom at 96"
BEAM_Y = 332         # y-position of beam (from back wall y=0)
BEAM_W = 12          # beam depth (along Y)
BEAM_THK = 12        # beam thickness (along Z, drops below ceiling)

WALL_THK = 6         # wall thickness, inches

# Door openings: (wall, y_or_x_start, span, height) -- "wall" is which face
# wall codes: 'L'=left (x=0), 'R'=right (x=ROOM_W), 'F'=front (y=ROOM_L), 'B'=back (y=0)
DOOR_H = 80
# v15: door layout corrected per user photos.
#   - Main Entry: RIGHT (east) wall, south end (railed stair landing). Unchanged.
#   - Kitchen:    RIGHT (east) wall, north of HVAC chase. Unchanged.
#   - Emergency Exit: FRONT (south) wall, right side. Unchanged.
#   - Storage:    TWO doors at the NE corner -- one on the BACK (north) wall
#                 at the east end, one on the RIGHT (east) wall at the north
#                 end. Old west-wall "Staff/Storage" door is REMOVED.
DOORS = [
    # Main entry, RIGHT wall, top-right corner (matches railed stair landing)
    ('R', ROOM_L - 70, 70, DOOR_H, "Main Entry (36\")"),
    # Kitchen, RIGHT wall, north of HVAC chase.
    ('R', 290, 40, DOOR_H, "Kitchen (32\")"),
    # Emergency exit, FRONT (south) wall, right side.
    # v18: moved to the WEST end of the south wall per the reference video
    # (was ROOM_W-95 = east half — supersedes the v15c position).
    ('F', 30, 65, DOOR_H, "Emergency Exit (36\")"),
    # Storage door 1: BACK (north) wall, east end. 36" door, 4" gap to NE corner.
    ('B', ROOM_W - 40, 36, DOOR_H, "Storage A (36\")"),
    # Storage door 2: RIGHT (east) wall, north end. 36" door, 4" gap to NE corner.
    ('R', 4, 36, DOOR_H, "Storage B (36\")"),
]

# Stair landing & 2 steps inside main entry
STAIR_RISE = 7.5    # inches per riser
STAIR_TREAD = 11    # tread depth (X projection into room)
LANDING_DEPTH = 18  # outside-grade landing depth at door (lower elevation)
STAIR_WIDTH = 70    # matches main door width

# ============================================================================
# HELPERS
# ============================================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # also nuke leftover meshes / materials so re-runs stay clean
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.images:
        bpy.data.images.remove(block)


def setup_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = 'IMPERIAL'
    scene.unit_settings.length_unit = 'FEET'
    # World background a neutral grey
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.18, 0.18, 0.18, 1)
        bg.inputs[1].default_value = 1.0


def in2m(v):
    return v * IN


def make_box(name, x, y, z, w, l, h, material=None, parent_collection=None):
    """Create an axis-aligned box (mesh) at (x,y,z) corner with size (w,l,h) in inches."""
    bpy.ops.mesh.primitive_cube_add(size=1.0,
                                    location=(in2m(x + w / 2),
                                              in2m(y + l / 2),
                                              in2m(z + h / 2)))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (in2m(w), in2m(l), in2m(h))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj


def load_image(filename):
    path = os.path.join(TEXTURE_DIR, filename)
    if not os.path.isfile(path):
        print(f"  WARNING: missing texture {path}")
        return None
    return bpy.data.images.load(path, check_existing=True)


def make_pbr_material(name, albedo_file, normal_file, roughness_file,
                      tile_size_m, project_axis='Z', flat_color=None):
    """
    Build a node-based PBR material.

    tile_size_m: physical size in meters of one repeat of the texture.
    project_axis: 'Z' for floor/ceiling (use UV-style flat XY mapping),
                  'X' for left/right walls (texture varies in Y,Z),
                  'Y' for front/back walls (texture varies in X,Z).
    flat_color: if given, builds a solid-color material instead (RGBA).
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (800, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    if flat_color is not None:
        bsdf.inputs['Base Color'].default_value = flat_color
        bsdf.inputs['Roughness'].default_value = 0.7
        return mat

    # Texture coordinate -> mapping (object space, scale = 1/tile_size_m)
    coord = nt.nodes.new('ShaderNodeTexCoord')
    coord.location = (-700, 0)
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.location = (-500, 0)
    s = 1.0 / tile_size_m
    mapping.inputs['Scale'].default_value = (s, s, s)
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])

    # Albedo
    tex_a = nt.nodes.new('ShaderNodeTexImage')
    tex_a.location = (-200, 200)
    img_a = load_image(albedo_file)
    if img_a:
        tex_a.image = img_a
    nt.links.new(mapping.outputs['Vector'], tex_a.inputs['Vector'])
    nt.links.new(tex_a.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness
    tex_r = nt.nodes.new('ShaderNodeTexImage')
    tex_r.location = (-200, -100)
    img_r = load_image(roughness_file)
    if img_r:
        tex_r.image = img_r
        try:
            tex_r.image.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass
    nt.links.new(mapping.outputs['Vector'], tex_r.inputs['Vector'])
    nt.links.new(tex_r.outputs['Color'], bsdf.inputs['Roughness'])

    # Normal
    tex_n = nt.nodes.new('ShaderNodeTexImage')
    tex_n.location = (-200, -400)
    img_n = load_image(normal_file)
    if img_n:
        tex_n.image = img_n
        try:
            tex_n.image.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass
    nt.links.new(mapping.outputs['Vector'], tex_n.inputs['Vector'])

    norm = nt.nodes.new('ShaderNodeNormalMap')
    norm.location = (200, -400)
    norm.inputs['Strength'].default_value = 1.0
    nt.links.new(tex_n.outputs['Color'], norm.inputs['Color'])
    nt.links.new(norm.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


# ============================================================================
# BUILD
# ============================================================================

clear_scene()
setup_scene()

# ---- materials ------------------------------------------------------------
# Tile size 64" CMU = 1.6256 m
mat_cmu = make_pbr_material("CMU_White",
                            "cmu_wall_albedo.png",
                            "cmu_wall_normal.png",
                            "cmu_wall_roughness.png",
                            tile_size_m=1.6256)
# Wood panel 48" = 1.2192 m
mat_panel = make_pbr_material("Wood_Panel_Dark",
                              "wood_panel_albedo.png",
                              "wood_panel_normal.png",
                              "wood_panel_roughness.png",
                              tile_size_m=1.2192)
# White plank 48" = 1.2192 m
mat_plank = make_pbr_material("White_Plank",
                              "white_plank_albedo.png",
                              "white_plank_normal.png",
                              "white_plank_roughness.png",
                              tile_size_m=1.2192)
# Ceiling 48" = 1.2192 m
mat_ceil = make_pbr_material("Acoustic_Ceiling",
                             "ceiling_tile_albedo.png",
                             "ceiling_tile_normal.png",
                             "ceiling_tile_roughness.png",
                             tile_size_m=1.2192)
# VCT 48" = 1.2192 m
mat_vct = make_pbr_material("VCT_Floor",
                            "vct_floor_albedo.png",
                            "vct_floor_normal.png",
                            "vct_floor_roughness.png",
                            tile_size_m=1.2192)
# Beam 96" = 2.4384 m
mat_beam = make_pbr_material("Wood_Beam",
                             "wood_beam_albedo.png",
                             "wood_beam_normal.png",
                             "wood_beam_roughness.png",
                             tile_size_m=2.4384)
# Felt 24" = 0.6096 m  (kept here for the user to apply to pool tables)
mat_felt = make_pbr_material("Pool_Felt",
                             "felt_albedo.png",
                             "felt_normal.png",
                             "felt_roughness.png",
                             tile_size_m=0.6096)

# Solid colors for landing & steps (concrete)
mat_concrete = make_pbr_material("Concrete_Step", None, None, None,
                                 tile_size_m=1.0,
                                 flat_color=(0.55, 0.54, 0.52, 1.0))

# ---- floor ----------------------------------------------------------------
# v17: the slab stops at the Main Entry well so the sunken landing and the
# two treads (build_entry_alcove) are visible — previously the full-room
# slab buried them (and z-fought with the top tread in top-down renders).
ENTRY_WELL_X0 = ROOM_W - LANDING_DEPTH - 2 * STAIR_TREAD   # 276
ENTRY_WELL_Y0 = ROOM_L - 70                                 # 612
make_box("Floor",
         x=0, y=0, z=-1,
         w=ROOM_W, l=ENTRY_WELL_Y0, h=1,
         material=mat_vct)
make_box("Floor_S_strip",
         x=0, y=ENTRY_WELL_Y0, z=-1,
         w=ENTRY_WELL_X0, l=ROOM_L - ENTRY_WELL_Y0, h=1,
         material=mat_vct)

# ---- ceiling --------------------------------------------------------------
make_box("Ceiling",
         x=0, y=0, z=CEIL_H,
         w=ROOM_W, l=ROOM_L, h=1,
         material=mat_ceil)

# ---- WALLS: build each as a series of segments around door openings -------
# Helper: build a wall along one face, with door cutouts.
# `face` axis: 'L'/'R' is a wall parallel to Y (varies in Y);
#               'F'/'B' is a wall parallel to X (varies in X).
# We split the wall into rectangles around each door opening.

def build_wall_segment(name, x, y, z, w, l, h, material):
    """Wall slab from (x,y,z) corner with size (w,l,h) inches."""
    make_box(name, x, y, z, w, l, h, material=material)


def build_left_wall():
    """Left wall x=0, spans full Y. Mixed materials by segment."""
    # Collect door openings on this wall (sorted by y)
    openings = sorted([(start, span) for (wall, start, span, hh, lbl)
                       in DOORS if wall == 'L'])
    # Material zones along Y (per user spec: mixed)
    # Y: 0          --> BEAM_Y    : white CMU (back/HVAC side -> use white plank instead)
    #    BEAM_Y    --> ROOM_L    : white CMU
    # But user said back HVAC area = white plank. Back of room is small-y, so:
    #    0..120     -> white plank (HVAC back)
    #    120..ROOM_L -> CMU
    def material_at(y_inches):
        if y_inches < 120:
            return mat_plank
        return mat_cmu

    # Walk Y from 0 to ROOM_L, emitting solid slabs and skipping door spans
    y_cursor = 0
    cuts = []
    for (start, span) in openings:
        if y_cursor < start:
            cuts.append((y_cursor, start - y_cursor))
        y_cursor = start + span
    if y_cursor < ROOM_L:
        cuts.append((y_cursor, ROOM_L - y_cursor))

    # full-height segment between doors (one box) -- but split by material zone
    for i, (y0, span) in enumerate(cuts):
        # split this segment at y=120 if it crosses
        breakpoints = [y0]
        if y0 < 120 < y0 + span:
            breakpoints.append(120)
        breakpoints.append(y0 + span)
        for j in range(len(breakpoints) - 1):
            ya, yb = breakpoints[j], breakpoints[j+1]
            mat = material_at((ya + yb) / 2)
            build_wall_segment(f"Wall_L_seg_{i}_{j}",
                               x=-WALL_THK, y=ya, z=0,
                               w=WALL_THK, l=yb - ya, h=CEIL_H,
                               material=mat)

    # Header above each door opening
    for (start, span) in openings:
        build_wall_segment(f"Wall_L_header_{start}",
                           x=-WALL_THK, y=start, z=DOOR_H,
                           w=WALL_THK, l=span, h=CEIL_H - DOOR_H,
                           material=mat_cmu)


def build_right_wall():
    """Right wall x=ROOM_W. v11: now has Main Entry + Kitchen door cutouts."""
    openings = sorted([(start, span) for (wall, start, span, hh, lbl)
                       in DOORS if wall == 'R'])
    y_cursor = 0
    cuts = []
    for (start, span) in openings:
        if y_cursor < start:
            cuts.append((y_cursor, start - y_cursor))
        y_cursor = start + span
    if y_cursor < ROOM_L:
        cuts.append((y_cursor, ROOM_L - y_cursor))

    for i, (y0, span) in enumerate(cuts):
        build_wall_segment(f"Wall_R_seg_{i}",
                           x=ROOM_W, y=y0, z=0,
                           w=WALL_THK, l=span, h=CEIL_H,
                           material=mat_cmu)
    # Header above each door opening
    for (start, span) in openings:
        build_wall_segment(f"Wall_R_header_{start}",
                           x=ROOM_W, y=start, z=DOOR_H,
                           w=WALL_THK, l=span, h=CEIL_H - DOOR_H,
                           material=mat_cmu)


def build_front_wall():
    """Front wall y=ROOM_L (long bottom edge). One door (emergency exit)."""
    openings = sorted([(start, span) for (wall, start, span, hh, lbl)
                       in DOORS if wall == 'F'])
    x_cursor = 0
    cuts = []
    for (start, span) in openings:
        if x_cursor < start:
            cuts.append((x_cursor, start - x_cursor))
        x_cursor = start + span
    if x_cursor < ROOM_W:
        cuts.append((x_cursor, ROOM_W - x_cursor))

    for i, (x0, span) in enumerate(cuts):
        build_wall_segment(f"Wall_F_seg_{i}",
                           x=x0, y=ROOM_L, z=0,
                           w=span, l=WALL_THK, h=CEIL_H,
                           material=mat_cmu)
    # Headers
    for (start, span) in openings:
        build_wall_segment(f"Wall_F_header_{start}",
                           x=start, y=ROOM_L, z=DOOR_H,
                           w=span, l=WALL_THK, h=CEIL_H - DOOR_H,
                           material=mat_cmu)


def build_back_wall():
    """Back wall y=0. v15: now has Storage A door cutout at east end.
    White-painted plank siding (HVAC area)."""
    openings = sorted([(start, span) for (wall, start, span, hh, lbl)
                       in DOORS if wall == 'B'])
    x_cursor = 0
    cuts = []
    for (start, span) in openings:
        if x_cursor < start:
            cuts.append((x_cursor, start - x_cursor))
        x_cursor = start + span
    if x_cursor < ROOM_W:
        cuts.append((x_cursor, ROOM_W - x_cursor))

    for i, (x0, span) in enumerate(cuts):
        build_wall_segment(f"Wall_B_seg_{i}",
                           x=x0, y=-WALL_THK, z=0,
                           w=span, l=WALL_THK, h=CEIL_H,
                           material=mat_plank)
    # Headers above each door opening
    for (start, span) in openings:
        build_wall_segment(f"Wall_B_header_{start}",
                           x=start, y=-WALL_THK, z=DOOR_H,
                           w=span, l=WALL_THK, h=CEIL_H - DOOR_H,
                           material=mat_plank)


def build_entry_alcove():
    """v17: sunken Main Entry well, matching the reference video.
    From the room floor two treads step DOWN to a landing at the door,
    flanked by two wrought-iron rails, with a wood door leaf standing
    open against the wall beside the opening. The floor slab stops at
    the well edge (see Floor / Floor_S_strip) so all of it is visible.
    Treads are solid to the well bottom — no floating 1\" slabs."""
    door_y0 = ROOM_L - 70
    door_y_span = 70
    landing_z = -2 * STAIR_RISE  # -15"
    x_step2 = ROOM_W - LANDING_DEPTH - 2 * STAIR_TREAD   # 276
    x_step1 = ROOM_W - LANDING_DEPTH - STAIR_TREAD       # 287
    x_landing = ROOM_W - LANDING_DEPTH                   # 298
    # Landing at east wall (door side), the well bottom
    build_wall_segment("Entry_Landing",
                       x=x_landing, y=door_y0, z=landing_z,
                       w=LANDING_DEPTH, l=door_y_span,
                       h=1, material=mat_concrete)
    # step 1: solid riser+tread, top at -STAIR_RISE
    build_wall_segment("Entry_Step1",
                       x=x_step1, y=door_y0, z=landing_z,
                       w=STAIR_TREAD, l=door_y_span,
                       h=STAIR_RISE, material=mat_concrete)   # top -7.5
    # step 2: solid, top flush with the room floor
    build_wall_segment("Entry_Step2",
                       x=x_step2, y=door_y0, z=landing_z,
                       w=STAIR_TREAD, l=door_y_span,
                       h=2 * STAIR_RISE, material=mat_concrete)  # top 0
    # well cheeks: low curb on the room side, foundation under the S wall
    build_wall_segment("Entry_Well_Curb_N",
                       x=x_step2, y=door_y0 - 2, z=landing_z,
                       w=ROOM_W - x_step2, l=2,
                       h=2 * STAIR_RISE + 3, material=mat_concrete)
    build_wall_segment("Entry_Well_Fnd_S",
                       x=x_step2, y=ROOM_L, z=landing_z,
                       w=ROOM_W - x_step2, l=WALL_THK,
                       h=2 * STAIR_RISE, material=mat_concrete)
    # exterior stoop seen through the open doorway
    build_wall_segment("Entry_Stoop",
                       x=ROOM_W, y=door_y0, z=landing_z,
                       w=24, l=door_y_span,
                       h=1, material=mat_concrete)
    # two wrought-iron rails flanking the stair run (v17: moved here from
    # the removed west entry). Open ironwork: a level top bar on posts
    # whose bases follow the stair profile — not solid panels.
    mat_iron = make_pbr_material("Wrought_Iron_Entry", None, None, None,
                                 tile_size_m=1.0,
                                 flat_color=(0.05, 0.05, 0.06, 1.0))
    RAIL_T = 1.5
    RAIL_TOP = 36

    def _tread_top(x):
        if x >= x_landing:
            return landing_z + 1        # -14 (landing surface)
        if x >= x_step1:
            return -STAIR_RISE          # -7.5
        return 0.0                      # step2 top / floor level

    for side, ry in (("N", door_y0 + 3), ("S", ROOM_L - 3 - RAIL_T)):
        build_wall_segment(f"Entry_Rail_{side}_bar",
                           x=x_step2, y=ry, z=RAIL_TOP - 2,
                           w=ROOM_W - x_step2, l=RAIL_T,
                           h=2, material=mat_iron)
        for px_ in (x_step2 + 1, x_step1 + 2, x_landing + 2, ROOM_W - 3):
            base = _tread_top(px_)
            build_wall_segment(f"Entry_Rail_{side}_post_{px_:.0f}",
                               x=px_, y=ry, z=base,
                               w=RAIL_T, l=RAIL_T,
                               h=RAIL_TOP - 2 - base, material=mat_iron)

    # daylight beyond the open doorway: a light-grey exterior backdrop and
    # a warm area light over the stoop, so the doorway reads as an exit
    # instead of a black void
    mat_ext = make_pbr_material("Entry_Exterior_Backdrop", None, None, None,
                                tile_size_m=1.0,
                                flat_color=(0.38, 0.38, 0.36, 1.0))
    build_wall_segment("Entry_Backdrop",
                       x=ROOM_W + 40, y=door_y0 - 20, z=landing_z,
                       w=2, l=door_y_span + 40,
                       h=CEIL_H, material=mat_ext)
    ld = bpy.data.lights.new("Entry_Daylight", type='AREA')
    ld.energy = 160.0
    ld.size = 1.6
    ld.color = (1.0, 0.96, 0.88)
    lo = bpy.data.objects.new("Entry_Daylight", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = (in2m(ROOM_W + 20), in2m(door_y0 + 35), in2m(70))
    lo.rotation_euler = (0.0, math.radians(-115.0), 0.0)
    # v26: the wood door leaf hinges on the SOUTH jamb and opens to the
    # LEFT (as you enter) — it swings exactly 90 degrees and stops flat
    # against the south (top) wall face beside the opening
    mat_wood_door = make_pbr_material("Wood_Door_Entry", None, None, None,
                                      tile_size_m=1.0,
                                      flat_color=(0.42, 0.26, 0.13, 1.0))
    build_wall_segment("Entry_Door_Leaf_Open",
                       x=ROOM_W - 36 - 1, y=ROOM_L - 2.5, z=0,
                       w=36, l=1.75,
                       h=80, material=mat_wood_door)


def build_beam():
    """Rough-sawn wood beam across room at y=BEAM_Y, dropping below ceiling."""
    z0 = CEIL_H - BEAM_THK  # beam top at ceiling level, bottom 12" below
    make_box("Wood_Beam",
             x=0, y=BEAM_Y - BEAM_W / 2, z=z0,
             w=ROOM_W, l=BEAM_W, h=BEAM_THK,
             material=mat_beam)


# ---- build everything -----------------------------------------------------
build_left_wall()
build_right_wall()
build_front_wall()
build_back_wall()
build_beam()
build_entry_alcove()

# v13: physical door slabs, 1" proud of wall face, painted matte black for
# contrast against the room walls. These visually close each door opening so
# the top-down render reads a clear door instead of a wall-cut void.
DOOR_SLAB_T = 1.5     # slab thickness (proud of wall)
DOOR_SLAB_PROUD = 1   # how far slab protrudes past wall face (inches)

def _door_slab_mat():
    name = "MAT_door_black"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.03, 0.03, 0.03, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.55
    return m

def build_door_slabs():
    mat = _door_slab_mat()
    for wall, start, span, height, name in DOORS:
        if name.startswith("Main Entry"):
            # v17: the Main Entry is an open doorway with a wood leaf
            # standing open beside it (build_entry_alcove) — no black slab.
            continue
        if wall == 'R':
            # right wall, slab projects INTO room from x=ROOM_W inward
            make_box(f"DoorSlab_{name}",
                     x=ROOM_W - DOOR_SLAB_PROUD, y=start, z=0,
                     w=DOOR_SLAB_T, l=span, h=height,
                     material=mat)
        elif wall == 'L':
            make_box(f"DoorSlab_{name}",
                     x=-DOOR_SLAB_T + DOOR_SLAB_PROUD, y=start, z=0,
                     w=DOOR_SLAB_T, l=span, h=height,
                     material=mat)
        elif wall == 'F':
            make_box(f"DoorSlab_{name}",
                     x=start, y=ROOM_L - DOOR_SLAB_PROUD, z=0,
                     w=span, l=DOOR_SLAB_T, h=height,
                     material=mat)
        elif wall == 'B':
            make_box(f"DoorSlab_{name}",
                     x=start, y=-DOOR_SLAB_T + DOOR_SLAB_PROUD, z=0,
                     w=span, l=DOOR_SLAB_T, h=height,
                     material=mat)

build_door_slabs()

# ---- camera & lights for quick preview ------------------------------------
bpy.ops.object.camera_add(location=(in2m(ROOM_W / 2),
                                    in2m(ROOM_L + 200),
                                    in2m(CEIL_H * 1.5)),
                          rotation=(math.radians(65), 0, 0))
cam = bpy.context.active_object
cam.name = "PreviewCam"
bpy.context.scene.camera = cam

# Sun light
bpy.ops.object.light_add(type='SUN', location=(in2m(ROOM_W/2),
                                               in2m(ROOM_L/2),
                                               in2m(CEIL_H*2)))
bpy.context.active_object.data.energy = 2.0
bpy.context.active_object.data.angle = math.radians(20)
# Point light inside room
bpy.ops.object.light_add(type='POINT', location=(in2m(ROOM_W/2),
                                                  in2m(ROOM_L/2),
                                                  in2m(CEIL_H - 18)))
bpy.context.active_object.data.energy = 800

# Frame all geometry in viewport
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.view3d.camera_to_view_selected() if hasattr(bpy.ops.view3d, 'camera_to_view_selected') else None

print("=" * 60)
print("Pool room shell built.")
print(f"  Floor: {ROOM_W}\" x {ROOM_L}\" (= {ROOM_W/12:.1f}' x {ROOM_L/12:.1f}')")
print(f"  Ceiling: {CEIL_H}\" ({CEIL_H/12:.1f}')")
print(f"  Beam at y={BEAM_Y}\", drops to z={CEIL_H - BEAM_THK}\"")
print(f"  Doors: {len(DOORS)} openings")
print(f"  Textures loaded from: {TEXTURE_DIR}")
print("Drop your pool tables, chairs, posters, lights on top.")
print("=" * 60)
