"""v15L wide-angle perspective from Emergency Exit toward staff storage (NE)
and NW stage corner. Uses a very wide 14mm lens to fit whole room including
Main Entry (right side, near) and NW stage/lockers (deep background left)."""
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
ROOM_W = 316 * IN
ROOM_L = 682 * IN
EYE_H = 66 * IN     # standing eye ~ 5'6" for a broad framing
LOOK_H = 36 * IN    # aim slightly above table height so the diagonal reads

# Emergency Exit door center: x = ROOM_W - 95 + 65/2 = 253.5"; y = ROOM_L
# Place camera JUST inside the exit doorway, offset ~20" north (into room)
# to clear the wall + a hair west so we don't peek through it.
# NOTE: ROOM_W and ROOM_L above are already in METERS (inches * IN), so use
# raw-inch expressions here and multiply by IN once.
CAM_X = (253.5 - 6) * IN            # 6" west of Emergency Exit door center
CAM_Y = (682.0 - 22.0) * IN         # 22" inside the south wall (just past threshold)
CAM_Z = EYE_H

# Aim: NW stage / staff storage corner is at (0, 0). But to also frame the
# Storage A/B (NE at ~x=294..316, y=0..80), aim closer to true NW-ish diagonal
# but slightly RIGHT of dead-NW so the NE corner storage doors appear on the
# right side. Aim at a point ~1/3 across the room and near the north wall.
LOOK_X = 90 * IN                    # left-of-center: swings NW stage into left third
LOOK_Y = 40 * IN                    # near north wall
LOOK_Z = LOOK_H

# Camera
cd = bpy.data.cameras.new("CAM_v15L_ee")
cd.type = 'PERSP'
cd.lens = 14.0               # ULTRA-WIDE to fit whole room diagonal
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L_ee", cd)
bpy.context.collection.objects.link(co)
scene.camera = co

co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
rot_quat = direction.to_track_quat('-Z', 'Y')
co.rotation_euler = rot_quat.to_euler()

out = os.path.join(HERE, "render_v15L_persp_Exit_to_NW_wide.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L-ee] rendering -> {out}")
print(f"[v15L-ee] cam loc=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm res={scene.render.resolution_x}x{scene.render.resolution_y}")
bpy.ops.render.render(write_still=True)
print(f"[v15L-ee] DONE in {time.time()-t0:.1f}s")
