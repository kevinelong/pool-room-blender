"""v16 variant renderer — builds a v16 configuration and renders two views:
a top-down ortho (1600x3200) and the 5.5 ft eye-height Main Entry
perspective (2560x1440), in one Blender session.

Select the variant with the V16_CONFIG env var (lounge | split | bistro |
league | tournament) and the view with V16_VIEW (topdown | persp | both,
default both) — one view per invocation keeps each run short enough for
supervised execution. Requires v16_configs.py staged alongside the build
modules (render.sh does this).

How it works: the furniture module keys everything on its module-level
POOL_TABLES list — tables, cues, pendant fixtures, wall two-tops, players.
We rewrite that list in the source text before exec'ing it, so the whole
ecosystem follows the variant's table layout. Config-specific extras
(48\" rounds, drink rails) are added afterwards via the module's own
builder functions.
"""
import bpy, os, re, time
from mathutils import Vector

HERE = "/tmp/blender_test"
KEY = os.environ.get("V16_CONFIG", "split")
VIEW = os.environ.get("V16_VIEW", "both")

import sys
sys.path.insert(0, HERE)
import v16_configs as V16

cfg = next(c for c in V16.CONFIGS if c["key"] == KEY)
print(f"[v16:{KEY}] building variant: {cfg['name']}")

# ---- relabel tables so the furniture module's row conventions hold -------
ROT90 = cfg.get("rot90", False)
TBL_W_, TBL_L_ = 53.5, 92.5
if ROT90:
    # v20 line layouts: build each table unrotated with the same CENTER the
    # rotated table will have (config y_top is the rotated cabinet's north
    # edge), then rotate the whole table group 90° about that center below.
    tables = [(n, cx, yt + TBL_W_ / 2 - TBL_L_ / 2)
              for n, cx, yt in cfg["tables"]]
else:
    ROW_NAMES = ["Back", "MainA", "MainB", "MainC"]
    tables = []
    row = -1
    last_y = None
    for _n, cx, yt in cfg["tables"]:
        if yt != last_y:
            row += 1
            last_y = yt
        suffix = "L" if cx < 130 else ("R" if cx > 185 else "C")
        tables.append((f"{ROW_NAMES[row]}{suffix}", cx, yt))
tables_src = "POOL_TABLES = [\n" + "".join(
    f"    ({n!r}, {cx!r}, {yt!r}),\n" for n, cx, yt in tables) + "]"

bpy.ops.wm.read_factory_settings(use_empty=True)
G = {"__name__": "__main__"}
with open(os.path.join(HERE, "build_pool_room.py")) as fh:
    exec(compile(fh.read(), "build_pool_room.py", "exec"), G)

src = open(os.path.join(HERE, "build_pool_room_furniture.py")).read()
src, n = re.subn(r"POOL_TABLES = \[[^\]]*\]", tables_src, src, count=1)
assert n == 1, "POOL_TABLES patch failed"
# v23: stage and storage lockers are removed from every layout
DISABLE = ["build_stage", "build_lockers"]
if not cfg.get("classroom"):
    DISABLE.append("build_classroom")
if KEY != "social":          # the v15L north rounds are part of the current
    DISABLE.append("build_round_tables")   # build only
if not cfg.get("bench"):
    DISABLE.append("build_bench")
if ROT90:
    # wall two-tops are keyed to the column layout; a rotated line puts
    # them inside the tables' east swing — drop them (patrons pruned below)
    DISABLE.append("build_two_tops")
for call in DISABLE:
    src, n = re.subn(rf"^{call}\(\)", f"# v16:{KEY} disabled: {call}()",
                     src, count=1, flags=re.M)
    assert n == 1, f"disable patch failed: {call}"
G2 = {"__name__": "__main__"}
exec(compile(src, "build_pool_room_furniture.py", "exec"), G2)

if ROT90:
    # prune seated patrons (their wall two-tops were disabled)
    for o in [o for o in bpy.data.objects if o.name.startswith("P_patron_")]:
        bpy.data.objects.remove(o, do_unlink=True)
    # rotate each table's object group 90° about its cabinet center
    from mathutils import Matrix
    IN_ = 0.0254
    for name, cx, yt in cfg["tables"]:
        pivot = Vector((cx * IN_, (yt + TBL_W_ / 2) * IN_, 0.0))
        R = (Matrix.Translation(pivot)
             @ Matrix.Rotation(3.14159265 / 2, 4, 'Z')
             @ Matrix.Translation(-pivot))
        for o in bpy.data.objects:
            if (f"_{name}_" in o.name or o.name.endswith(f"_{name}")
                    or o.name.endswith(name)):
                o.matrix_world = R @ o.matrix_world
    print(f"[v16:{KEY}] rotated {len(cfg['tables'])} tables 90°")

STAGE_DEFAULT = (0, 0, 96, 48)
stage_rect = cfg.get("stage_rect")
if stage_rect and tuple(stage_rect) != STAGE_DEFAULT:
    # v21: relocate the stage — rotate 90° about origin ((x,y)->(-y,x))
    # then translate so the footprint lands on stage_rect.
    from mathutils import Matrix
    IN_ = 0.0254
    sx0, sy0, sx1, sy1 = stage_rect
    R = (Matrix.Translation(Vector((sx1 * IN_, sy0 * IN_, 0)))
         @ Matrix.Rotation(3.14159265 / 2, 4, 'Z'))
    coll = bpy.data.collections.get("Stage")
    moved = 0
    for o in (coll.objects if coll else []):
        o.matrix_world = R @ o.matrix_world
        moved += 1
    print(f"[v16:{KEY}] relocated stage ({moved} objects) -> {stage_rect}")

# ---- config-specific additions -------------------------------------------
coll = G2["get_or_create_collection"]("V16_Extras")
for i, (cx, cy) in enumerate(cfg.get("rounds", [])):
    G2["build_round_table"](f"v16_{KEY}_round{i}", cx, cy, 60, coll)
# Free-standing high-tops are the standard 22x28 bar-height two-top.
ht_mat = G2["get_or_create_color_material"](
    "MAT_v16_hightop", (0.35, 0.24, 0.16, 1.0), roughness=0.45)
for i, (cx, cy) in enumerate(cfg.get("hightops", [])):
    G2["make_box"](f"v16_{KEY}_hightop{i}_top", cx - 11, cy - 14, 40.5,
                   22, 28, 1.5, material=ht_mat, collection=coll)
    G2["make_box"](f"v16_{KEY}_hightop{i}_post", cx - 2, cy - 2, 0,
                   4, 4, 40.5, material=ht_mat, collection=coll)
    G2["make_box"](f"v16_{KEY}_hightop{i}_foot", cx - 9, cy - 9, 0,
                   18, 18, 1.5, material=ht_mat, collection=coll)
rail_mat = G2["get_or_create_color_material"](
    "MAT_v16_rail", (0.45, 0.30, 0.18, 1.0), roughness=0.5)
IN = 0.0254

# Wall two-tops are auto-built per pool table (west wall for L tables, east
# for R). A wall rail must skip those bands or it slices through them.
TBL_L_ = 92.5
west_tt = [yt + TBL_L_ / 2 for _n, cx, yt in tables if cx < 130]


def _rail_spans(y0, y1, blocks, margin=26):
    spans, cur = [], min(y0, y1)
    end = max(y0, y1)
    for b in sorted(blocks):
        lo, hi = b - margin, b + margin
        if hi < cur or lo > end:
            continue
        if lo - cur >= 18:
            spans.append((cur, lo))
        cur = max(cur, hi)
    if end - cur >= 18:
        spans.append((cur, end))
    return spans


for i, (x0, y0, x1, y1, _role) in enumerate(cfg.get("rails", [])):
    if x0 == x1:                       # rail along W or E wall
        x, w = (x0, 8) if x0 < 158 else (x0 - 8, 8)
        blocks = west_tt if x0 < 158 else []
        for j, (sy, ey) in enumerate(_rail_spans(y0, y1, blocks)):
            G2["make_box"](f"v16_{KEY}_rail{i}_{j}", x, sy, 40, w, ey - sy, 2,
                           material=rail_mat, collection=coll)
    else:                              # rail along N or S wall
        y, l = (y0, 8) if y0 < 340 else (y0 - 8, 8)
        x, w = min(x0, x1), abs(x1 - x0)
        G2["make_box"](f"v16_{KEY}_rail{i}", x, y, 40, w, l, 2,
                       material=rail_mat, collection=coll)

# Bleachers: 3 stepped rows rising toward the nearest wall. Steps run
# along the rect's SHORT axis; the back (tallest) row hugs the wall side.
bl_mat = G2["get_or_create_color_material"](
    "MAT_v16_bleacher", (0.55, 0.48, 0.58, 1.0), roughness=0.6)
for i, (bx0, by0, bx1, by1) in enumerate(cfg.get("bleachers", [])):
    if (bx1 - bx0) < (by1 - by0):        # against W/E wall: step in x
        step = (bx1 - bx0) / 3
        for r in range(3):
            G2["make_box"](f"v16_{KEY}_bleacher{i}_r{r}",
                           bx0 + r * step, by0, 0,
                           step, by1 - by0, 40 - r * 12,
                           material=bl_mat, collection=coll)
    else:                                 # against N/S wall: step in y
        step = (by1 - by0) / 3
        for r in range(3):
            G2["make_box"](f"v16_{KEY}_bleacher{i}_r{r}",
                           bx0, by0 + r * step, 0,
                           bx1 - bx0, step, 40 - r * 12,
                           material=bl_mat, collection=coll)

# ---- lighting + look (matches the v15L3 drivers) --------------------------
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'AREA':
        if o.data.energy >= 500:
            o.data.energy = 220.0
            o.data.color = (1.0, 0.88, 0.72)
        elif o.data.energy >= 100:
            o.data.energy = 38.0
            o.data.color = (1.0, 0.96, 0.92)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('Path_'):
        o.visible_camera = False

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = (world.node_tree.nodes.get("Background")
      or world.node_tree.nodes.new("ShaderNodeBackground"))
bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1.0)
bg.inputs[1].default_value = 1.0

scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True

ROOM_W, ROOM_L = 316, 682

# ---- render 1: top-down ortho --------------------------------------------
# Hide the ceiling AND all light-fixture meshes (troffer frames/lenses,
# pendant shades) so the floor plan reads clean — from above they overlay
# every table, and the frame meshes render as black bars near the door
# corners. The AREA lights themselves stay on, so illumination holds.
if VIEW in ("topdown", "both"):
    HIDE_COLLS = {"Ceiling_Troffers", "Pendant_Fixtures"}
    hidden = []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        n = o.name.lower()
        in_hidden_coll = any(c.name in HIDE_COLLS
                             for c in o.users_collection)
        # (v17: the Entry_Step hide is gone — the entry well is now real,
        # exposed geometry with the floor slab cut around it.)
        if 'ceiling' in n or n.startswith('ceil') or in_hidden_coll:
            o.hide_render = True
            hidden.append(o)
    cd = bpy.data.cameras.new("CAM_v16_topdown")
    cd.type = 'ORTHO'
    cd.ortho_scale = (ROOM_L + 20) * IN
    co = bpy.data.objects.new("CAM_v16_topdown", cd)
    bpy.context.collection.objects.link(co)
    scene.camera = co
    co.location = ((ROOM_W / 2) * IN, (ROOM_L / 2) * IN, 30.0)
    co.rotation_euler = (0, 0, 0)
    scene.view_settings.exposure = 0.0
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 3200
    out1 = os.path.join(HERE, f"render_v16_{KEY}_topdown.png")
    scene.render.filepath = out1
    t0 = time.time()
    print(f"[v16:{KEY}] rendering topdown -> {out1}")
    bpy.ops.render.render(write_still=True)
    print(f"[v16:{KEY}] topdown DONE in {time.time()-t0:.1f}s")
    for o in hidden:
        o.hide_render = False

# ---- render 2: 5.5 ft eye height, west side aiming at Main Entry ----------
if VIEW not in ("persp", "both"):
    raise SystemExit(0)
EYE_H = 66
CAM = (60.0 * IN, (ROOM_L - 30) * IN, EYE_H * IN)
LOOK = (ROOM_W * IN, (ROOM_L - 70) * IN, 48 * IN)
cd2 = bpy.data.cameras.new("CAM_v16_5p5ft")
cd2.type = 'PERSP'
cd2.lens = 14.0
cd2.clip_end = 400.0
co2 = bpy.data.objects.new("CAM_v16_5p5ft", cd2)
bpy.context.collection.objects.link(co2)
scene.camera = co2
co2.location = CAM
direction = Vector(LOOK) - Vector(CAM)
co2.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.view_settings.exposure = -0.7
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440
out2 = os.path.join(HERE, f"render_v16_{KEY}_persp_west_to_ME_5p5ft.png")
scene.render.filepath = out2
t0 = time.time()
print(f"[v16:{KEY}] rendering 5.5ft persp -> {out2}")
bpy.ops.render.render(write_still=True)
print(f"[v16:{KEY}] persp DONE in {time.time()-t0:.1f}s")
