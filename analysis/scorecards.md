# v16 configuration scorecards

| Config | Tables | Players | Spect. | Drink | Dine | Flex | Cue full% | Min clr" | Cocktail max run | Food max run | Svc conflicts | Egress worst | Path min" | $/hr proxy | Flip min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A · Four On Top | 6 | 24 | 0 | 0 | 0 | 62 | 67% | 56.5 | 67.6 ft | 52.0 ft | 12 | 58.8 ft | 38.2 | $821 | 0 |
| B · Four On Top — Turned | 6 | 24 | 0 | 0 | 0 | 14 | 62% | 46.8 | 72.0 ft | 45.6 ft | 9 | 61.0 ft | 44.0 | $269 | 15 |
| C · Four On Top — Turned Left | 6 | 24 | 0 | 0 | 0 | 14 | 62% | 37.2 | 72.8 ft | 46.4 ft | 9 | 61.8 ft | 44.0 | $269 | 15 |
| D · Four On Top — Turned Right | 6 | 24 | 0 | 0 | 0 | 14 | 62% | 37.2 | 93.7 ft | 69.8 ft | 9 | 59.5 ft | 37.0 | $269 | 15 |
| E · Center Line | 6 | 24 | 0 | 24 | 0 | 0 | 58% | 54.8 | 70.0 ft | 0.0 ft | 12 | 56.6 ft | 42 | $324 | 0 |
| F · East Line + West Lounge | 6 | 24 | 0 | 0 | 0 | 48 | 58% | 54.8 | 68.2 ft | 46.8 ft | 12 | 54.9 ft | 41.2 | $660 | 20 |
| G · East Line — Shifted Down | 6 | 24 | 0 | 0 | 0 | 48 | 50% | 43.0 | 71.0 ft | 44.0 ft | 12 | 57.7 ft | 47.5 | $660 | 20 |
| H · West Line + Wall Rounds | 6 | 24 | 0 | 0 | 0 | 48 | 46% | 39.3 | 59.0 ft | 34.3 ft | 0 | 52.6 ft | 25.0 | $660 | 25 |
| I · West Line — Shifted Down | 6 | 24 | 0 | 0 | 0 | 48 | 42% | 41.0 | 58.6 ft | 34.9 ft | 0 | 55.7 ft | 25.1 | $660 | 25 |

## Walking-path anomalies (clear width < 36")

- **A · Four On Top** — narrowest walk 38.2":
    - blocked: 0.0" (center-east: walk crosses a wall two-top)
- **B · Four On Top — Turned** — narrowest walk 44.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
    - blocked: 0.0" (south-east: walk crosses a wall two-top)
- **C · Four On Top — Turned Left** — narrowest walk 44.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
    - blocked: 0.0" (south-east: walk crosses a wall two-top)
- **D · Four On Top — Turned Right** — narrowest walk 37.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
    - blocked: 0.0" (south-east: walk crosses a wall two-top)
- **E · Center Line** — none; narrowest walk 42"
- **F · East Line + West Lounge** — none; narrowest walk 41.2"
- **G · East Line — Shifted Down** — none; narrowest walk 47.5"
- **H · West Line + Wall Rounds** — narrowest walk 25.0":
    - blocked: 0.0" (south-east: walk crosses a round's chairs)
    - pinch: 25.0" (center-east: between a round's chairs and a round's chairs)
- **I · West Line — Shifted Down** — narrowest walk 25.1":
    - blocked: 0.0" (south-east: walk crosses a round's chairs)
    - pinch: 25.1" (center-east: between a round's chairs and a round's chairs)

## Methodology & assumptions

**Revenue proxy** — a *comparator*, not a forecast. Every option has the
same six tables, so table rent is constant across the set; the proxy
exists to price the HOSPITALITY differences (drink seats vs dining
covers vs flex seats vs spectators) in one number so options can be
ranked. It assumes peak-hour full occupancy — every table rented and
every seat filled at once — at placeholder margins:

- table: $18/hr (typical hourly rental)
- drink seat: $9/hr (~1.5 drinks/hr at ~$6 margin)
- dining cover: $14/hr (~one cover turn/hr at ~$14 food margin)
- flex seat: the average of drink and dine ($11.50/hr) — a flex seat
  hosts ONE patron at a time, so it must not be counted as both
- spectator: $2/hr (incidental purchases)

It deliberately EXCLUDES labor, kitchen throughput, demand differences
between layouts, and service speed (scored separately as run lengths
and cue-crossing conflicts). Read it as "peak-hour gross capacity at
placeholder margins"; edit RATES in configs/v16_configs.py (or reweight
in the deck) and regenerate before deciding on revenue grounds.

**Other conventions** — cue swing: full >= 58" from the playfield edge,
playable-but-tight >= 54"; walking paths: < 36" clear is a pinch, < 24"
a fail, rounds measured at the 38" tucked-chair body; egress: 36" EE
frontage held clear, corridor pass >= 44"; service runs: Manhattan
routes door -> spine -> seat; capacities: a 60" round seats 8, a
two-top seats 2, four players per table.
