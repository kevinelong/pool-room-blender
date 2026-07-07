"""Single source of truth for the three public artifact URLs.

Every generated surface (poster, options PDF, walkthrough, download page,
decision deck, README) cross-links these; import from here so they can
never drift apart.
"""
WALKTHROUGH_URL = (
    "https://claude.ai/code/artifact/29c21156-ee9c-46b8-96b3-bf32162aacfe")
DOWNLOAD_URL = (
    "https://claude.ai/code/artifact/13ae99fe-5608-405e-b746-cdbad72873cd")
DECK_URL = (
    "https://claude.ai/code/artifact/5a9942da-0297-48fe-8acb-24d5e81baa24")
# the one-stop landing page (web poster) that wraps the three above —
# this is THE link to share
HUB_URL = (
    "https://claude.ai/code/artifact/4762f49c-6200-4062-8f9d-91f69d3c0aca")
