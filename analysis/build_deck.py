#!/usr/bin/env python3
"""Assemble docs/decision_deck_v16.html — a self-contained decision deck.

Embeds the six plan PNGs (base64) and scorecards.json, and gives decision
makers weight sliders that re-rank the options live. Regenerate after any
config/analyzer change:  python3 analysis/build_deck.py
"""
import base64
import io
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

data = json.load(open(os.path.join(HERE, "scorecards.json")))
imgs = {}
for c in data["configs"]:
    p = os.path.join(ROOT, "renders", "plans", f"plan_v16_{c['key']}.png")
    imgs[c["key"]] = base64.b64encode(open(p, "rb").read()).decode()

# Eye-level Blender render per config (downscaled JPEG keeps the deck lean).
# Social is the built v15L3 model, so it uses the existing v15L3 render.
PERSP_SRC = {
    c["key"]: os.path.join(
        ROOT, "renders",
        "render_v15L3_persp_west_to_ME_5p5ft_annotated.png"
        if c["key"] == "social" else
        f"render_v16_{c['key']}_persp_west_to_ME_5p5ft_annotated.png")
    for c in data["configs"]
}
persps = {}
for key, p in PERSP_SRC.items():
    if not os.path.isfile(p) or os.path.getsize(p) < 2048:  # LFS pointer/missing
        continue
    im = Image.open(p).convert("RGB")
    im.thumbnail((1280, 720))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    persps[key] = base64.b64encode(buf.getvalue()).decode()

HTML = r"""<title>Pool Room v16 — Configuration Decision Deck</title>
<style>
:root {
  --paper: #f6f4ee; --ink: #232a30; --muted: #5d6a74; --line: #d9d4c8;
  --card: #fdfcf9; --felt: #3e8fc7; --felt-deep: #2c6e9e;
  --good: #3e9b6b; --warn: #b8860b; --fail: #c94f3d;
  --cocktail: #8a4fbf; --food: #cd7a1e; --bar-bg: #e7e2d6;
}
@media (prefers-color-scheme: dark) { :root {
  --paper: #1a2128; --ink: #e8e6e0; --muted: #93a0aa; --line: #323c46;
  --card: #212a33; --felt: #5aa6d8; --felt-deep: #7fbbe2;
  --good: #58b585; --warn: #d9a83f; --fail: #e07a68;
  --cocktail: #b07fe0; --food: #e09a4a; --bar-bg: #2a343e;
}}
:root[data-theme="dark"] {
  --paper: #1a2128; --ink: #e8e6e0; --muted: #93a0aa; --line: #323c46;
  --card: #212a33; --felt: #5aa6d8; --felt-deep: #7fbbe2;
  --good: #58b585; --warn: #d9a83f; --fail: #e07a68;
  --cocktail: #b07fe0; --food: #e09a4a; --bar-bg: #2a343e;
}
:root[data-theme="light"] {
  --paper: #f6f4ee; --ink: #232a30; --muted: #5d6a74; --line: #d9d4c8;
  --card: #fdfcf9; --felt: #3e8fc7; --felt-deep: #2c6e9e;
  --good: #3e9b6b; --warn: #b8860b; --fail: #c94f3d;
  --cocktail: #8a4fbf; --food: #cd7a1e; --bar-bg: #e7e2d6;
}
* { box-sizing: border-box; }
body {
  background: var(--paper); color: var(--ink);
  font-family: Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'Trebuchet MS', sans-serif;
  margin: 0; line-height: 1.5;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 28px 20px 80px; }
h1, h2, h3 { font-family: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif; text-wrap: balance; }
h1 { font-size: 2.1rem; margin: 0 0 4px; }
h2 { font-size: 1.45rem; margin: 42px 0 12px; border-bottom: 2px solid var(--felt); padding-bottom: 6px; }
.sub { color: var(--muted); margin: 0 0 8px; max-width: 65ch; }
.eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; color: var(--felt-deep); font-weight: 700; }
.num { font-variant-numeric: tabular-nums; }
.mixer { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 18px 20px; margin-top: 20px; }
.mixer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px 26px; margin-top: 10px; }
.slider label { display: flex; justify-content: space-between; font-size: .85rem; font-weight: 600; }
.slider input { width: 100%; accent-color: var(--felt); }
.presets { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.presets button {
  background: var(--bar-bg); color: var(--ink); border: 1px solid var(--line);
  border-radius: 20px; padding: 5px 14px; font: inherit; font-size: .82rem; cursor: pointer;
}
.presets button:hover, .presets button:focus-visible { border-color: var(--felt); outline: none; }
.rank { margin-top: 18px; display: flex; flex-direction: column; gap: 8px; }
.rank-row { display: grid; grid-template-columns: 2.2em 15em 1fr 3.5em; gap: 10px; align-items: center; }
.rank-row .medal { font-weight: 700; color: var(--muted); }
.rank-row .bar { background: var(--bar-bg); border-radius: 4px; height: 20px; overflow: hidden; }
.rank-row .bar > div { background: var(--felt); height: 100%; border-radius: 4px; transition: width .25s; }
.rank-row:first-child .bar > div { background: var(--felt-deep); }
.rank-row .score { text-align: right; font-weight: 700; }
table { border-collapse: collapse; width: 100%; font-size: .85rem; }
.tblwrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
th, td { padding: 7px 10px; text-align: right; border-bottom: 1px solid var(--line); white-space: nowrap; }
th:first-child, td:first-child { text-align: left; }
thead th { background: var(--bar-bg); position: sticky; top: 0; }
tbody tr:last-child td { border-bottom: none; }
td.good { color: var(--good); font-weight: 700; }
td.warn { color: var(--warn); font-weight: 700; }
td.fail { color: var(--fail); font-weight: 700; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; margin: 26px 0; overflow: hidden; }
.card img { width: 100%; height: auto; display: block; border-bottom: 1px solid var(--line); }
.card .body { padding: 16px 20px 20px; }
.card h3 { margin: 0 0 2px; font-size: 1.25rem; }
.card .tag { color: var(--muted); font-size: .9rem; margin-bottom: 12px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
.chip { background: var(--bar-bg); border-radius: 14px; padding: 3px 12px; font-size: .8rem; font-weight: 600; }
.chip b { color: var(--felt-deep); }
ul.notes { margin: 10px 0 0; padding-left: 20px; font-size: .9rem; }
ul.notes li { margin-bottom: 5px; max-width: 75ch; }
.method { font-size: .85rem; color: var(--muted); max-width: 72ch; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 5px; margin-right: 4px; }
</style>
<div class="wrap">
  <p class="eyebrow">Pool Room · 26'4" × 56'10" · v16 configuration study</p>
  <h1>Six ways to balance the room</h1>
  <p class="sub">Players, spectators, drinkers, eaters — and the two service
  streams that feed them: <span class="legend-dot" style="background:var(--cocktail)"></span>cocktails
  in through the Main Entry, <span class="legend-dot" style="background:var(--food)"></span>food
  in through the kitchen door. Every number below is computed from the room
  geometry, not estimated. Set the weights to what the house values; the
  ranking follows.</p>

  <div class="mixer">
    <p class="eyebrow">Weight mixer — what do we value?</p>
    <div class="mixer-grid" id="sliders"></div>
    <div class="presets" id="presets"></div>
    <div class="rank" id="rank"></div>
  </div>

  <h2>Comparison matrix</h2>
  <div class="tblwrap"><table id="matrix"></table></div>
  <p class="method">Cue swing: share of table sides with a full 58" clearance
  from the playfield edge (54–58" counts as tight, under 54" as blocked).
  Service runs are routed along the wall side of the east lane; a conflict is
  a seat whose delivery route crosses an active cue-swing zone. Exit corridor
  is the widest clear approach to the Emergency Exit (44" minimum to pass).
  Revenue proxy uses $18/hr per table, $9 per drink seat, $14 per dining
  cover, $11.50 per flex seat, $2 per spectator — adjust to the house's real
  numbers before deciding on revenue grounds.</p>

  <h2>The options</h2>
  <div id="cards"></div>
</div>
<script>
const DATA = __DATA_JSON__;
const IMGS = __IMGS_JSON__;
const PERSPS = __PERSPS_JSON__;

const DIMS = [
  { key: "players",    label: "Pool players",   raw: c => c.capacity.players },
  { key: "spectators", label: "Spectators",     raw: c => c.capacity.spectators },
  { key: "drinks",     label: "Drink service",  raw: c => c.capacity.drink + 0.5 * c.capacity.flex },
  { key: "dining",     label: "Food service",   raw: c => c.capacity.dine + 0.5 * c.capacity.flex },
  { key: "service",    label: "Service speed",  raw: c => -(c.service.cocktail.max_run_ft + c.service.food.max_run_ft
                                                    + 4 * (c.service.cocktail.conflicted_seats + c.service.food.conflicted_seats)) },
  { key: "flex",       label: "Flexibility",    raw: c => c.capacity.flex + Math.max(0, 45 - c.flip_minutes) },
  { key: "revenue",    label: "Revenue proxy",  raw: c => c.revenue_proxy_hr },
];
const PRESETS = {
  "Balanced":        { players: 5, spectators: 5, drinks: 5, dining: 5, service: 5, flex: 5, revenue: 5 },
  "Players first":   { players: 10, spectators: 3, drinks: 4, dining: 1, service: 3, flex: 2, revenue: 4 },
  "Revenue first":   { players: 3, spectators: 2, drinks: 7, dining: 7, service: 6, flex: 4, revenue: 10 },
  "Events & shows":  { players: 3, spectators: 10, drinks: 6, dining: 3, service: 4, flex: 8, revenue: 4 },
  "Ops simplicity":  { players: 4, spectators: 3, drinks: 5, dining: 5, service: 10, flex: 6, revenue: 4 },
};

// normalize each dimension 0..10 across configs
const scores = {};
for (const d of DIMS) {
  const vals = DATA.configs.map(d.raw);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  DATA.configs.forEach((c, i) => {
    (scores[c.key] = scores[c.key] || {})[d.key] = hi === lo ? 5 : 10 * (vals[i] - lo) / (hi - lo);
  });
}

const sliders = document.getElementById("sliders");
const weights = {};
for (const d of DIMS) {
  weights[d.key] = 5;
  const div = document.createElement("div");
  div.className = "slider";
  div.innerHTML = `<label for="w_${d.key}">${d.label}<span class="num" id="v_${d.key}">5</span></label>
    <input type="range" id="w_${d.key}" min="0" max="10" value="5">`;
  sliders.appendChild(div);
  div.querySelector("input").addEventListener("input", e => {
    weights[d.key] = +e.target.value;
    document.getElementById(`v_${d.key}`).textContent = e.target.value;
    render();
  });
}
const presets = document.getElementById("presets");
for (const [name, w] of Object.entries(PRESETS)) {
  const b = document.createElement("button");
  b.textContent = name;
  b.addEventListener("click", () => {
    for (const d of DIMS) {
      weights[d.key] = w[d.key];
      document.getElementById(`w_${d.key}`).value = w[d.key];
      document.getElementById(`v_${d.key}`).textContent = w[d.key];
    }
    render();
  });
  presets.appendChild(b);
}

function render() {
  const totalW = DIMS.reduce((s, d) => s + weights[d.key], 0) || 1;
  const ranked = DATA.configs.map(c => ({
    c, total: DIMS.reduce((s, d) => s + weights[d.key] * scores[c.key][d.key], 0) / totalW
  })).sort((a, b) => b.total - a.total);
  const max = ranked[0].total || 1;
  document.getElementById("rank").innerHTML = ranked.map((r, i) => `
    <div class="rank-row">
      <span class="medal num">${i + 1}.</span>
      <span>${r.c.name}</span>
      <div class="bar"><div style="width:${(100 * r.total / max).toFixed(1)}%"></div></div>
      <span class="score num">${r.total.toFixed(1)}</span>
    </div>`).join("");
}

// matrix
const fmt = (v, unit) => v ? v + (unit || "") : "—";
const rows = [
  ["Pool tables", c => c.capacity.tables],
  ["Player positions", c => c.capacity.players],
  ["Spectator seats", c => c.capacity.spectators],
  ["Drink positions", c => c.capacity.drink],
  ["Dining covers", c => c.capacity.dine],
  ["Flex seats", c => c.capacity.flex],
  ["Full cue swing", c => c.cue.full_pct + "%", c => c.cue.full_pct >= 95 ? "good" : c.cue.full_pct >= 80 ? "warn" : "fail"],
  ["Tightest swing", c => c.cue.min_clearance_in + '"', c => c.cue.min_clearance_in >= 58 ? "good" : c.cue.min_clearance_in >= 54 ? "warn" : "fail"],
  ["Cocktail run (max)", c => c.service.cocktail.seats ? c.service.cocktail.max_run_ft + " ft" : "—"],
  ["Food run (max)", c => c.service.food.seats ? c.service.food.max_run_ft + " ft" : "—"],
  ["Service × cue conflicts", c => c.service.cocktail.conflicted_seats + c.service.food.conflicted_seats,
     c => (c.service.cocktail.conflicted_seats + c.service.food.conflicted_seats) === 0 ? "good" : "fail"],
  ["Exit corridor", c => c.egress.exit_corridor_in + '"', c => c.egress.exit_corridor_ok ? "good" : "fail"],
  ["Revenue proxy", c => "$" + c.revenue_proxy_hr + "/hr"],
  ["Flip cost", c => c.flip_minutes + " min"],
];
let thead = "<thead><tr><th>Metric</th>" + DATA.configs.map(c =>
  `<th>${c.name.replace(/^\d+ · /, "")}</th>`).join("") + "</tr></thead><tbody>";
document.getElementById("matrix").innerHTML = thead + rows.map(([label, fn, cls]) =>
  `<tr><td>${label}</td>` + DATA.configs.map(c =>
    `<td class="num ${cls ? cls(c) : ""}">${fn(c)}</td>`).join("") + "</tr>"
).join("") + "</tbody>";

// option cards
document.getElementById("cards").innerHTML = DATA.configs.map(c => `
  <div class="card" id="opt-${c.key}">
    <img src="data:image/png;base64,${IMGS[c.key]}" alt="Annotated floor plan: ${c.name}" loading="lazy">
    ${PERSPS[c.key] ? `<img src="data:image/jpeg;base64,${PERSPS[c.key]}"
      alt="Eye-level render: ${c.name} seen from the Main Entry sight line" loading="lazy">` : ""}
    <div class="body">
      <h3>${c.name}</h3>
      <div class="tag">${c.tagline}</div>
      <div class="chips">
        <span class="chip"><b>${c.capacity.tables}</b> tables</span>
        <span class="chip"><b>${c.capacity.players}</b> players</span>
        <span class="chip"><b>${c.capacity.spectators}</b> spectators</span>
        <span class="chip"><b>${c.capacity.drink}</b> drink</span>
        <span class="chip"><b>${c.capacity.dine}</b> dine</span>
        <span class="chip"><b>${c.capacity.flex}</b> flex</span>
        <span class="chip"><b>$${c.revenue_proxy_hr}</b>/hr proxy</span>
      </div>
      <ul class="notes">${c.notes.map(n => `<li>${n}</li>`).join("")}</ul>
    </div>
  </div>`).join("");

render();
</script>
"""


def main():
    html = (HTML
            .replace("__DATA_JSON__", json.dumps(data))
            .replace("__IMGS_JSON__", json.dumps(imgs))
            .replace("__PERSPS_JSON__", json.dumps(persps)))
    out = os.path.join(ROOT, "docs", "decision_deck_v16.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
