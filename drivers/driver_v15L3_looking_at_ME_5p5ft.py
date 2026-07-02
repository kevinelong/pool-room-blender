"""v15L3 perspective: camera on WEST side of south end, aiming directly
at the Main Entry door.

Room coords (fixed rule #4):
  Main Entry door center: E wall (x=ROOM_W=316), south end (y=ROOM_L-70=612)
  Emergency Exit door center: S wall (y=ROOM_L=682), east half (x=ROOM_W-95=221)

Camera:
  - Stand on the WEST-side south-end interior corner area.
  - Position: x=60 (~5 ft from west wall), y=ROOM_L-30 (~2.5 ft north of south wall)
  - 5.5 ft eye height (66")
Aim:
  - Directly at Main Entry door (x=316, y=612), at door-handle height (~48")
"""
import bpy, os, math, time
from mathutils import Vector

HERE = "/tmp/blender_test"
bpy.ops.wm.read_factory_settings(use_empty=True)
for fname in ("build_pool_room.py", "build_pool_room_furniture.py"):
    with open(os.path.join(HERE, fname)) as fh:
        exec(compile(fh.read(), fname, "exec"), {"__name__": "__main__"})

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
scene.view_settings.exposure = -0.7
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440

IN = 0.0254
ROOM_W = 316
ROOM_L = 682
EYE_H  = 66

CAM_X =  60.0 * IN
CAM_Y = (ROOM_L - 30) * IN     # 652
CAM_Z = EYE_H * IN

# Aim directly at Main Entry door
LOOK_X = ROOM_W * IN           # 316 (east wall)
LOOK_Y = (ROOM_L - 70) * IN    # 612 (door center Y)
LOOK_Z = 48 * IN               # door-handle height

cd = bpy.data.cameras.new("CAM_v15L3_looking_at_ME_5p5ft")
cd.type = 'PERSP'
cd.lens = 14.0                 # slight wide to include some flanking room
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L3_looking_at_ME_5p5ft", cd)
bpy.context.collection.objects.link(co)
scene.camera = co
co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
co.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

out = os.path.join(HERE, "render_v15L3_persp_west_to_ME_5p5ft.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L3-west->ME] rendering -> {out}")
print(f"[v15L3-west->ME] cam=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm")
bpy.ops.render.render(write_still=True)
print(f"[v15L3-west->ME] DONE in {time.time()-t0:.1f}s")
