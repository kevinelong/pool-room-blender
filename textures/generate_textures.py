#!/usr/bin/env python3
"""Regenerate the 21 texture PNGs the build scripts load at render time.

The original textures lived only in the first sandbox's /tmp and were lost
in a reboot (renders came out magenta — Blender's missing-image color).
This script recreates them procedurally with PIL, tuned to match the look
of the committed v15L3 renders: white vertical-plank walls, white-painted
CMU, off-white acoustic ceiling tile, cream VCT floor, tan wood paneling,
rough brown beam, Diamond-blue felt.

Each material family gets albedo/normal/roughness. build_pool_room.py loads
them from TEXTURE_DIR, which resolves to /tmp when Blender runs with an
unsaved file (the normal headless-driver case), so default output is /tmp.

Usage:
    python3 textures/generate_textures.py [output_dir]
"""
import random
import sys

from PIL import Image, ImageDraw

SIZE = 512
random.seed(15)  # deterministic output


def noisy(img, amp):
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y][:3]
            d = random.randint(-amp, amp)
            px[x, y] = (max(0, min(255, r + d)),
                        max(0, min(255, g + d)),
                        max(0, min(255, b + d)))
    return img


def flat_normal(amp=2):
    img = Image.new("RGB", (SIZE, SIZE), (128, 128, 255))
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            px[x, y] = (128 + random.randint(-amp, amp),
                        128 + random.randint(-amp, amp),
                        255)
    return img


def flat_rough(value, amp=6):
    img = Image.new("RGB", (SIZE, SIZE), (value,) * 3)
    return noisy(img, amp)


def vertical_grain(img, streaks, amp):
    """Darken/lighten thin full-height columns to fake wood grain."""
    px = img.load()
    for _ in range(streaks):
        x0 = random.randrange(SIZE)
        d = random.randint(-amp, amp)
        w = random.randint(1, 3)
        for dx in range(w):
            x = (x0 + dx) % SIZE
            for y in range(SIZE):
                r, g, b = px[x, y][:3]
                px[x, y] = (max(0, min(255, r + d)),
                            max(0, min(255, g + d)),
                            max(0, min(255, b + d)))
    return img


def save(img, name, outdir):
    img.save(f"{outdir}/{name}.png")
    print(f"  wrote {outdir}/{name}.png")


def make_felt(outdir):
    # Diamond blue felt (matches committed v15L3 renders' light-blue beds)
    alb = noisy(Image.new("RGB", (SIZE, SIZE), (25, 120, 205)), 5)
    save(alb, "felt_albedo", outdir)
    save(flat_normal(3), "felt_normal", outdir)
    save(flat_rough(220), "felt_roughness", outdir)


def make_vct_floor(outdir):
    # Tile covers 48"; 4x4 grid of 12" VCT tiles, cream with seams.
    alb = Image.new("RGB", (SIZE, SIZE), (112, 84, 60))
    d = ImageDraw.Draw(alb)
    cell = SIZE // 4
    for ty in range(4):
        for tx in range(4):
            dv = random.randint(-6, 6)
            d.rectangle([tx * cell, ty * cell,
                         (tx + 1) * cell - 1, (ty + 1) * cell - 1],
                        fill=(112 + dv, 84 + dv, 60 + dv))
    for i in range(5):
        p = min(i * cell, SIZE - 1)
        d.line([(p, 0), (p, SIZE)], fill=(88, 66, 46), width=2)
        d.line([(0, p), (SIZE, p)], fill=(88, 66, 46), width=2)
    d2 = ImageDraw.Draw(alb)
    for _ in range(4000):                       # dark speckle per video
        x, y = random.randrange(SIZE), random.randrange(SIZE)
        v = random.randint(-45, -15)
        d2.point((x, y), fill=(112 + v, 84 + v, 60 + v))
    save(noisy(alb, 4), "vct_floor_albedo", outdir)
    save(flat_normal(2), "vct_floor_normal", outdir)
    save(flat_rough(90), "vct_floor_roughness", outdir)


def make_white_plank(outdir):
    # Tile covers 48"; 8 vertical planks of 6" each, near-white.
    alb = Image.new("RGB", (SIZE, SIZE), (240, 240, 237))
    d = ImageDraw.Draw(alb)
    plank = SIZE // 8
    for i in range(8):
        dv = random.randint(-4, 4)
        d.rectangle([i * plank, 0, (i + 1) * plank - 1, SIZE],
                    fill=(240 + dv, 240 + dv, 237 + dv))
        d.line([(i * plank, 0), (i * plank, SIZE)],
               fill=(205, 205, 202), width=2)
    alb = vertical_grain(alb, 60, 5)
    save(noisy(alb, 2), "white_plank_albedo", outdir)
    save(flat_normal(2), "white_plank_normal", outdir)
    save(flat_rough(150), "white_plank_roughness", outdir)


def make_cmu_wall(outdir):
    # Tile covers 64"; running-bond 16x8" blocks -> 4 cols x 8 rows.
    alb = Image.new("RGB", (SIZE, SIZE), (196, 196, 193))  # mortar
    d = ImageDraw.Draw(alb)
    bw, bh, m = SIZE // 4, SIZE // 8, 3
    for row in range(8):
        off = (bw // 2) if row % 2 else 0
        for col in range(-1, 5):
            x0 = col * bw + off
            dv = random.randint(-5, 5)
            d.rectangle([x0 + m, row * bh + m,
                         x0 + bw - m, (row + 1) * bh - m],
                        fill=(225 + dv, 225 + dv, 222 + dv))
    save(noisy(alb, 3), "cmu_wall_albedo", outdir)
    save(flat_normal(3), "cmu_wall_normal", outdir)
    save(flat_rough(180), "cmu_wall_roughness", outdir)


def make_ceiling_tile(outdir):
    # Tile covers 48"; 2x2 grid of 24" acoustic tiles.
    alb = Image.new("RGB", (SIZE, SIZE), (235, 235, 230))
    d = ImageDraw.Draw(alb)
    half = SIZE // 2
    for p in (0, half, SIZE - 1):
        d.line([(p, 0), (p, SIZE)], fill=(208, 208, 203), width=3)
        d.line([(0, p), (SIZE, p)], fill=(208, 208, 203), width=3)
    # pinhole speckle
    for _ in range(2500):
        x, y = random.randrange(SIZE), random.randrange(SIZE)
        v = random.randint(210, 228)
        d.point((x, y), fill=(v, v, v - 4))
    save(alb, "ceiling_tile_albedo", outdir)
    save(flat_normal(2), "ceiling_tile_normal", outdir)
    save(flat_rough(200), "ceiling_tile_roughness", outdir)


def make_wood_panel(outdir):
    # Tile covers 48"; 4 vertical boards of 12", warm tan.
    alb = Image.new("RGB", (SIZE, SIZE), (168, 124, 82))
    d = ImageDraw.Draw(alb)
    board = SIZE // 4
    for i in range(4):
        dv = random.randint(-10, 10)
        d.rectangle([i * board, 0, (i + 1) * board - 1, SIZE],
                    fill=(168 + dv, 124 + dv, 82 + dv // 2))
        d.line([(i * board, 0), (i * board, SIZE)],
               fill=(120, 86, 54), width=2)
    alb = vertical_grain(alb, 90, 12)
    save(noisy(alb, 4), "wood_panel_albedo", outdir)
    save(flat_normal(3), "wood_panel_normal", outdir)
    save(flat_rough(130), "wood_panel_roughness", outdir)


def make_wood_beam(outdir):
    # Tile covers 96"; rough-sawn brown, horizontal grain.
    alb = Image.new("RGB", (SIZE, SIZE), (120, 88, 58))
    alb = alb.rotate(90)
    alb = vertical_grain(alb, 120, 14).rotate(-90)
    save(noisy(alb, 5), "wood_beam_albedo", outdir)
    save(flat_normal(4), "wood_beam_normal", outdir)
    save(flat_rough(170), "wood_beam_roughness", outdir)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
    print(f"Generating textures -> {outdir}")
    make_felt(outdir)
    make_vct_floor(outdir)
    make_white_plank(outdir)
    make_cmu_wall(outdir)
    make_ceiling_tile(outdir)
    make_wood_panel(outdir)
    make_wood_beam(outdir)
    print("done: 21 PNGs")


if __name__ == "__main__":
    main()
