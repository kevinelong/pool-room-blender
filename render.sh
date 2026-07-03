#!/usr/bin/env bash
# render.sh — one-command render helper for the pool room project.
#
# Usage:
#   ./render.sh <driver-name>    # e.g. ./render.sh test_driver_v15L_persp_sw_hi
#   ./render.sh list             # show available drivers
#   ./render.sh all              # render every driver in sequence
#
# Prereqs: Blender 4.2.x at $BLENDER_BIN (default /tmp/blender-4.2.3-linux-x64/blender).
# The driver expects the two build modules to live alongside it in a working
# directory. We stage the driver + build modules to /tmp/blender_test/ so
# Blender's factory-startup can find them via HERE=/tmp/blender_test/.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
STAGE_DIR="${STAGE_DIR:-/tmp/blender_test}"
BLENDER_BIN="${BLENDER_BIN:-/tmp/blender-4.2.3-linux-x64/blender}"
DRIVERS_DIR="$REPO_DIR/drivers"
RENDERS_DIR="$REPO_DIR/renders"

_list_drivers() {
    ls "$DRIVERS_DIR"/*.py 2>/dev/null | xargs -n1 basename | sed 's/\.py$//'
}

_stage() {
    mkdir -p "$STAGE_DIR"
    cp "$REPO_DIR/build_pool_room.py"           "$STAGE_DIR/"
    cp "$REPO_DIR/build_pool_room_furniture.py" "$STAGE_DIR/"
    cp "$DRIVERS_DIR"/*.py                      "$STAGE_DIR/"
    # Texture PNGs: build_pool_room.py loads them from TEXTURE_DIR, which
    # resolves to /tmp for headless drivers (unsaved .blend). Prefer the
    # committed textures/ PNGs; a <1KB file is a git-lfs pointer, not an
    # image, so fall back to regenerating with PIL.
    local staged=0
    for tex in "$REPO_DIR"/textures/*.png; do
        [ -e "$tex" ] || continue
        if [ "$(stat -c%s "$tex")" -gt 1024 ]; then
            cp "$tex" /tmp/
            staged=1
        fi
    done
    if [ "$staged" -eq 0 ]; then
        echo "[stage] textures missing or LFS pointers — regenerating via PIL"
        python3 "$REPO_DIR/textures/generate_textures.py" /tmp
    fi
}

_run_one() {
    local driver="$1"
    local driver_py="$STAGE_DIR/$driver.py"
    if [ ! -f "$driver_py" ]; then
        echo "ERROR: driver $driver.py not found in $STAGE_DIR" >&2
        exit 1
    fi
    local log="/tmp/log_${driver}_$(date +%s).log"
    echo "[render] running $driver -> log $log"
    "$BLENDER_BIN" --background --factory-startup --python "$driver_py" > "$log" 2>&1
    echo "[render] $driver done"
    # Copy any newly-created PNGs from stage back to renders/
    find "$STAGE_DIR" -maxdepth 1 -name '*.png' -newer "$driver_py" -exec cp {} "$RENDERS_DIR/" \;
    tail -3 "$log"
}

cmd="${1:-list}"

case "$cmd" in
    list)
        echo "Available drivers:"
        _list_drivers | sed 's/^/  /'
        ;;
    all)
        _stage
        for d in $(_list_drivers); do
            _run_one "$d"
        done
        ;;
    *)
        _stage
        _run_one "$cmd"
        ;;
esac
