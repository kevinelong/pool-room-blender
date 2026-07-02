"""v15L3 perspective: from Emergency Exit toward Main Entry.

Both doors are on the SOUTH wall:
  Emergency Exit — S wall east half (center approx x=ROOM_W-95=221, y=ROOM_L)
  Main Entry    — E wall south end at (ROOM_W, ROOM_L-70)  [SE corner]

Wait — clarifying: Main Entry is actually on E-wall south (per rule #4:
"Main Entry E-wall south (ROOM_L-70, 70)"). So Emergency Exit is on the
S wall, Main Entry is on the E wall near the SE corner. Camera sits just
inside Emergency Exit looking toward SE corner (roughly southwest of the
door position is actually toward the west side of the room).

Given the user's ask "from bottom right emergency entrance toward main
entrance in bottom left" and their answered clarification "camera near NE
corner looking SW along south wall" — I'll place the camera near the
image-top-right of the topdown (which is actually the SE corner interior
of the room = high X, high Y), looking WEST (lower X) along the south
wall so the Main Entry door and the row of tables on the south end come
into view.

Wait — Emergency Exit is on the S wall east half but not exactly at the
NE-image-corner. NE image corner corresponds to SE room corner
(high X, high Y). The Emergency Exit door center is at
(x=ROOM_W-95=221, y=ROOM_L=682). Main Entry door is on E wall at
(x=ROOM_W=316, y=ROOM_L-70=612).

So Emergency Exit is a bit west of the SE corner; Main Entry is a bit
south of the SE corner. They're both hugging the SE corner. To fit the
user's mental map ("from bottom right toward bottom left" — but on their
topdown mental map bottom-left was already interpreted as image-bottom-left
of the topdown, which is our NORTH-WEST room corner) — I'll follow the
clarification chosen: camera near Emergency Exit looking SW along south
wall.

Camera position: just inside Emergency Exit, ~24" west of door center,
~30" north of south wall.
Look-at: aim toward the west end of the south wall (Main Entry direction
plus continuing along the wall westward), roughly x=60, y=ROOM_L-24.
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
EYE_H  = 96          # 8 ft eye height (matches wider2)
LOOK_H = 12

# Camera near Emergency Exit interior — image top-right of the topdown =
# high X, high Y in room coords. Emergency Exit is on S wall (y=ROOM_L)
# with center at x=ROOM_W-95=221. Stand ~24" west of door, ~30" inside
# (south wall is high Y, so "inside" = lower Y).
CAM_X = (ROOM_W - 95 - 24) * IN     # 197
CAM_Y = (ROOM_L - 30) * IN          # 652
CAM_Z = EYE_H * IN

# Look-at: aim WEST-SW along south wall. Target the west end of south
# wall interior (x=60, y near south wall).
LOOK_X =  60.0 * IN
LOOK_Y = (ROOM_L - 40) * IN
LOOK_Z = LOOK_H * IN

cd = bpy.data.cameras.new("CAM_v15L3_ee_to_me")
cd.type = 'PERSP'
cd.lens = 12.0          # slightly less wide than 11mm to reduce distortion
cd.clip_end = 400.0
co = bpy.data.objects.new("CAM_v15L3_ee_to_me", cd)
bpy.context.collection.objects.link(co)
scene.camera = co
co.location = (CAM_X, CAM_Y, CAM_Z)
direction = Vector((LOOK_X, LOOK_Y, LOOK_Z)) - Vector((CAM_X, CAM_Y, CAM_Z))
co.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

out = os.path.join(HERE, "render_v15L3_persp_EE_to_ME.png")
scene.render.filepath = out
t0 = time.time()
print(f"[v15L3-ee-to-me] rendering -> {out}")
print(f"[v15L3-ee-to-me] cam=({CAM_X/IN:.1f},{CAM_Y/IN:.1f},{CAM_Z/IN:.1f}) look=({LOOK_X/IN:.1f},{LOOK_Y/IN:.1f},{LOOK_Z/IN:.1f}) lens={cd.lens}mm expo=-0.7")
bpy.ops.render.render(write_still=True)
print(f"[v15L3-ee-to-me] DONE in {time.time()-t0:.1f}s")
