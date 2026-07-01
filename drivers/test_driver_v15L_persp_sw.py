"""v15L2 wide-angle perspective: camera in the SW corner of the room
(image top-left of topdown per user's mental map) looking diagonally
across the room toward the NE corner (image bottom-right of topdown).

Room coordinate mapping (verified from build code + annotated topdown):
  image-top of topdown    = high Y = SOUTH wall (Main Entry east end, Emergency Exit east half)
  image-bottom of topdown = low  Y = NORTH wall (Stage, Lockers, Storage A east end)
  image-right of topdown  = high X = EAST wall (Main Entry, Kitchen, Storage B)
  image-left of topdown   = low  X = WEST wall (folding banquets on this side)

User asked for view "from top-left toward bottom-right" of the topdown, so:
  Camera anchor: SW corner interior (low X, high Y)
  Look target:   NE corner (high X, low Y)  -- where Storage A/B are.
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
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720

IN = 0.0254
ROOM_W = 316          # inches
ROOM_L = 682          # inches
EYE_H = 66            # standing eye ~ 5'6" for broad framing
LOOK_H = 36           # aim slightly above table height for the diagonal read

# ---- CAMERA: SW corner interior (image top-left of topdown) ----
# 22" north of the south wall, 22" east of the west wall — tucked into
# the corner but with a hair of clearance so we don't clip the walls.
CAM_X = 22.0 * IN
CAM_Y = (ROOM_L - 22.0) * IN
CAM_Z = EYE_H * IN

# ---- LOOK-AT: NE corner (image bottom-right of topdown) ----
# Aim at ~35" in from the NE corner so both Storage A door (N wall east)
# and Storage B door (E wall north) sit near the vanishing point.
LOOK_X = (ROOM_W - 40.0) * IN
LOOK_Y = 40.0 * IN
LOOK_Z = LOOK_H * IN

# Camera
cd = bpy.data.cameras.new("CAM_v15L_sw")
cd.type = 'PERSP'
cd.lens = 14.0               # ULTRA-WIDE to fit whole room diagonal
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L_sw", cd)
bpy.context.collection.objects.link(co)
scene.camera = co

co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
rot_quat = direction.to_track_quat('-Z', 'Y')
co.rotation_euler = rot_quat.to_euler()

out = os.path.join(HERE, "render_v15L_persp_SW_to_NE_wide.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L-sw] rendering -> {out}")
print(f"[v15L-sw] cam loc=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm res={scene.render.resolution_x}x{scene.render.resolution_y}")
bpy.ops.render.render(write_still=True)
print(f"[v15L-sw] DONE in {time.time()-t0:.1f}s")
