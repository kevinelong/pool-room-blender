"""v15b topdown only."""
import bpy, os, math
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

HIDE_PREFIXES = ("Ceiling", "Troffer", "Pendant_Shade", "Pendant_Rod", "Pendant_Bulb")
KEEP_SUBSTR = ("Beam", "beam")
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    name = o.name
    if any(k in name for k in KEEP_SUBSTR): continue
    if any(name.startswith(p) or p.lower() in name.lower() for p in HIDE_PREFIXES):
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

IN = 0.0254
ROOM_W = 316 * IN
ROOM_L = 682 * IN
CEIL_H = 108 * IN

cam_data = bpy.data.cameras.new("CAM_topdown")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = ROOM_L * 1.05
cam_data.clip_end = 200.0
cam_obj = bpy.data.objects.new("CAM_topdown", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (ROOM_W * 0.5, ROOM_L * 0.5, CEIL_H + 5.0)
cam_obj.rotation_euler = (0.0, 0.0, 0.0)
scene.camera = cam_obj

scene.render.resolution_x = 720
scene.render.resolution_y = int(720 * (ROOM_L / ROOM_W))
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True

scene.render.filepath = os.path.join(HERE, "render_topdown_v15b.png")
print(f"[v15b] rendering topdown {scene.render.resolution_x}x{scene.render.resolution_y} ...")
bpy.ops.render.render(write_still=True)
print("[v15b] topdown DONE")
