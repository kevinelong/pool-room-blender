#!/usr/bin/env python3
"""Build docs/get_pdf.html — the single-purpose PDF download page.

Both PDFs are embedded as data URIs so the page works anywhere with no
repo access; the footer cross-links the walkthrough and the interactive
decision deck (v44: every surface carries all three central URLs).
Regenerate after the options PDF or top-down sheet changes.
"""
import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from project_urls import WALKTHROUGH_URL, DECK_URL  # noqa: E402


def data_uri(relpath):
    fp = os.path.join(ROOT, relpath)
    with open(fp, "rb") as fh:
        raw = fh.read()
    return ("data:application/pdf;base64,"
            + base64.b64encode(raw).decode(), len(raw) / 1e6)


def main():
    options, opt_mb = data_uri("docs/pool_room_v16_options.pdf")
    sheet, sheet_mb = data_uri("docs/pool_room_topdowns.pdf")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pool Room — PDF Download</title>
</head>
<body>
<style>
  body {{ font-family: system-ui, sans-serif; background:#141417; color:#eee;
         display:flex; flex-direction:column; align-items:center;
         justify-content:center; min-height:92vh; gap:26px; padding:24px;
         text-align:center; }}
  h1 {{ font-size:26px; }}
  p {{ color:#9a9aa2; max-width:52ch; }}
  a.btn {{ display:block; background:#2e7d32; color:#fff; text-decoration:none;
          font-size:22px; font-weight:700; padding:22px 44px;
          border-radius:12px; }}
  a.btn:hover {{ background:#379e3c; }}
  a.btn small {{ display:block; font-size:13px; font-weight:400;
                opacity:.85; margin-top:4px; }}
  a.alt {{ background:#31446e; }}
  a.alt:hover {{ background:#3c5488; }}
</style>
<h1>Pool Room — Twelve Layout Options</h1>
<p>The complete study: overview scenarios, the lettered contents grid,
twelve layout pages with sightlines and pros &amp; cons, and the
links QR page. Tap a button — the file saves directly, nothing
else on this page.</p>
<a class="btn" download="pool_room_options.pdf"
   href="{options}">
   ⤓ Download the Options PDF<small>15 pages · {opt_mb:.1f} MB</small></a>
<a class="btn alt" download="pool_room_topdowns.pdf"
   href="{sheet}">
   ⤓ Download the one-page top-down sheet<small>8.5×11 · {sheet_mb:.1f} MB</small></a>
<p>Prefer to explore first? The
<a style="color:#9ad0ff" href="{WALKTHROUGH_URL}">first-person walkthrough</a>
has these same downloads at the top — and the
<a style="color:#9ad0ff" href="{DECK_URL}">interactive decision deck</a>
lets you set what the house values and watch the twelve layouts
re-rank live.</p>
</body>
</html>
"""
    # v48: Pages serves the repo root — public pages live there
    out = os.path.join(ROOT, "get_pdf.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
