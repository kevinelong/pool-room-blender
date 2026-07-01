"""v15L3 top-down orthographic render — companion to the SW wider perspective.
Includes v15L3 cue geometry (tapered cylinders, tip on felt, 12" inward shift).
"""
import bpy, os, time
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

# Hide ceiling for top-down clarity
for o in bpy.data.objects:
    if o.type == 'MESH':
        n = o.name.lower()
        if 'ceiling' in n or n.startswith('ceil'):
            o.hide_render = True

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background") or world.node_tree.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1.0)
bg.inputs[1].default_value = 1.0

scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.0
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 3200   # 1:2 to match room aspect roughly

IN = 0.0254
ROOM_W = 316
ROOM_L = 682

# Orthographic camera looking straight down centered on the room
cd = bpy.data.cameras.new("CAM_v15L3_topdown")
cd.type = 'ORTHO'
# Ortho scale = largest dimension in meters + small padding
cd.ortho_scale = (ROOM_L + 20) * IN
co = bpy.data.objects.new("CAM_v15L3_topdown", cd)
bpy.context.collection.objects.link(co)
scene.camera = co
co.location = ((ROOM_W/2) * IN, (ROOM_L/2) * IN, 30.0)   # 30m up
co.rotation_euler = (0, 0, 0)   # looks down -Z

out = os.path.join(HERE, "render_v15L3_topdown.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L3-topdown] rendering -> {out}")
bpy.ops.render.render(write_still=True)
print(f"[v15L3-topdown] DONE in {time.time()-t0:.1f}s")
