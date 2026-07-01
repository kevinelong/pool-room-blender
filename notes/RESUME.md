# RESUME — Pool Room Blender Project

**Snapshot time:** Wednesday, July 1, 2026 at 3:37 PM PDT
**Reason for snapshot:** Reboot before resuming work

---

## TL;DR — Where we are

Repo hardening + nightly Drive mirror **are done**. Two loose ends before reboot:

1. **Drive baseline upload is blocked** by a Drive connector auth-scope loop (logged as diagnostic `f5079d24`). The scheduled task itself is fine and will fire tomorrow.
2. **v15L3 cue re-render has NOT been produced yet.** Build code is updated (source of truth in `build_pool_room_furniture.py`); no render exists with the new cue geometry.
3. **Turned-left SW render** at `/tmp/blender_test/render_v15L_persp_SW_lookNW_hi.png` was completed but never inspected, annotated, or shared. Note: it was rendered **before** the v15L3 cue geometry rewrite, so cues in that image are the old boxy version.

---

## Repo — SOURCE OF TRUTH

- **URL:** https://github.com/kevinelong/pool-room-blender (private)
- **Latest commit:** `1a24bc6` — "v15L3 org: references/ + notes/ + render.sh + Makefile"
- **Prior commits:**
  - `fb33dc0` LFS enable + migrate PNGs
  - `255f505` v15L3 cue rebuild (tapered cylinders)
  - `c5ef72e` SW→NE hi-res render
  - `b0caabd` initial import
- **Git LFS:** enabled, tracking `*.png *.jpg *.jpeg *.blend *.blend1 *.zip`. All existing PNGs migrated via `git lfs migrate import --include=... --everything --yes` and force-pushed.
- **Push pattern:** `bash` with `api_credentials=["github"]` for `gh` and `git push`.

### Repo layout

```
/home/user/workspace/pool_room_blender/
├─ build_pool_room.py              # room shell (source of truth)
├─ build_pool_room_furniture.py    # furniture (source of truth) — v15L3 cue code here (~line 2144)
├─ drivers/                        # 5 driver scripts
├─ annotators/                     # 4 PIL annotator scripts
├─ renders/                        # LFS-tracked PNGs (6 files)
├─ references/
│   ├─ village_inn_satellite.jpg
│   └─ pool_room_footprint_on_satellite.png
├─ notes/
│   ├─ v15L.md v15L2.md v15L3.md site_scale.md
│   └─ RESUME.md  (this file)
├─ render.sh (executable — list|all|<driver_name>)
├─ Makefile (topdown, sw_hi, ee_wide, ns_ew, all, check, list)
├─ .gitattributes .gitignore README.md
```

---

## Baseline zip

- **Path:** `/home/user/workspace/pool_room_blender_2026-07-01.zip` (10.4 MB)
- **Shared to user** as asset `pool_room_blender_baseline_2026-07-01` (asset_id `04401031-549a-4a9e-bfe9-0660445be00a`)
- Contains the full repo at commit `1a24bc6` minus `.git`.

---

## Nightly Drive mirror — SCHEDULED

- **Cron ID:** `87e306b5`
- **Session ID (owns the task):** `f5079d24-e928-44f1-b530-e5d06be45d5e`
- **Cron expression:** `0 9 * * *` UTC = 2:00 AM PDT (1:00 AM PST during standard time)
- **Next run:** Thursday, July 2, 2026 at 2:00 AM PDT
- **exact:** true, **background:** true
- **Task recipe:**
  1. `git clone --depth=1 https://github.com/kevinelong/pool-room-blender.git /tmp/prb_mirror` + `git lfs pull`
  2. `DATE=$(TZ=America/Los_Angeles date +%Y-%m-%d)`
  3. `zip -r /home/user/workspace/pool_room_blender_${DATE}.zip prb_mirror -x 'prb_mirror/.git/*'`
  4. Verify zip > 100KB
  5. `call_external_tool(source_id="google_drive", tool_name="export_files", arguments={"file_paths":[...]})`
  6. Silent on success; in-app failure notification on any error
  7. Cleanup local zip + `/tmp/prb_mirror`

### Drive auth issue (BLOCKER for baseline upload)

- `export_files` returns `requires_auth=true` even after 6+ successful `[CONNECTOR AUTH]` reminders
- `gws` CLI reports "authorization is outdated" the same way
- Logged as diagnostic `f5079d24` (external_connector, major)
- **Impact:** the scheduled task will fire tomorrow; if scope-refresh resolves overnight it works silently, otherwise it will send an in-app failure notification. Fallback available: rewrite task to mirror to Dropbox instead (Dropbox is CONNECTED).

---

## User instructions — PRESERVE VERBATIM

1. **(persistent, all future renders)** "after render edit image and annotate similar to initial 2d diagram that came in along side photos and remember to do this with future renders."
2. **(annotation rule v15+)** Strip ALL numeric position coords from annotation callouts. Descriptive only.
3. **(orientation, DO NOT re-derive)** image-top = high Y = SOUTH (Main Entry east end, Emergency Exit east half); image-bottom = low Y = NORTH (stage, lockers, Storage A); image-right = high X = EAST; image-left = low X = WEST.
4. **(v15c doors — DO NOT change)** Main Entry E-wall south (ROOM_L-70, 70), Kitchen E-wall (290, 40), Emergency Exit S-wall (ROOM_W-95, 65), Storage A N-wall east end (ROOM_W-40, 36), Storage B E-wall north end (4, 36).
5. **(v15L rounds)** Option A: 48" folding stacking rounds between stage x=96 and Storage A door x=276
6. **(v15L2)** Round tables share classroom folding banquet surface material
7. **(v15L3 cue)** "move all the pool cues 1 ft closer to their corresponding pool table and move tip down to touch the table and then butt of cue up to not intersect the pool table rails"
8. **(v15L3 cue interpretation, user-selected)** "Realistic natural rest: butt just above rail (~38"), gentle tilt" — keeps full 58" cue length, shifts whole cue 12" inward, adds 6° tilt

---

## v15L3 cue geometry (already in code, not yet rendered)

Location: `build_pool_room_furniture.py` around line 2144, function `build_cues()`.

- Rendered as rotated tapered cylinders (was axis-aligned boxes)
- Tip Z = **32.0"** (TBL_H, on the felt)
- Butt Z = **38.0"** (2.5" above 35.5" rail top)
- INSET_FROM_RAIL = **16"** (was 4"; shifted 12" closer to table)
- Rise 6", run 57.69", full 58" length preserved
- Server clearance: 18.6" between butt and two-top at hip height; butt at 38" ≤ hip 39-43" typical adult. Future bump to 42-44" recommended if full tray clearance needed.

---

## Renders already produced

Shared as `pool_room_layout` (version history):
- `render_topdown_v15L2_annotated.png`
- `render_v15L_persp_Exit_to_NW_wide_annotated.png`
- `render_v15L_persp_E_to_W_north_strip_annotated.png`
- `render_v15L_persp_SW_to_NE_wide_annotated.png`
- `render_v15L_persp_SW_to_NE_hi.png` (2560×1440)

Shared as `pool_room_satellite_fit`:
- Village Inn satellite with red rectangle rotated 40° CW around SW pivot

### Not yet shared / annotated

- `/tmp/blender_test/render_v15L_persp_SW_lookNW_hi.png` (2560×1440, 11mm, cam LOOK_X=130, LOOK_Y=20 — turned-left view). **Made BEFORE v15L3 cue changes.** May need re-render depending on whether user wants cue-updated version.

---

## Satellite fit reference

- Village Inn Restaurant & Lounge (Portland, OR area)
- Scale: **20 ft = 118 px → 0.1695 ft/px (2.034 in/px)**
- Building footprint: ~105 ft (N) × ~80 ft (E) × ~144 ft (S, L-shape) × ~84 ft (W)
- Pool room 26.3 × 56.8 ft fits with ~27 ft below SW corner + ~79 ft east of NE corner
- Overlay red rectangle (rotated 40° CW around SW pivot):
  - NW=(694,228), NE=(826,311), SE=(647,595), SW=(516,512)

---

## Room + build constants (memorize)

- ROOM_W = 316", ROOM_L = 682"
- IN = 0.0254 (inch → meter)
- TBL_H = 32" (table felt height)
- RAIL_H = 3.5" (top of rail = 35.5")
- BEAM_Y = 332"
- Emergency Exit door center: x=253.5", y=ROOM_L
- v15L3 west-side cue: tip x=94.25 z=32; butt x=36.56 z=38; 60.25" service lane; 18.6" gap butt-to-two-top

---

## Render workflow (post-reboot)

Blender binary: `/tmp/blender-4.2.3-linux-x64/blender`
Working dir for builds: `/tmp/blender_test/`

Source of truth is `/home/user/workspace/pool_room_blender/`. Before rendering:
- `./render.sh list` — see available drivers
- `./render.sh <driver_name>` — stages files to `/tmp/blender_test/` and runs
- `./render.sh all` — run every driver
- Or `make topdown` / `make sw_hi` / etc.

Manual pattern (if not using render.sh):
```
cp /home/user/workspace/pool_room_blender/build_pool_room*.py /tmp/blender_test/
setsid nohup /tmp/blender-4.2.3-linux-x64/blender --background --factory-startup \
  --python /path/to/driver.py > /tmp/log_<name>.log 2>&1 &
disown
```

- 2560×1440 @ 24 samples ≈ 12 min
- 1280×720 @ 20 samples ≈ 2.5 min
- Poll: `pgrep -af blender`

**Sharing:** `share_file(name="pool_room_layout", should_validate=False)` for main asset version history.

---

## Connector status

- `github_mcp_direct`: CONNECTED — use `gh`/`git` with `api_credentials=["github"]`
- `google_drive`: officially CONNECTED but auth loop on export_files — see BLOCKER above
- `dropbox`, `gcal`, `finance`, `files` (search_files_v2): CONNECTED

---

## Immediate next steps after reboot

**Priority order:**

1. **Check if Drive auth resolved:**
   ```
   call_external_tool(source_id="google_drive", tool_name="export_files",
     arguments={"file_paths": ["/home/user/workspace/pool_room_blender_2026-07-01.zip"]})
   ```
   If success → baseline is in Drive, done.
   If still requires_auth → ask user whether to (a) rewrite the cron to mirror to Dropbox instead, or (b) wait for engineering fix on the diagnostic.

2. **Check tomorrow's mirror run status:**
   ```
   pplx-tool schedule_cron <<'JSON'
   {"action":"list","cross_session":true}
   JSON
   ```
   Cron ID `87e306b5`. If it fired successfully, done. If it failed, expect in-app notification with details.

3. **Ask user about v15L3 cue re-render:**
   - Should I render a new v15L3 top-down + at least one perspective with the updated cues?
   - Which cameras? (Recommend: topdown + SW→NE hi + Exit→NW wide, all annotated per persistent rules)

4. **Turned-left SW render at `/tmp/blender_test/render_v15L_persp_SW_lookNW_hi.png`:**
   - Was completed pre-cue-fix. Ask user whether to (a) inspect + annotate + share as-is (fastest), or (b) re-render with new v15L3 cues first.

**Note on /tmp:** `/tmp/blender_test/` may be wiped by reboot. If so, all in-progress renders are gone; re-run via `./render.sh <driver>` from the repo. The repo itself in `/home/user/workspace/` should persist.

---

## Session URL

Canonical thread: https://www.perplexity.ai/computer/tasks/97d989a0-0edd-4fd4-a18a-d7c9b51a0ebe
