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

## v23 addendum (2026-07-05)

6. **Stage and storage lockers: REMOVED from every layout.** The classroom
   seating is also removed from all layouts. The League layout (tables
   under the beam) is retired. Option set: Social, Tournament (+north
   rounds), Center Line (+end two-tops), East Line (6 rounds, top table
   centered between round and entry rail), West Line (per-table wall
   rounds).

## v26 addendum (2026-07-05, evening review)

7. **Round chairs sit on the DIAGONALS (X shape, not +).** Only Social /
   Tournament's forced CENTER round keeps the cardinal (+) orientation.
8. **Door frontage hierarchy: kitchen door gets the deepest clearance;**
   the Emergency Exit and storage doors need less. A round or two-top may
   PARTIALLY front the kitchen door where a mandated placement needs it —
   allowed, but always called out in the notes.
9. **Staff paths never cross a pool table** — they turn down an aisle and
   cross between tables. Every walking path is width-audited; anomalies
   (<36" pinches, blocked walks) are called out in scorecards.md.
10. **Main Entry door leaf opens LEFT, exactly 90 degrees,** stopping flat
    against the south wall.
11. **2x3 layouts (Social, Tournament): a bar two-top at every table-row
    END on BOTH walls,** pushed to the wall, stools north/south facing
    their top. The row-3 south end on the east wall is skipped (entry
    well); the HVAC-adjacent one nudges south.
12. **Tournament: NO bleachers** — a five-round gallery instead. Social:
    four aligned north rounds + a forced center fifth (quincunx).
13. **East Line: the sixth round sits IN LINE with the column** (flagged:
    narrows the EE approach). **West Line: all SIX rounds present** —
    the sixth beside the entry well (flagged: crowds the Main Entry
    approach).

## v27 addendum (2026-07-05)

14. **Social Hall + Tournament House MERGED into "Four On Top".** Once the
    bleachers left, the two were geometrically identical (same tables,
    same five-round quincunx, same wall two-tops) — only seat-role labels
    differed. One option remains (key `social` kept for file continuity);
    the set renumbers to four options.

15. **v27b: second Four On Top variant ("Four On Top — Turned").** All six
    tables rotated 90°: four in a 2x2 block at the top (south), two at the
    bottom (north). Two-top bands on the top wall, between the clusters,
    and below the bottom pair (north wall) — side walls stay clear for the
    rotated table ends. West/center end swings ~47" (practical maximum,
    flagged); the east aisle carries the service spine clear of the HVAC
    chase; N/S-wall two-tops turn 90° with stools east/west.

16. **v28: shifted line variants.** "East Line — Shifted Down" and "West
    Line — Shifted Down": the six-table line slides 33.5" toward the
    bottom (north) wall so the top table's cabinet exactly clears the
    Main Entry approach — the east line's top table returns to the
    straight line and its round clears the EE corridor entirely; the
    west line's sixth round reaches the wall (chairs still graze the
    approach corner, noted). Costs, flagged: the bottom table's end swing
    runs ~45", and the west line's first round pulls inboard of the
    storage-door frontage.

17. **v29: complementary shifts of the turned 4+2 + semantic sheet.**
    "Turned Left" and "Turned Right" slide both rotated columns toward a
    side wall (right capped by the HVAC chase and entry well; the spine
    moves to the west aisle there). The pushed side's end swings run
    ~37" (flagged); the open side gets full swings and the service lane.
    The one-page top-down sheet is arranged semantically: left-shifted
    layouts down the left of the page, centered down the center,
    right-(east-)shifted down the right.

18. **v30: the kitchen-door table nudges left (user).** In both west-line
    layouts, the table whose round sits by the kitchen door moves ~14"
    west (cx 96) so its round can pull inboard (x 224) and truly clear
    the 54" door frontage — the round alone falls 2" short. Cost,
    flagged: that table's inboard swing ~48"; kitchen service threads a
    ~25" squeeze between that round and the HVAC-row round (called out).

19. **v36: spectator metric retired.** Zero in every layout since the
    bleachers left (v26); the column, deck slider/chip, and $/hr rate
    were dead weight and are removed from all surfaces. Gallery-style
    watching is covered by flex seats (rounds/two-tops facing play).

20. **v39: letters follow the semantic order.** The A–I letters now read
    alphabetically through the presentation order (down the page's
    left / centered / right columns): A left 4+2, B west 1×6, C west
    1×6 low, D center 2×3, E center 4+2, F center 1×6, G right 4+2,
    H east 1×6, I east 1×6 low. Config keys (render filenames) are
    unchanged.

21. **v50: entry well re-measured from the reference video (transposed).**
    The sunken Main Entry channel runs E-W ALONG the south wall — 70"
    run x 40" wide (N-S): door at the east end of the channel, 48" wood
    landing, two 11" treads climbing WEST to the room floor, rails
    flanking. ENTRY_WELL = (246, 642, 316, 682); egress keepout
    (210, 642, 316, 682). Previously modeled 70" along the east wall.
    Knock-ons applied: A/E/G-family SE south-wall two-tops nudged west
    clear of the top of the treads; west-line sixth round returned to
    the east wall in the freed band; H/I-family HVAC-row table jogs 12"
    west; D/F-family southmost east-wall seat slid south into the freed
    band (move, not add — the old keepout had compressed those pairs).

22. **v54: the straight 2x3 family (user) — twelve layouts, A to L.**
    The center 2x3 grid + five-round quincunx (Four On Top) gains three
    variations: Slid Left (cols 93/199), Wide Aisle (cols 95/221 — a
    72" center promenade), and Slid Right (cols 117/223). Wall two-tops
    stay on their walls; the grid and rounds move together. Letters
    re-read semantically: A left 4+2, B left 2×3, C west 1×6, D west
    1×6 low, E center 2×3, F center 4+2, G center 2×3 wide, H center
    1×6, I right 4+2, J right 2×3, K east 1×6, L east 1×6 low.
