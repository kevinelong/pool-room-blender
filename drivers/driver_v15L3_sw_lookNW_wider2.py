"""v15L3 EVEN wider/lefter perspective from SW corner + darker exposure.

Changes vs driver_v15L3_sw_lookNW_wider.py:
  - LOOK_X 130" -> 80" (push aim ~15deg further counterclockwise)
  - Exposure -0.4 -> -0.9 (tame the overexposed upper-left / stage bleed)
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
scene.view_settings.exposure = -0.9   # was -0.4
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440

IN = 0.0254
ROOM_W = 316
ROOM_L = 682
EYE_H  = 96
LOOK_H = 12

CAM_X = 28.0 * IN
CAM_Y = (ROOM_L - 28.0) * IN
CAM_Z = EYE_H * IN

LOOK_X =  80.0 * IN   # was 130 -- push further left
LOOK_Y =  20.0 * IN
LOOK_Z = LOOK_H * IN

cd = bpy.data.cameras.new("CAM_v15L3_sw_lookNW2")
cd.type = 'PERSP'
cd.lens = 11.0
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L3_sw_lookNW2", cd)
bpy.context.collection.objects.link(co)
scene.camera = co
co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
co.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

out = os.path.join(HERE, "render_v15L3_persp_SW_lookNW_wider2.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L3-sw-wider2] rendering -> {out}")
print(f"[v15L3-sw-wider2] cam=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm expo=-0.9")
bpy.ops.render.render(write_still=True)
print(f"[v15L3-sw-wider2] DONE in {time.time()-t0:.1f}s")
