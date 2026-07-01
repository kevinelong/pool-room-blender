"""v15L2 wide-angle SW->NE, HIGH RES + steeper downward + wider FOV to
include the full west wall and the Emergency Exit door.

Changes vs test_driver_v15L_persp_sw.py:
  - Eye height 66" -> 96" (8 ft) for a steeper downward look
  - Look-at Z lowered so pitch is more sharply downward
  - Lens 14mm -> 11mm (even wider) to capture west wall + exit door
  - Resolution doubled: 1280x720 -> 2560x1440 for manual zoom
  - Camera nudged slightly further off the SW corner so the west wall
    and the south wall (with Emergency Exit door) are BOTH visible.
"""
import bpy, os, math, time
from mathutils import Vector

HERE = "/tmp/blender_test"
bpy.ops.wm.read_factory_settings(use_empty=True)

for fname in ("build_pool_room.py", "build_pool_room_furniture.py"):
    with open(os.path.join(HERE, fname)) as fh:
        exec(compile(fh.read(), fname, "exec"), {"__name__": "__main__"})

# Light tune (same recipe as v15c)
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
bg = world.node_tree.nodes.get("Background") or world.node_tree.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1.0)
bg.inputs[1].default_value = 1.0

scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = -0.4
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
# Double the previous 1280x720
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440

IN = 0.0254
ROOM_W = 316          # inches
ROOM_L = 682          # inches
EYE_H  = 96           # 8 ft eye height
LOOK_H = 12           # aim well below eye for a steep downward pitch

# ---- CAMERA: SW corner interior (image top-left of topdown) ----
# Pull the camera ~6" further off each wall vs prior so the west wall
# is inside the FOV rather than hugging the sensor edge.
CAM_X = 28.0 * IN
CAM_Y = (ROOM_L - 28.0) * IN
CAM_Z = EYE_H * IN

# ---- LOOK-AT: NE corner (image bottom-right of topdown) ----
LOOK_X = (ROOM_W - 40.0) * IN
LOOK_Y = 40.0 * IN
LOOK_Z = LOOK_H * IN

# Camera
cd = bpy.data.cameras.new("CAM_v15L_sw_hi")
cd.type = 'PERSP'
cd.lens = 11.0               # even wider than 14mm to catch full west wall + S wall doors
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L_sw_hi", cd)
bpy.context.collection.objects.link(co)
scene.camera = co

co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
rot_quat = direction.to_track_quat('-Z', 'Y')
co.rotation_euler = rot_quat.to_euler()

out = os.path.join(HERE, "render_v15L_persp_SW_to_NE_hi.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L-sw-hi] rendering -> {out}")
print(f"[v15L-sw-hi] cam loc=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm res={scene.render.resolution_x}x{scene.render.resolution_y}")
bpy.ops.render.render(write_still=True)
print(f"[v15L-sw-hi] DONE in {time.time()-t0:.1f}s")
