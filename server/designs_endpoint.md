# Pool Room — saved-designs API (VPS handoff)

The designer at `https://kevinelong.github.io/pool-room-blender/design.html`
now has a **cloud store**. It needs matching routes on codeonline.io. The
front end is already built and deployed against this exact contract — no
client change is needed once these routes are live.

## Identity model (already implemented client-side)

- Each browser mints a UUID once (`crypto.randomUUID()`), keeps it in
  `localStorage`, and sends it on **every** request as header
  `X-Client-Token: <uuid>`. No email, no login, no cookies.
- A design's **owner** is the token that created it. Regular callers only
  ever see their own designs — **the server enforces this filter; never
  trust the client to scope it.**
- **Admin** = any token listed in env `POOLROOM_ADMIN_TOKENS` (comma-
  separated). An admin's `GET` returns *all* designs plus each row's
  `owner`, and the response carries `isAdmin: true`. The designer relabels
  its panel to "All saved designs (admin)" when it sees that flag.
- **Admin enrollment**: the designer shows "This device's ID: <uuid>" with
  a copy button. To make Kevin an admin, copy that ID and add it to
  `POOLROOM_ADMIN_TOKENS`. That's the whole flow.

## Env vars

```
POOLROOM_ADMIN_TOKENS=<kevin-device-uuid>[,<another>,...]   # optional; may be empty
POOLROOM_DESIGNS_DB=/var/www/poolroom/designs.sqlite         # or wherever
```

## Routes  (base: `/api/poolroom/designs`)

All responses are JSON. All set CORS headers (see below). `:id` is the
server-assigned design id.

| Method   | Path        | Auth (X-Client-Token) | Does |
|----------|-------------|-----------------------|------|
| `POST`   | `/`         | required              | Create a design owned by the token. Body `{name, base, els}`. Returns `{ok:true, id}`. |
| `GET`    | `/`         | required              | List designs. Regular token → only its own: `{designs:[{id,name,updatedAt}], isAdmin:false}`. Admin token → all, each with `owner`: `{designs:[{id,name,updatedAt,owner}], isAdmin:true}`. |
| `GET`    | `/:id`      | required              | Load one full design `{id,name,base,els}`. 404 unless the token owns it **or** is admin. |
| `DELETE` | `/:id`      | required              | Delete. 404/403 unless owner or admin. Returns `{ok:true}`. |
| `OPTIONS`| any         | —                     | CORS preflight → `204`. |

Missing/empty `X-Client-Token` on a required route → `401 {"error":"no token"}`.

### Payload shape

`els` is an array of pieces, each `{t, x, y, rot}` where `t` ∈
`table|round|top`, `x`/`y` are inches, `rot` a multiple of 45. `base` is a
layout key (e.g. `social`). Store `name`, `base`, and `els` verbatim; you
do not need to interpret geometry. Cap: reject bodies over ~64 KB and
`els.length > 200` with `400` (defensive; a real design is ~6–20 pieces).

## CORS (every response, including errors and OPTIONS)

```
Access-Control-Allow-Origin: https://kevinelong.github.io
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-Client-Token
```

Reuse whatever rate-limit middleware guards `/api/poolroom/vote`.

## Reference implementation (Express + better-sqlite3)

```js
// designs.js  — mount with: app.use("/api/poolroom/designs", require("./designs"))
const express = require("express");
const Database = require("better-sqlite3");
const crypto = require("crypto");

const db = new Database(process.env.POOLROOM_DESIGNS_DB || "designs.sqlite");
db.exec(`CREATE TABLE IF NOT EXISTS designs(
  id TEXT PRIMARY KEY, owner TEXT NOT NULL, name TEXT, base TEXT,
  els TEXT NOT NULL, created TEXT, updated TEXT);
  CREATE INDEX IF NOT EXISTS designs_owner ON designs(owner);`);

const ADMIN = new Set((process.env.POOLROOM_ADMIN_TOKENS || "")
  .split(",").map(s => s.trim()).filter(Boolean));
const isAdmin = tok => ADMIN.has(tok);

const router = express.Router();
router.use(express.json({ limit: "64kb" }));
router.use((req, res, next) => {
  res.set("Access-Control-Allow-Origin", "https://kevinelong.github.io");
  res.set("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.set("Access-Control-Allow-Headers", "Content-Type, X-Client-Token");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});
function token(req){ return (req.get("X-Client-Token") || "").trim(); }
function requireToken(req, res){
  const t = token(req);
  if (!t){ res.status(401).json({ error: "no token" }); return null; }
  return t;
}

// create
router.post("/", (req, res) => {
  const tok = requireToken(req, res); if (!tok) return;
  const { name, base, els } = req.body || {};
  if (!Array.isArray(els) || els.length > 200)
    return res.status(400).json({ error: "bad design" });
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  db.prepare(`INSERT INTO designs(id,owner,name,base,els,created,updated)
              VALUES(?,?,?,?,?,?,?)`).run(
    id, tok, String(name || "untitled").slice(0, 80),
    String(base || ""), JSON.stringify(els), now, now);
  res.json({ ok: true, id });
});

// list
router.get("/", (req, res) => {
  const tok = requireToken(req, res); if (!tok) return;
  const admin = isAdmin(tok);
  const rows = admin
    ? db.prepare(`SELECT id,name,updated,owner FROM designs
                  ORDER BY updated DESC`).all()
    : db.prepare(`SELECT id,name,updated FROM designs WHERE owner=?
                  ORDER BY updated DESC`).all(tok);
  res.json({
    isAdmin: admin,
    designs: rows.map(r => ({
      id: r.id, name: r.name, updatedAt: r.updated,
      ...(admin ? { owner: r.owner } : {}) })),
  });
});

// load one
router.get("/:id", (req, res) => {
  const tok = requireToken(req, res); if (!tok) return;
  const r = db.prepare("SELECT * FROM designs WHERE id=?").get(req.params.id);
  if (!r || (r.owner !== tok && !isAdmin(tok)))
    return res.status(404).json({ error: "not found" });
  res.json({ id: r.id, name: r.name, base: r.base, els: JSON.parse(r.els) });
});

// delete
router.delete("/:id", (req, res) => {
  const tok = requireToken(req, res); if (!tok) return;
  const r = db.prepare("SELECT owner FROM designs WHERE id=?").get(req.params.id);
  if (!r || (r.owner !== tok && !isAdmin(tok)))
    return res.status(404).json({ error: "not found" });
  db.prepare("DELETE FROM designs WHERE id=?").run(req.params.id);
  res.json({ ok: true });
});

module.exports = router;
```

That's the whole backend. `npm i better-sqlite3` if it isn't already
present. Once mounted, the designer's "My saved designs" panel goes live
with zero client changes; adding Kevin's device ID to
`POOLROOM_ADMIN_TOKENS` flips his view to all-accounts.
