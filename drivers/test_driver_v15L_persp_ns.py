"""v15L perspective: E->W across the north strip to showcase the round tables.
Camera near the east wall (offset inward to clear Storage A door + Storage B),
at eye height, looking west along y=48 (center of the round tables' cy).
"""
import bpy, os, math, time
from mathutils import Vector

HERE = "/tmp/blender_test"
bpy.ops.wm.read_factory_settings(use_empty=True)

for fname in ("build_pool_room.py", "build_pool_room_furniture.py"):
    with open(os.path.join(HERE, fname)) as fh:
        exec(compile(fh.read(), fname, "exec"), {"__name__": "__main__"})

# Light tune (same as v15c)
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'AREA':
        if o.data.energy >= 500:
            o.data.energy = 220.0
            o.data.color = (1.0, 0.88, 0.72)
        elif o.data.energy >= 100:
            o.data.energy = 38.0
            o.data.color = (1.0, 0.96, 0.92)

# Hide path planes from camera
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('Path_'):
        o.visible_camera = False

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background") or world.node_tree.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1.0)
bg.inputs[1].default_value = 1.0

scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = -0.4
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 540

IN = 0.0254
ROOM_W = 316 * IN   # x extent
ROOM_L = 682 * IN   # y extent
EYE_H = 60 * IN     # slightly lower eye to peek under HVAC / partition beam if any
LOOK_H = 32 * IN    # aim at table-top height to keep the rounds well centered

# --- E -> W across the north strip ---
# Round tables center: (cx_left=144, cx_right=228, cy=48) in inches world.
# Storage B door is on east wall at north end (approx wy=18..? per v15c geometry).
# Position camera at east side, offset ~6" inside from wall, at cy=48 (round-tables center).
# Aim west toward the round tables and (beyond them) the stage.

CAM_X = ROOM_W - 8 * IN                        # 8" inside from east wall
CAM_Y = 48 * IN                                 # aligned with round tables' cy
CAM_Z = EYE_H

# Look at a point past the LEFT round table (cx_left=144), y slightly north of
# rounds to include a bit of the north wall / booths sliver at frame top-right.
LOOK_X = 20 * IN                                # near west wall
LOOK_Y = 48 * IN                                # same strip
LOOK_Z = LOOK_H

# Camera setup
cd = bpy.data.cameras.new("CAM_v15L_ns")
cd.type = 'PERSP'
cd.lens = 24.0                                  # 24mm for a natural framing of the ~14ft strip
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L_ns", cd)
bpy.context.collection.objects.link(co)
scene.camera = co

co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
rot_quat = direction.to_track_quat('-Z', 'Y')
co.rotation_euler = rot_quat.to_euler()

out = os.path.join(HERE, "render_v15L_persp_E_to_W_north_strip.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L-ns] rendering -> {out}")
print(f"[v15L-ns] cam loc=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm")
bpy.ops.render.render(write_still=True)
print(f"[v15L-ns] DONE in {time.time()-t0:.1f}s")
