# Pool Room Blender Project

Procedural Blender build of a real pool room at Village Inn Restaurant & Lounge
(Portland, OR area). The room is modeled from measurements and photos taken on
site, then rendered top-down + several perspective angles for layout planning.

## Live links

All three are single self-contained pages/files and cross-link each other:

- **Walk it** — first-person walkthrough of all nine layouts:
  https://claude.ai/code/artifact/29c21156-ee9c-46b8-96b3-bf32162aacfe
- **Get the PDF** — one-tap download page (options study + one-page sheet):
  https://claude.ai/code/artifact/13ae99fe-5608-405e-b746-cdbad72873cd
- **Weigh the options** — interactive decision deck (set weights, re-rank live):
  https://claude.ai/code/artifact/5a9942da-0297-48fe-8acb-24d5e81baa24

The print poster (`docs/pool_room_poster.pdf`) carries the same three URLs
as QR codes. URLs are defined once in `analysis/project_urls.py`.

## Room

- Interior: **316" wide (W) x 682" long (L)** — ~26'4" x ~56'10"
- 5 doors: Main Entry (E wall, S end, railed stair landing), Kitchen (E wall,
  N of HVAC chase), Emergency Exit (S wall, right of center), Storage A (N wall,
  east end), Storage B (E wall, north end)
- NW corner stage 96" x 48" with ball locker + triple locker on N wall
- 6 Diamond Pro-Am 7ft pool tables in a 3x2 grid
- 4 folding banquet tables in a 2x2 grid + 2 stacking 48" round tables
- 3 black-vinyl booth sections along N wall
- East-wall two-tops with pub bar stools + chrome footrest ring
- Buffet along E wall

## Orientation convention

Top-down render orientation (Blender camera looking straight down at +Z-negative):

- image-top    = high Y = **SOUTH wall** (Emergency Exit, Main Entry south end)
- image-bottom = low  Y = **NORTH wall** (Stage, Lockers, Storage A)
- image-right  = high X = **EAST wall** (Main Entry, Kitchen, Buffet, Storage B)
- image-left   = low  X = **WEST wall** (folding banquets along this wall)

## Layout

```
build_pool_room.py            -- room shell, walls, ceiling, floor, doors, HVAC,
                                  lights, cameras, materials, human figures
build_pool_room_furniture.py  -- all furniture: pool tables, two-tops, bar
                                  stools + footrest ring, classroom folding
                                  banquets, round stacking tables, booths,
                                  buffet, stage, lockers
drivers/                      -- one Blender driver script per render angle
annotators/                   -- PIL scripts that add title / view info /
                                  callouts to raw renders
renders/                      -- latest annotated PNGs (v15L2)
```

## Version log

- v15L2 (current): Round stacking tables share the folding banquet surface —
  MAT_class_top (0.93, 0.91, 0.84, roughness 0.38) top + MAT_class_bump T-mold
  bullnose ring (0.78, 0.75, 0.68, roughness 0.55). 1.25" top thickness, 64-vertex
  smooth-shaded, chrome splayed legs, black plastic foot caps, X cross-brace.
- v15L : 2 x 48" folding stacking rounds between NW stage and Storage A door,
  replacing back row of classroom (Option A).
- v15k : Lockers (ball + triple, 72H x 18D on N wall), classroom tables
  converted to folding banquets, chrome footrest ring on bar stools, bench
  replaced by 3 black-vinyl booth sections.

## Render pattern

```bash
cd /tmp/blender_test
LOG=/tmp/log_$(date +%s).log
setsid nohup /tmp/blender-4.2.3-linux-x64/blender \
  --background --factory-startup \
  --python drivers/<driver>.py \
  > $LOG 2>&1 < /dev/null &
disown
```

Cycles CPU, 20-32 samples with denoising, Filmic view transform at -0.4 EV.
Perspective renders use 14mm ultra-wide by default; the SW-corner high-res
view uses 11mm to catch the full west wall + Emergency Exit doorway.
