# Site scale check — Village Inn Restaurant & Lounge

Google Maps satellite screenshot (see `references/village_inn_satellite.jpg`),
zoomed such that the "20 ft" scale bar spans **118 px**, giving 0.1695 ft/px
(≈ 2.034 in/px).

## Building measurements (from pixel grid, ±5%)
- North edge (TL→TR): ~105 ft
- East edge (TR→BR): ~79 ft
- South edge (BR→BL): ~144 ft (building has an SE extension — not a pure rectangle)
- West edge (BL→TL): ~84 ft

## Modeled pool room
- **26.3 ft × 56.8 ft** (316" × 682")
- NW exterior corner anchored at the top-left of the roof (per user marker at
  the awning end + thin white line inside corner)

## Fit
The pool room takes:
- ~57 ft of the ~84 ft west wall → ~27 ft of building remains south of the SW
  pool-room corner (storage / kitchen / offices zone)
- ~26 ft of the ~105 ft north wall → ~79 ft of building east of the NE
  pool-room corner (bar + restaurant)

Overlay: `references/pool_room_footprint_on_satellite.png` (red rectangle rotated
40° CW around SW corner to align the west edge of the pool room with the
building's west wall, per user tuning).
