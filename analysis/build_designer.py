#!/usr/bin/env python3
"""Build design.html — the "design your own layout" page.

Start from any of the fourteen study layouts, then drag pieces around the
room, rotate them, add and remove them. Positions snap to 6-inch
increments and rotations to 45 degrees (snap on by default, toggleable).
Designs are named and saved in the browser (localStorage) and can be
exported/imported as small JSON files for sharing.

The fourteen templates are generated straight from configs/v16_configs.py,
so they are exactly the study layouts. Room fixtures (doors, entry
well, beam, HVAC) are fixed scenery. Same paper-and-ink visual language
as the hub and print poster.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from configs.v16_configs import (  # noqa: E402
    CONFIGS, ROOM_W, ROOM_L, BEAM_Y, HVAC, ENTRY_WELL, table_rect,
    tbl_rot,
)
from project_urls import HUB_URL  # noqa: E402

# Cloud store (Node route on codeonline.io). Designs POST/GET here keyed by
# an anonymous per-browser token (X-Client-Token); a token the server has
# flagged in POOLROOM_ADMIN_TOKENS sees every account's designs. Set to ""
# to hide the cloud panel entirely (local save always works).
DESIGNS_API = "https://codeonline.io/api/poolroom/designs"


def elements_for(cfg):
    els = []
    for _n, tx, ty in cfg["tables"]:
        trot = tbl_rot(cfg, _n)
        x0, y0, x1, y1 = table_rect(tx, ty, trot)
        els.append(dict(t="table", x=round((x0 + x1) / 2, 1),
                        y=round((y0 + y1) / 2, 1), rot=90 if trot else 0))
    plus = {(round(px, 1), round(py, 1))
            for px, py in cfg.get("rounds_plus", [])}
    for cx, cy in cfg.get("rounds", []):
        isplus = (round(cx, 1), round(cy, 1)) in plus
        els.append(dict(t="round", x=round(cx, 1), y=round(cy, 1),
                        rot=0 if isplus else 45))
    for hx, hy in list(cfg.get("hightops", [])) + list(cfg.get("twotops", [])):
        ns = hy < 40 or hy > ROOM_L - 40
        els.append(dict(t="top", x=round(hx, 1), y=round(hy, 1),
                        rot=90 if ns else 0))
    return els


TPL = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Pool Room — Design Your Own Layout</title>
<style>
  :root { --paper:#f7f6f2; --ink:#17171a; --muted:#6a6a70; --rule:#c9c7c0;
          --acc:#2e7d32; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }
  header { text-align:center; padding:14px 10px 4px; }
  h1 { margin:0; font-size:clamp(20px,4.5vw,30px); font-weight:900;
       letter-spacing:.02em; }
  .tag { font-family:ui-monospace,Menlo,monospace; font-size:11px;
         letter-spacing:.12em; color:var(--muted); text-transform:uppercase;
         margin:4px 0 0; }
  .tag a { color:var(--muted); }
  .app { display:flex; gap:14px; justify-content:center; align-items:flex-start;
         padding:10px; flex-wrap:wrap; }
  .panel { width:250px; display:flex; flex-direction:column; gap:12px; }
  .box { border:2px solid var(--ink); padding:10px 12px; background:var(--paper);
         display:flex; flex-direction:column; gap:8px; }
  .box h2 { margin:0; font-size:11px; font-family:ui-monospace,Menlo,monospace;
            letter-spacing:.16em; text-transform:uppercase; color:var(--muted);
            font-weight:700; }
  button, select, input[type=text] {
    font:inherit; font-size:14px; padding:7px 10px; background:var(--paper);
    color:var(--ink); border:2px solid var(--ink); border-radius:0;
    cursor:pointer; }
  button:hover { background:var(--ink); color:var(--paper); }
  button:disabled { opacity:.35; cursor:default; }
  button:disabled:hover { background:var(--paper); color:var(--ink); }
  .row { display:flex; gap:6px; }
  .row > * { flex:1; }
  label.chk { display:flex; align-items:center; gap:8px; font-size:14px;
              cursor:pointer; user-select:none; }
  input[type=checkbox] { width:17px; height:17px; accent-color:var(--ink); }
  #cwrap { border:3px solid var(--ink); outline:1px solid var(--ink);
           outline-offset:4px; line-height:0; background:var(--paper);
           margin:5px; }
  canvas { touch-action:none; cursor:grab; }
  canvas.dragging { cursor:grabbing; }
  #status { font-family:ui-monospace,Menlo,monospace; font-size:11.5px;
            color:var(--muted); min-height:2.6em; line-height:1.3; }
  .help { font-size:12px; color:var(--muted); line-height:1.45; margin:0; }
  kbd { font-family:ui-monospace,Menlo,monospace; border:1px solid var(--rule);
        padding:0 4px; border-radius:3px; font-size:11px; }
  #savedSel { max-width:100%; }
  .hidden { display:none; }
</style>
</head>
<body>
<header>
  <h1>DESIGN YOUR OWN LAYOUT</h1>
  <p class="tag">drag · rotate · add · remove — snapped to 6&Prime; and 45&deg;
    · <a href="__HUB_URL__">back to the hub</a></p>
</header>
<div class="app">
  <div id="cwrap"><canvas id="cv"></canvas></div>
  <div class="panel">
    <div class="box">
      <h2>Start from</h2>
      <select id="tplSel"></select>
      <button id="resetBtn">Reset to this layout</button>
    </div>
    <div class="box">
      <h2>Pieces</h2>
      <div class="row">
        <button id="addTable">+ Table</button>
        <button id="addRound">+ Round</button>
        <button id="addTop">+ Two-top</button>
      </div>
      <div class="row">
        <button id="rotBtn" disabled>&#10227; Rotate 45&deg;</button>
        <button id="delBtn" disabled>&#10005; Remove</button>
      </div>
      <label class="chk"><input type="checkbox" id="snapChk" checked>
        Snap to 6&Prime; grid &amp; 45&deg;</label>
    </div>
    <div class="box">
      <h2>Your design</h2>
      <input type="text" id="nameInp" placeholder="name this variation"
             maxlength="40">
      <button id="saveBtn">Save in this browser</button>
      <select id="savedSel"></select>
      <div class="row">
        <button id="loadBtn">Load</button>
        <button id="delSavedBtn">Delete</button>
      </div>
      <div class="row">
        <button id="exportBtn">Export file</button>
        <button id="importBtn">Import file</button>
      </div>
      <input type="file" id="importInp" accept=".json,application/json"
             class="hidden">
    </div>
    <div class="box" id="cloudBox">
      <h2>My saved designs</h2>
      <button id="cloudSaveBtn">Save to my account</button>
      <select id="cloudSel"></select>
      <div class="row">
        <button id="cloudLoadBtn" disabled>Load</button>
        <button id="cloudDelBtn" disabled>Delete</button>
      </div>
      <div id="cloudMsg" class="help"></div>
      <p class="help" id="idLine" style="word-break:break-all">This device's
        ID: <code id="cid">…</code>
        <button id="copyIdBtn" style="padding:1px 7px;font-size:11px;flex:0">
          copy</button></p>
    </div>
    <div class="box">
      <h2>Status</h2>
      <div id="status"></div>
      <p class="help">Drag a piece to move it. <kbd>R</kbd> or the button
        rotates 45&deg;. <kbd>Del</kbd> removes. Arrow keys nudge 6&Prime;.
        Doors, entry steps, beam and the HVAC chase are part of the room and
        stay put.</p>
    </div>
  </div>
</div>
<script>
"use strict";
const DATA = __DATA__;
window.DATA = DATA;                       // for tests/debugging
const R = DATA.room;
const INK = "#17171a", PAPER = "#f7f6f2", MUTED = "#6a6a70", ACC = "#2e7d32";
const STORE = "poolRoomDesigns.v1", WORK = "poolRoomWork.v1";
const API = __DESIGNS_API__;              // cloud store; "" hides the panel
const CLIENT_KEY = "poolRoomClientId.v1"; // anonymous per-browser identity
const EXT = { table:[26.75,46.25], round:[46,46], top:[11,22] };

let cloudAdmin = false;
function clientId(){
  let id = localStorage.getItem(CLIENT_KEY);
  if (!id){
    id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
       : "id-" + Date.now().toString(36) + Math.random().toString(36).slice(2);
    localStorage.setItem(CLIENT_KEY, id);
  }
  return id;
}

const cv = document.getElementById("cv"), ctx = cv.getContext("2d");
const dpr = window.devicePixelRatio || 1;
let s = 1, base = "social", els = [], sel = -1, dirty = false;
let drag = null;

function tplByKey(k){ return DATA.layouts.find(l => l.key === k); }
function clone(o){ return JSON.parse(JSON.stringify(o)); }
function snapOn(){ return document.getElementById("snapChk").checked; }
function snapPos(v){ return snapOn() ? Math.round(v / 6) * 6 : Math.round(v * 2) / 2; }

function fit(){
  const maxH = Math.max(420, window.innerHeight - 150);
  const maxW = Math.min(document.documentElement.clientWidth - 30, 560);
  s = Math.min(maxW / R.w, maxH / R.l);
  cv.width = Math.round(R.w * s * dpr);
  cv.height = Math.round(R.l * s * dpr);
  cv.style.width = (R.w * s) + "px";
  cv.style.height = (R.l * s) + "px";
  draw();
}

function Y(v){ return R.l - v; }   // image-top = south, like every drawing

function extents(e){                // rotated half-extents for clamp/hit box
  const [hw, hl] = EXT[e.t];
  const a = e.rot * Math.PI / 180;
  const c = Math.abs(Math.cos(a)), n = Math.abs(Math.sin(a));
  return [hw * c + hl * n, hw * n + hl * c];
}

function clampEl(e){
  const [ex, ey] = extents(e);
  e.x = Math.min(Math.max(e.x, ex), R.w - ex);
  e.y = Math.min(Math.max(e.y, ey), R.l - ey);
}

function drawRoom(){
  ctx.fillStyle = PAPER;
  ctx.fillRect(0, 0, R.w, R.l);
  ctx.strokeStyle = INK; ctx.lineWidth = 3;
  ctx.strokeRect(1.5, 1.5, R.w - 3, R.l - 3);
  ctx.fillStyle = INK;
  ctx.fillRect(30, Y(682), 65, 4);            // emergency exit (south)
  ctx.fillRect(R.w - 4, Y(330), 4, 40);       // kitchen (east)
  ctx.fillRect(276, Y(4), 36, 4);             // storage A (north)
  ctx.fillRect(R.w - 4, Y(40), 4, 36);        // storage B (east)
  // entry well: sunken channel along the S wall, treads at the west end
  ctx.lineWidth = 1;
  const wd = R.well[3] - R.well[1];
  ctx.strokeRect(R.well[0], Y(R.well[3]) + 1, R.w - R.well[0] - 1, wd - 1);
  for (const tx of [R.well[0] + 11, R.well[0] + 22]){
    ctx.beginPath(); ctx.moveTo(tx, Y(R.well[3]) + 1);
    ctx.lineTo(tx, Y(R.well[1])); ctx.stroke();
  }
  // beam
  ctx.save();
  ctx.setLineDash([10, 8]); ctx.lineWidth = 1; ctx.strokeStyle = MUTED;
  ctx.beginPath(); ctx.moveTo(2, Y(R.beamY)); ctx.lineTo(R.w - 2, Y(R.beamY));
  ctx.stroke();
  ctx.restore();
  // hvac chase
  ctx.lineWidth = 1.2;
  ctx.strokeRect(R.hvac[0], Y(R.hvac[3]), R.hvac[2] - R.hvac[0],
                 R.hvac[3] - R.hvac[1]);
  ctx.beginPath();
  ctx.moveTo(R.hvac[0], Y(R.hvac[1])); ctx.lineTo(R.hvac[2], Y(R.hvac[3]));
  ctx.stroke();
  // labels
  ctx.fillStyle = MUTED;
  ctx.font = "9px ui-monospace, Menlo, monospace";
  ctx.textAlign = "center";
  ctx.fillText("ENTRY", (R.well[0] + 22 + R.w) / 2,
               Y((R.well[1] + R.well[3]) / 2) + 3);
  ctx.fillText("EXIT", 62, Y(668));
  ctx.fillText("HVAC", (R.hvac[0] + R.hvac[2]) / 2, Y((R.hvac[1] + R.hvac[3]) / 2) + 3);
  ctx.save();
  ctx.translate(R.w - 9, Y(310)); ctx.rotate(-Math.PI / 2);
  ctx.fillText("KITCHEN", 0, 3);
  ctx.restore();
  ctx.fillText("STORAGE", 294, Y(14));
}

function drawEl(e, isSel){
  ctx.save();
  ctx.translate(e.x, Y(e.y));
  ctx.rotate(e.rot * Math.PI / 180);
  ctx.strokeStyle = INK;
  if (e.t === "table"){
    ctx.lineWidth = 2.2;
    ctx.strokeRect(-26.75, -46.25, 53.5, 92.5);
    ctx.lineWidth = 0.8;
    ctx.strokeRect(-19.5, -39, 39, 78);
  } else if (e.t === "round"){
    ctx.lineWidth = 2.2;
    ctx.beginPath(); ctx.arc(0, 0, 30, 0, Math.PI * 2); ctx.stroke();
    ctx.lineWidth = 0.8;
    for (const [cx, cy] of [[0, -40], [40, 0], [0, 40], [-40, 0]])
      ctx.strokeRect(cx - 6, cy - 6, 12, 12);
  } else {
    ctx.lineWidth = 1.6;
    ctx.strokeRect(-11, -14, 22, 28);
    ctx.lineWidth = 0.8;
    for (const sy of [-16, 16]){
      ctx.beginPath(); ctx.arc(0, sy, 6, 0, Math.PI * 2); ctx.stroke();
    }
  }
  if (isSel){
    const [hw, hl] = EXT[e.t];
    ctx.strokeStyle = ACC; ctx.lineWidth = 1.4;
    ctx.setLineDash([5, 4]);
    ctx.strokeRect(-hw - 5, -hl - 5, hw * 2 + 10, hl * 2 + 10);
  }
  ctx.restore();
}

function draw(){
  ctx.setTransform(dpr * s, 0, 0, dpr * s, 0, 0);
  ctx.clearRect(0, 0, R.w, R.l);
  drawRoom();
  els.forEach((e, i) => drawEl(e, i === sel));
  status_();
}

function status_(){
  const n = { table:0, round:0, top:0 };
  els.forEach(e => n[e.t]++);
  let txt = n.table + " tables · " + n.round + " rounds · " + n.top +
            " two-tops";
  if (sel >= 0){
    const e = els[sel];
    const name = { table:"Pool table", round:"60″ round",
                   top:"Two-top" }[e.t];
    txt += "\n" + name + " at (" + e.x + "″, " + e.y + "″) · " +
           (e.rot % 360) + "°";
  }
  document.getElementById("status").innerText = txt;
  document.getElementById("rotBtn").disabled = sel < 0;
  document.getElementById("delBtn").disabled = sel < 0;
}

function hitTest(mx, my){            // mx,my in room inches (screen-y)
  for (let i = els.length - 1; i >= 0; i--){
    const e = els[i];
    const dx = mx - e.x, dy = my - Y(e.y);
    const a = -e.rot * Math.PI / 180;
    const lx = dx * Math.cos(a) - dy * Math.sin(a);
    const ly = dx * Math.sin(a) + dy * Math.cos(a);
    if (e.t === "round"){ if (Math.hypot(lx, ly) <= 46) return i; }
    else {
      const [hw, hl] = EXT[e.t];
      if (Math.abs(lx) <= hw + 3 && Math.abs(ly) <= hl + 3) return i;
    }
  }
  return -1;
}

function ptr(ev){
  const r = cv.getBoundingClientRect();
  return [(ev.clientX - r.left) / s, (ev.clientY - r.top) / s];
}

cv.addEventListener("pointerdown", ev => {
  const [mx, my] = ptr(ev);
  const i = hitTest(mx, my);
  sel = i;
  if (i >= 0){
    const e = els[i];
    drag = { ox: mx - e.x, oy: my - Y(e.y) };
    cv.setPointerCapture(ev.pointerId);
    cv.classList.add("dragging");
  }
  draw();
});
cv.addEventListener("pointermove", ev => {
  if (!drag || sel < 0) return;
  const [mx, my] = ptr(ev);
  const e = els[sel];
  e.x = snapPos(mx - drag.ox);
  e.y = snapPos(R.l - (my - drag.oy));
  clampEl(e);
  markDirty();
  draw();
});
function endDrag(){ drag = null; cv.classList.remove("dragging"); }
cv.addEventListener("pointerup", endDrag);
cv.addEventListener("pointercancel", endDrag);

document.addEventListener("keydown", ev => {
  if (ev.target.tagName === "INPUT" || ev.target.tagName === "SELECT") return;
  if (sel < 0) return;
  const e = els[sel];
  const step = snapOn() ? 6 : 1;
  let used = true;
  if (ev.key === "r" || ev.key === "R") rotateSel();
  else if (ev.key === "Delete" || ev.key === "Backspace") removeSel();
  else if (ev.key === "ArrowLeft")  e.x -= step;
  else if (ev.key === "ArrowRight") e.x += step;
  else if (ev.key === "ArrowUp")    e.y += step;   // up on screen = south
  else if (ev.key === "ArrowDown")  e.y -= step;
  else used = false;
  if (used){ ev.preventDefault(); clampEl(e); markDirty(); draw(); }
});

function rotateSel(){
  if (sel < 0) return;
  const e = els[sel];
  e.rot = (e.rot + 45) % 360;
  if (!snapOn()) e.rot = e.rot; // rotation is always 45-degree steps
  clampEl(e); markDirty(); draw();
}
function removeSel(){
  if (sel < 0) return;
  els.splice(sel, 1); sel = -1; markDirty(); draw();
}
function addEl(t){
  const e = { t, x: snapPos(R.w / 2), y: snapPos(R.l / 2), rot: 0 };
  clampEl(e); els.push(e); sel = els.length - 1; markDirty(); draw();
}

function markDirty(){ dirty = true; saveWork(); }
function saveWork(){
  localStorage.setItem(WORK, JSON.stringify(
    { base, els, name: document.getElementById("nameInp").value }));
}

function loadTemplate(key, confirmFirst){
  if (confirmFirst && dirty &&
      !confirm("Replace your current design with the template?")) {
    document.getElementById("tplSel").value = base;
    return;
  }
  base = key;
  els = clone(tplByKey(key).els);
  sel = -1; dirty = false; saveWork(); draw();
}

// ------- saved designs (localStorage) -------
function savedAll(){
  try { return JSON.parse(localStorage.getItem(STORE) || "{}"); }
  catch(e){ return {}; }
}
function refreshSaved(selName){
  const all = savedAll();
  const selEl = document.getElementById("savedSel");
  const names = Object.keys(all).sort();
  selEl.innerHTML = names.length
    ? names.map(n => `<option>${n.replace(/</g, "&lt;")}</option>`).join("")
    : "<option value=''>(no saved designs yet)</option>";
  if (selName) selEl.value = selName;
  const has = names.length > 0;
  document.getElementById("loadBtn").disabled = !has;
  document.getElementById("delSavedBtn").disabled = !has;
}
document.getElementById("saveBtn").onclick = () => {
  let name = document.getElementById("nameInp").value.trim();
  if (!name){ name = prompt("Name this variation:", "my layout") || ""; }
  name = name.trim();
  if (!name) return;
  document.getElementById("nameInp").value = name;
  const all = savedAll();
  all[name] = { base, els: clone(els), saved: new Date().toISOString() };
  localStorage.setItem(STORE, JSON.stringify(all));
  dirty = false; saveWork(); refreshSaved(name);
  document.getElementById("status").innerText =
    "Saved “" + name + "” in this browser.";
};
document.getElementById("loadBtn").onclick = () => {
  const name = document.getElementById("savedSel").value;
  const d = savedAll()[name];
  if (!d) return;
  base = d.base; els = clone(d.els); sel = -1; dirty = false;
  document.getElementById("nameInp").value = name;
  document.getElementById("tplSel").value = base;
  saveWork(); draw();
};
document.getElementById("delSavedBtn").onclick = () => {
  const name = document.getElementById("savedSel").value;
  if (!name || !confirm("Delete saved design “" + name + "”?")) return;
  const all = savedAll(); delete all[name];
  localStorage.setItem(STORE, JSON.stringify(all));
  refreshSaved();
};

// ------- export / import -------
document.getElementById("exportBtn").onclick = () => {
  const name = (document.getElementById("nameInp").value.trim() || "layout");
  const blob = new Blob([JSON.stringify(
    { app: "pool-room-designer", v: 1, name, base, els }, null, 1)],
    { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name.replace(/[^\w.-]+/g, "_") + ".poolroom.json";
  a.click();
  URL.revokeObjectURL(a.href);
};
document.getElementById("importBtn").onclick = () =>
  document.getElementById("importInp").click();
document.getElementById("importInp").onchange = ev => {
  const f = ev.target.files[0];
  if (!f) return;
  f.text().then(txt => {
    try {
      const d = JSON.parse(txt);
      if (!Array.isArray(d.els)) throw 0;
      base = tplByKey(d.base) ? d.base : base;
      els = d.els.filter(e => EXT[e.t]).map(e => (
        { t: e.t, x: +e.x || 0, y: +e.y || 0, rot: (+e.rot || 0) % 360 }));
      els.forEach(clampEl);
      sel = -1; dirty = true;
      document.getElementById("nameInp").value = d.name || "";
      document.getElementById("tplSel").value = base;
      saveWork(); draw();
    } catch(e){ alert("That file doesn't look like a saved layout."); }
  });
  ev.target.value = "";
};

// ------- cloud store (server, keyed by anonymous token) -------
function esc(s){ return String(s).replace(/[<>&]/g,
  c => ({ "<":"&lt;", ">":"&gt;", "&":"&amp;" }[c])); }
function cloudMsg(t){ document.getElementById("cloudMsg").innerText = t || ""; }
function apiHeaders(){
  return { "Content-Type":"application/json", "X-Client-Token": clientId() };
}
function cloudBtns(on){
  document.getElementById("cloudLoadBtn").disabled = !on;
  document.getElementById("cloudDelBtn").disabled = !on;
}
function renderCloud(list){
  const sel = document.getElementById("cloudSel");
  document.querySelector("#cloudBox h2").textContent =
    cloudAdmin ? "All saved designs (admin)" : "My saved designs";
  if (list === null){
    sel.innerHTML = "<option value=''>(cloud unavailable — local save still works)</option>";
    cloudBtns(false); return;
  }
  if (!list.length){
    sel.innerHTML = "<option value=''>(nothing saved to your account yet)</option>";
    cloudBtns(false); return;
  }
  sel.innerHTML = list.map(d => {
    const who = cloudAdmin && d.owner ? "  ·  " + String(d.owner).slice(0,8) : "";
    return `<option value="${esc(d.id)}">${esc(d.name || "untitled")}${who}</option>`;
  }).join("");
  cloudBtns(true);
}
function cloudList(){
  if (!API) return;
  fetch(API, { headers: apiHeaders(), cache:"no-store" })
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(d => { cloudAdmin = !!d.isAdmin; renderCloud(d.designs || []); })
    .catch(() => { cloudAdmin = false; renderCloud(null); });
}
function cloudSave(){
  if (!API){ cloudMsg("Cloud saving isn't configured."); return; }
  const name = (document.getElementById("nameInp").value.trim() || "untitled");
  cloudMsg("Saving…");
  fetch(API, { method:"POST", headers: apiHeaders(),
    body: JSON.stringify({ name, base, els }) })
    .then(r => r.ok ? r.json().catch(() => ({})) : Promise.reject(r.status))
    .then(() => { cloudMsg("Saved “" + name + "” to your account."); cloudList(); })
    .catch(e => cloudMsg("Couldn't save to cloud (" + e + "). It's kept in this browser."));
}
function cloudLoad(){
  const id = document.getElementById("cloudSel").value;
  if (!id) return;
  fetch(API + "/" + encodeURIComponent(id), { headers: apiHeaders(), cache:"no-store" })
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(d => {
      if (!Array.isArray(d.els)) throw 0;
      base = tplByKey(d.base) ? d.base : base;
      els = d.els.filter(e => EXT[e.t]).map(e => (
        { t:e.t, x:+e.x||0, y:+e.y||0, rot:(+e.rot||0)%360 }));
      els.forEach(clampEl);
      sel = -1; dirty = true;
      document.getElementById("nameInp").value = d.name || "";
      document.getElementById("tplSel").value = base;
      saveWork(); draw();
      cloudMsg("Loaded “" + (d.name || "design") + "”.");
    })
    .catch(e => cloudMsg("Couldn't load that design (" + e + ")."));
}
function cloudDel(){
  const selEl = document.getElementById("cloudSel");
  const id = selEl.value, name = (selEl.selectedOptions[0] || {}).text || "";
  if (!id || !confirm("Delete “" + name + "” from your account?")) return;
  fetch(API + "/" + encodeURIComponent(id), { method:"DELETE", headers: apiHeaders() })
    .then(r => r.ok ? cloudList() : Promise.reject(r.status))
    .catch(e => cloudMsg("Couldn't delete (" + e + ")."));
}

// ------- wire up -------
const tplSel = document.getElementById("tplSel");
tplSel.innerHTML = DATA.layouts.map(l =>
  `<option value="${l.key}">${l.letter} · ${l.short} — ${l.name}</option>`
).join("");
tplSel.onchange = () => loadTemplate(tplSel.value, true);
document.getElementById("resetBtn").onclick = () => loadTemplate(base, true);
document.getElementById("addTable").onclick = () => addEl("table");
document.getElementById("addRound").onclick = () => addEl("round");
document.getElementById("addTop").onclick = () => addEl("top");
document.getElementById("rotBtn").onclick = rotateSel;
document.getElementById("delBtn").onclick = removeSel;
document.getElementById("snapChk").onchange = draw;
document.getElementById("cloudSaveBtn").onclick = cloudSave;
document.getElementById("cloudLoadBtn").onclick = cloudLoad;
document.getElementById("cloudDelBtn").onclick = cloudDel;
document.getElementById("cid").textContent = clientId();
document.getElementById("copyIdBtn").onclick = () => {
  const id = clientId();
  if (navigator.clipboard) navigator.clipboard.writeText(id)
    .then(() => cloudMsg("Device ID copied.")).catch(() => {});
  else cloudMsg(id);
};
if (!API) document.getElementById("cloudBox").classList.add("hidden");
else cloudList();
window.addEventListener("resize", fit);
window.__state = () => ({ base, els, sel });   // for tests

// restore working design if there is one
(function init(){
  let w = null;
  try { w = JSON.parse(localStorage.getItem(WORK) || "null"); } catch(e){}
  if (w && Array.isArray(w.els) && w.els.length){
    base = tplByKey(w.base) ? w.base : base;
    els = w.els.filter(e => EXT[e.t]);
    document.getElementById("nameInp").value = w.name || "";
    dirty = true;
  } else {
    els = clone(tplByKey(base).els);
  }
  tplSel.value = base;
  refreshSaved();
  fit();
})();
</script>
</body>
</html>
"""


def main():
    data = dict(
        room=dict(w=ROOM_W, l=ROOM_L, beamY=BEAM_Y, hvac=list(HVAC),
                  well=list(ENTRY_WELL)),
        layouts=[dict(key=c["key"], letter=c["letter"], short=c["short"],
                      name=c["name"].split("·", 1)[-1].strip(),
                      els=elements_for(c))
                 for c in CONFIGS],
    )
    html = (TPL.replace("__DATA__", json.dumps(data, separators=(",", ":")))
               .replace("__DESIGNS_API__", json.dumps(DESIGNS_API))
               .replace("__HUB_URL__", HUB_URL))
    out = os.path.join(ROOT, "design.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1e3:.0f} KB, "
          f"{len(data['layouts'])} templates)")


if __name__ == "__main__":
    main()
