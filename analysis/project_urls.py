"""Single source of truth for the public URLs.

Every generated surface (poster, options PDF, walkthrough, download page,
decision deck, hub, README) cross-links these; import from here so they
can never drift apart.

v47: URLs point at GitHub Pages (public — no login needed), served from
docs/ on main. The hub is the site root. claude.ai artifact copies still
exist but are workspace-only, so nothing printed should reference them.
"""
PAGES_ROOT = "https://kevinelong.github.io/pool-room-blender"

HUB_URL = PAGES_ROOT + "/"
WALKTHROUGH_URL = PAGES_ROOT + "/walk.html"
DOWNLOAD_URL = PAGES_ROOT + "/get_pdf.html"
DECK_URL = PAGES_ROOT + "/deck.html"
DESIGNER_URL = PAGES_ROOT + "/design.html"
