# v16 configuration scorecards

| Config | Tables | Players | Drink | Dine | Flex | Cue full% | Min clr" | Cocktail max run | Food max run | Svc conflicts | Egress worst | Path min" | $/hr proxy | Flip min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A · Four On Top — Turned Left | 6 | 24 | 0 | 0 | 14 | 62% | 37.2 | 72.8 ft | 46.4 ft | 9 | 61.8 ft | 44.0 | $221 | 15 |
| B · West Line + Wall Rounds | 6 | 24 | 0 | 0 | 48 | 50% | 49.0 | 59.0 ft | 36.7 ft | 0 | 52.6 ft | 25.0 | $612 | 25 |
| C · West Line — Shifted Down | 6 | 24 | 0 | 0 | 48 | 42% | 41.0 | 58.6 ft | 34.9 ft | 0 | 55.7 ft | 25.1 | $612 | 25 |
| D · Four On Top | 6 | 24 | 0 | 0 | 62 | 67% | 56.5 | 67.6 ft | 52.0 ft | 12 | 58.8 ft | 52.5 | $773 | 0 |
| E · Four On Top — Turned | 6 | 24 | 0 | 0 | 14 | 62% | 46.8 | 72.0 ft | 46.6 ft | 9 | 61.0 ft | 44.0 | $221 | 15 |
| F · Center Line | 6 | 24 | 24 | 0 | 0 | 58% | 54.8 | 70.0 ft | 0.0 ft | 12 | 56.6 ft | 47.5 | $276 | 0 |
| G · Four On Top — Turned Right | 6 | 24 | 0 | 0 | 14 | 62% | 37.2 | 93.7 ft | 66.8 ft | 9 | 59.5 ft | 40.0 | $221 | 15 |
| H · East Line + West Lounge | 6 | 24 | 0 | 0 | 48 | 58% | 54.8 | 68.2 ft | 46.8 ft | 12 | 54.9 ft | 41.2 | $612 | 20 |
| I · East Line — Shifted Down | 6 | 24 | 0 | 0 | 48 | 50% | 43.0 | 71.0 ft | 44.0 ft | 12 | 57.7 ft | 47.5 | $612 | 20 |

## Impact at a glance (− negative · neutral + positive)

| Layout | Play room | Hospitality $ | Service | Walkability | Entry/egress | Flip |
|---|---|---|---|---|---|---|
| A · Four On Top — Turned Left | − | − | · | · | + | · |
| B · West Line + Wall Rounds | − | + | + | · | + | − |
| C · West Line — Shifted Down | − | + | + | · | + | − |
| D · Four On Top | + | + | − | · | + | + |
| E · Four On Top — Turned | · | − | · | · | + | · |
| F · Center Line | · | − | − | + | + | + |
| G · Four On Top — Turned Right | − | − | · | · | + | · |
| H · East Line + West Lounge | · | + | − | + | − | − |
| I · East Line — Shifted Down | − | + | − | + | + | − |

## Walking-path anomalies (clear width < 36")

- **A · Four On Top — Turned Left** — narrowest walk 44.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
- **B · West Line + Wall Rounds** — narrowest walk 25.0":
    - pinch: 25.0" (center-east: between a round's chairs and a round's chairs)
- **C · West Line — Shifted Down** — narrowest walk 25.1":
    - pinch: 25.1" (center-east: between a round's chairs and a round's chairs)
- **D · Four On Top** — narrowest walk 52.5":
    - blocked: 0.0" (center-east: walk crosses a wall two-top)
- **E · Four On Top — Turned** — narrowest walk 44.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
- **F · Center Line** — none; narrowest walk 47.5"
- **G · Four On Top — Turned Right** — narrowest walk 40.0":
    - blocked: 0.0" (south-center: walk crosses a wall two-top)
- **H · East Line + West Lounge** — none; narrowest walk 41.2"
- **I · East Line — Shifted Down** — none; narrowest walk 47.5"

## Methodology & assumptions

**Revenue proxy** — a *comparator*, not a forecast. Every option has the
same six tables, so table rent is constant across the set; the proxy
exists to price the HOSPITALITY differences (drink seats vs dining
covers vs flex seats) in one number so options can be
ranked. It assumes peak-hour full occupancy — every table rented and
every seat filled at once — at placeholder margins:

- table: $10/hr rental
- drink seat: $9/hr (~1.5 drinks/hr at margin)
- dining cover: $14/hr (~one cover turn/hr at margin)
- flex seat: the average of drink and dine — a flex seat hosts ONE
  patron at a time, so it must not be counted as both

It deliberately EXCLUDES labor, kitchen throughput, demand differences
between layouts, and service speed (scored separately as run lengths
and cue-crossing conflicts). Read it as "peak-hour gross capacity at
placeholder margins"; edit RATES in configs/v16_configs.py (or reweight
in the deck) and regenerate before deciding on revenue grounds.

**Impact grid** — "+" / "·" / "−" per area, from fixed thresholds:
play room + at full-swing >= 65% of sides (− under 55% or tightest
< 44"); hospitality + at proxy >= $600/hr (− under $300); service + at
zero cue-crossing conflicts and food runs <= 45 ft (− at 10+ conflicts);
walkability + at no anomalies and narrowest walk >= 38" (− at any FAIL
or < 24"); entry/egress − when a compromise is flagged at the entry or
exit approach; flip + at <= 5 minutes (− at >= 20).

**Other conventions** — cue swing: full >= 58" from the playfield edge,
playable-but-tight >= 54"; walking paths: < 36" clear is a pinch, < 24"
a fail, rounds measured at the 38" tucked-chair body; egress: 36" EE
frontage held clear, corridor pass >= 44"; service runs: Manhattan
routes door -> spine -> seat; capacities: a 60" round seats 8, a
two-top seats 2, four players per table.
