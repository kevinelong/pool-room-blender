#!/usr/bin/env python3
"""Build vote.html — the stakeholder ballot (split ranked choice).

Because the partition beam divides the hall into two rooms, every layout
is one of two families:
  * "4 in one room, 2 in the other"  (the Four On Top family)
  * "3 in each room"                 (the single-file lines)
Management may veto the 3-in-each-room family, so the ballot collects a
RANKED top-two in EACH family as a hedge — plus name and stakeholder
type. Submission composes an email to kevinelong@gmail.com via mailto:;
set ENDPOINT to a URL to POST JSON server-side instead (mailto stays the
fallback).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from configs.v16_configs import (  # noqa: E402
    CONFIGS, BEAM_Y, table_rect, tbl_rot,
)
from project_urls import HUB_URL  # noqa: E402

VOTE_EMAIL = "kevinelong@gmail.com"
# Set to a URL (e.g. https://vote.codeonline.io/poolroom) that accepts
# POST application/json to switch to server storage; mailto stays fallback.
ENDPOINT = ""

STAKEHOLDERS = ["VI Staff", "Tournament Director", "Pool Player",
                "Spectator", "Other"]


def room_split(cfg):
    """(north_count, south_count) of tables across the partition beam."""
    n = s = 0
    for _name, tx, ty in cfg["tables"]:
        _x0, y0, _x1, y1 = table_rect(tx, ty, tbl_rot(cfg, _name))
        if (y0 + y1) / 2 < BEAM_Y:
            n += 1
        else:
            s += 1
    return n, s


def families():
    four_two, three_three = [], []
    for c in CONFIGS:
        n, s = room_split(c)
        (four_two if max(n, s) == 4 else three_three).append(c)
    return four_two, three_three


def opts(cfgs, blank):
    out = [f'<option value="">{blank}</option>']
    for c in cfgs:
        name = c["name"].split("·", 1)[-1].strip()
        val = f'{c["letter"]} · {c["short"]}'
        out.append(f'<option value="{val}">{val} — {name}</option>')
    return "".join(out)


TPL = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Pool Room — Cast Your Vote</title>
<style>
  :root { --paper:#f7f6f2; --ink:#17171a; --muted:#6a6a70; --rule:#c9c7c0;
          --acc:#2e7d32; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
         display:flex; justify-content:center; padding:28px 14px 48px; }
  .frame { max-width:600px; width:100%; border:3px solid var(--ink);
           outline:1px solid var(--ink); outline-offset:5px;
           padding:clamp(20px,5vw,40px); display:flex;
           flex-direction:column; gap:22px; }
  h1 { margin:0; font-size:clamp(26px,6vw,40px); font-weight:900;
       text-align:center; letter-spacing:.02em; }
  .tag { font-family:ui-monospace,Menlo,monospace; font-size:11px;
         letter-spacing:.12em; color:var(--muted); text-align:center;
         text-transform:uppercase; margin:0; border-top:2px solid var(--ink);
         padding-top:10px; }
  .tag a { color:var(--muted); }
  fieldset { border:2px solid var(--ink); padding:14px 16px 16px;
             display:flex; flex-direction:column; gap:12px; margin:0; }
  legend { font-weight:900; font-size:15px; padding:0 8px; }
  .lede { font-size:13px; color:var(--muted); line-height:1.5; margin:0; }
  label { display:flex; flex-direction:column; gap:6px; font-weight:700;
          font-size:14px; }
  label .hint { font-weight:400; color:var(--muted); font-size:12px; }
  input, select, textarea, button {
    font:inherit; font-size:15px; padding:10px 12px; background:var(--paper);
    color:var(--ink); border:2px solid var(--ink); border-radius:0; }
  textarea { min-height:60px; resize:vertical; }
  button { font-weight:900; font-size:17px; cursor:pointer; padding:14px; }
  button:hover { background:var(--ink); color:var(--paper); }
  .err { color:#b22222; font-size:13px; font-weight:700; min-height:1em;
         margin:0; }
  #note { font-size:13px; color:var(--muted); line-height:1.5; margin:0; }
  #done { display:none; text-align:center; font-weight:700;
          color:var(--acc); }
</style>
</head>
<body>
<div class="frame">
  <h1>CAST YOUR VOTE</h1>
  <p class="tag">ranked · two families · <a href="__HUB_URL__">back to the
    hub</a></p>
  <form id="ballot" style="display:flex;flex-direction:column;gap:20px">
    <label>Your name
      <input id="name" required maxlength="60" placeholder="who's voting">
    </label>
    <label>What makes you most unique? <span class="hint">(pick the first
      that matches)</span>
      <select id="stakeholder" required>__STAKEHOLDERS__</select>
    </label>

    <fieldset>
      <legend>4 in one room, 2 in the other</legend>
      <p class="lede">The Four On Top family — a four-table cluster in one
        room, a pair in the other. Rank your top two.</p>
      <label>1st choice
        <select id="ft1" required>__FT__</select></label>
      <label>2nd choice <span class="hint">(optional)</span>
        <select id="ft2">__FT__</select></label>
    </fieldset>

    <fieldset>
      <legend>3 in each room</legend>
      <p class="lede">The single-file lines — three tables in each room.
        Management may not go for these, so rank your top two here too.</p>
      <label>1st choice
        <select id="tt1" required>__TT__</select></label>
      <label>2nd choice <span class="hint">(optional)</span>
        <select id="tt2">__TT__</select></label>
    </fieldset>

    <label>Anything else? <span class="hint">(optional)</span>
      <textarea id="comment" maxlength="500"
        placeholder="what swung it for you"></textarea>
    </label>
    <p class="err" id="err"></p>
    <button type="submit">Submit ballot</button>
    <p id="done">Ballot sent — thank you!</p>
    <p id="note">Submitting opens your email app with the ballot addressed
      to the organizer — just press send. (No account or login needed.)</p>
  </form>
</div>
<script>
"use strict";
const ENDPOINT = __ENDPOINT__;
const EMAIL = __EMAIL__;
const g = id => document.getElementById(id);
g("ballot").addEventListener("submit", ev => {
  ev.preventDefault();
  g("err").textContent = "";
  if (g("ft1").value && g("ft2").value && g("ft1").value === g("ft2").value){
    g("err").textContent = "Your two 4+2 choices must differ."; return; }
  if (g("tt1").value && g("tt2").value && g("tt1").value === g("tt2").value){
    g("err").textContent = "Your two 3+3 choices must differ."; return; }
  const ballot = {
    name: g("name").value.trim(),
    stakeholder: g("stakeholder").value,
    fourTwo: [g("ft1").value, g("ft2").value].filter(Boolean),
    threeThree: [g("tt1").value, g("tt2").value].filter(Boolean),
    comment: g("comment").value.trim(),
    ts: new Date().toISOString(),
  };
  const done = () => { g("done").style.display = "block"; };
  if (ENDPOINT){
    fetch(ENDPOINT, { method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(ballot) })
      .then(r => { if (!r.ok) throw 0; done(); })
      .catch(() => mailto(ballot, done));
  } else { mailto(ballot, done); }
});
function mailto(b, done){
  const rank = a => a.length ? a.map((v,i)=>`  ${i+1}. ${v}`).join("\n")
                             : "  (none)";
  const body = [
    "POOL ROOM BALLOT",
    "Name: " + b.name,
    "Stakeholder: " + b.stakeholder,
    "",
    "4 in one room, 2 in the other — ranked:",
    rank(b.fourTwo),
    "",
    "3 in each room — ranked:",
    rank(b.threeThree),
    "",
    "Comment: " + (b.comment || "(none)"),
    "Time: " + b.ts,
  ].join("\n");
  location.href = "mailto:" + EMAIL
    + "?subject=" + encodeURIComponent(
        "Pool Room vote: " + (b.fourTwo[0] || b.threeThree[0] || "ballot"))
    + "&body=" + encodeURIComponent(body);
  done();
}
</script>
</body>
</html>
"""


def main():
    four_two, three_three = families()
    stak = "".join(f"<option>{s}</option>" for s in STAKEHOLDERS)
    html = (TPL.replace("__STAKEHOLDERS__", stak)
               .replace("__FT__", opts(four_two, "— pick a 4+2 layout —"))
               .replace("__TT__", opts(three_three, "— pick a 3+3 layout —"))
               .replace("__HUB_URL__", HUB_URL)
               .replace("__ENDPOINT__", json.dumps(ENDPOINT))
               .replace("__EMAIL__", json.dumps(VOTE_EMAIL)))
    out = os.path.join(ROOT, "vote.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1e3:.0f} KB; "
          f"{len(four_two)} 4+2, {len(three_three)} 3+3)")


if __name__ == "__main__":
    main()
