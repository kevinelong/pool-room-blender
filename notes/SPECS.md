# Fixed furniture specs — user-locked 2026-07-03

These override anything older. Do not change without an explicit user
instruction.

1. **Pool tables: exactly SIX in every configuration.** Never any other
   quantity, in any option, variant, or study. (Diamond 7-ft: 78x39
   playfield, 53.5x92.5 cabinet, unchanged.)
2. **Round tables: 5 ft (60") diameter** stacking folding rounds.
   A 60" round seats 8.
3. **Classroom tables: 2.5 x 8 ft (30" x 96")** folding banquet tables.
4. **Two-tops: 22" x 28" tops, standard bar height (~42" tall)** —
   both the wall-anchored ones and any free-standing "high-top".
   A two-top seats 2.

Applied in:
- `build_pool_room_furniture.py` (CLASS_W=30, TWOTOP_W=26 -> 22" top,
  TWOTOP_L=28, ROUND_DIA=60)
- `configs/v16_configs.py` (N_TABLES=6 asserted in capacities(),
  ROUND_D=60, ROUND_COVERS=8, HIGHTOP_SEATS=2)
- `drivers/driver_v16_variant.py` (rounds at 60", high-tops built as
  22x28 bar-height two-tops)

## v18 addendum (2026-07-04)

5. **Emergency Exit: WEST end of the south wall** — DOORS entry
   `('F', 30, 65)`, door span x 30..95, center (62.5, 682). The v15c
   east-half position (ROOM_W-95) was wrong per the reference video and
   is superseded. Egress checks, configs, and furniture placements all
   updated to keep the west-end approach clear.
