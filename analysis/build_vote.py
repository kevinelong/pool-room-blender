#!/usr/bin/env python3
"""Build vote.html — the stakeholder ballot.

Collects a name, a stakeholder type ("what makes you most unique —
first match"), a layout vote (A–M, generated from the configs), and an
optional comment. Submission today composes an email to
kevinelong@gmail.com via mailto:. The page is already wired for a
server endpoint: set ENDPOINT below (a URL that accepts a JSON POST)
and rebuilds switch every ballot to server storage with mailto as the
fallback.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from configs.v16_configs import CONFIGS  # noqa: E402
from project_urls import HUB_URL  # noqa: E402

VOTE_EMAIL = "kevinelong@gmail.com"
# Set to a URL (e.g. https://vote.codeonline.io/poolroom) that accepts
# POST application/json {name, stakeholder, layout, comment, ts} to
# switch storage server-side; mailto remains the fallback.
ENDPOINT = ""

STAKEHOLDERS = ["VI Staff", "Tournament Director", "Pool Player",
                "Spectator", "Other"]

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
  .frame { max-width:560px; width:100%; border:3px solid var(--ink);
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
  label { display:flex; flex-direction:column; gap:6px; font-weight:700;
          font-size:14px; }
  label .hint { font-weight:400; color:var(--muted); font-size:12px; }
  input, select, textarea, button {
    font:inherit; font-size:15px; padding:10px 12px; background:var(--paper);
    color:var(--ink); border:2px solid var(--ink); border-radius:0; }
  textarea { min-height:70px; resize:vertical; }
  button { font-weight:900; font-size:17px; cursor:pointer; padding:14px; }
  button:hover { background:var(--ink); color:var(--paper); }
  #note { font-size:13px; color:var(--muted); line-height:1.5; margin:0; }
  #done { display:none; text-align:center; font-weight:700;
          color:var(--acc); }
</style>
</head>
<body>
<div class="frame">
  <h1>CAST YOUR VOTE</h1>
  <p class="tag">one ballot per person · <a href="__HUB_URL__">back to the
    hub</a></p>
  <form id="ballot">
    <div style="display:flex;flex-direction:column;gap:18px">
      <label>Your name
        <input id="name" required maxlength="60" placeholder="who's voting">
      </label>
      <label>What makes you most unique? <span class="hint">(pick the
        first that matches)</span>
        <select id="stakeholder" required>__STAKEHOLDERS__</select>
      </label>
      <label>Your layout vote
        <select id="layout" required>__LAYOUTS__</select>
      </label>
      <label>Anything else? <span class="hint">(optional)</span>
        <textarea id="comment" maxlength="500"
          placeholder="what swung it for you"></textarea>
      </label>
      <button type="submit">Submit ballot</button>
      <p id="done">Ballot sent — thank you!</p>
      <p id="note">Submitting opens your email app with the ballot
        addressed to the organizer — just press send. (No account or
        login needed.)</p>
    </div>
  </form>
</div>
<script>
"use strict";
const ENDPOINT = __ENDPOINT__;
const EMAIL = __EMAIL__;
document.getElementById("ballot").addEventListener("submit", ev => {
  ev.preventDefault();
  const ballot = {
    name: document.getElementById("name").value.trim(),
    stakeholder: document.getElementById("stakeholder").value,
    layout: document.getElementById("layout").value,
    comment: document.getElementById("comment").value.trim(),
    ts: new Date().toISOString(),
  };
  const finish = () => {
    document.getElementById("done").style.display = "block";
  };
  if (ENDPOINT) {
    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ballot),
    }).then(r => { if (!r.ok) throw 0; finish(); })
      .catch(() => mailtoFallback(ballot, finish));
  } else {
    mailtoFallback(ballot, finish);
  }
});
function mailtoFallback(b, done){
  const body = [
    "POOL ROOM BALLOT",
    "Name: " + b.name,
    "Stakeholder: " + b.stakeholder,
    "Vote: " + b.layout,
    "Comment: " + (b.comment || "(none)"),
    "Time: " + b.ts,
  ].join("\n");
  location.href = "mailto:" + EMAIL
    + "?subject=" + encodeURIComponent("Pool Room vote: " + b.layout)
    + "&body=" + encodeURIComponent(body);
  done();
}
</script>
</body>
</html>
"""


def main():
    stak = "".join(f"<option>{s}</option>" for s in STAKEHOLDERS)
    lays = "".join(
        f'<option value="{c["letter"]} · {c["short"]}">'
        f'{c["letter"]} · {c["short"]} — {c["name"].split("·", 1)[-1].strip()}'
        f"</option>" for c in CONFIGS)
    html = (TPL.replace("__STAKEHOLDERS__", stak)
               .replace("__LAYOUTS__", lays)
               .replace("__HUB_URL__", HUB_URL)
               .replace("__ENDPOINT__", json.dumps(ENDPOINT))
               .replace("__EMAIL__", json.dumps(VOTE_EMAIL)))
    out = os.path.join(ROOT, "vote.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1e3:.0f} KB, "
          f"{len(CONFIGS)} layout options)")


if __name__ == "__main__":
    main()
