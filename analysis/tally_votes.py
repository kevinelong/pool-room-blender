#!/usr/bin/env python3
"""Tally the split ranked-choice ballots.

Reads ballots from either source:
  * server JSONL  — the file server/vote_endpoint.php appends to
                    (one JSON ballot per line), OR
  * a text dump   — paste the mailto ballots (or the whole inbox) into a
                    .txt file; the 'TALLY: 4+2=k>k ; 3+3=k>k' lines are
                    parsed, one ballot each.

For each room-split family it reports first-choice plurality, Borda points
(1st = 2, 2nd = 1), and a stakeholder-group breakdown. Layout keys resolve
to their current letter + short name from the configs.

Usage:
    python3 analysis/tally_votes.py path/to/ballots.jsonl
    python3 analysis/tally_votes.py path/to/inbox_dump.txt
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from configs.v16_configs import CONFIGS  # noqa: E402

LABEL = {c["key"]: f'{c["letter"]} · {c["short"]}' for c in CONFIGS}
KEYS = set(LABEL)


def load(path):
    """Return list of ballots: {stakeholder, fourTwo[], threeThree[]}."""
    text = open(path, encoding="utf-8", errors="replace").read()
    ballots = []
    # 1) JSONL (server)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and '"fourTwo"' in line:
            try:
                b = json.loads(line)
                ballots.append(dict(
                    stakeholder=b.get("stakeholder", "?"),
                    fourTwo=[k for k in b.get("fourTwo", []) if k in KEYS],
                    threeThree=[k for k in b.get("threeThree", []) if k in KEYS]))
            except json.JSONDecodeError:
                pass
    if ballots:
        return ballots
    # 2) mailto text dump — parse TALLY lines (+ optional Stakeholder-code)
    blocks = re.split(r"(?=POOL ROOM BALLOT)", text)
    for blk in blocks:
        m = re.search(r"TALLY:\s*4\+2=([^;]*);\s*3\+3=(\S*)", blk)
        if not m:
            continue
        stk = "?"
        sm = re.search(r"Stakeholder(?:-code)?:\s*(.+)", blk)
        if sm:
            stk = sm.group(1).strip()
        ft = [k for k in m.group(1).strip().split(">") if k in KEYS]
        tt = [k for k in m.group(2).strip().split(">") if k in KEYS]
        ballots.append(dict(stakeholder=stk, fourTwo=ft, threeThree=tt))
    return ballots


def report_family(title, picks):
    """picks: list of ranked key-lists (index 0 = 1st choice)."""
    first = Counter(p[0] for p in picks if p)
    borda = Counter()
    for p in picks:
        for i, k in enumerate(p[:2]):
            borda[k] += 2 - i          # 1st=2, 2nd=1
    n = sum(1 for p in picks if p)
    print(f"\n=== {title} — {n} ballots ranked here ===")
    print("  first-choice plurality:")
    for k, c in first.most_common():
        bar = "#" * c
        print(f"    {LABEL.get(k, k):26s} {c:3d}  {bar}")
    print("  Borda points (1st=2, 2nd=1):")
    for k, pts in borda.most_common():
        print(f"    {LABEL.get(k, k):26s} {pts:3d}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ballots = load(sys.argv[1])
    if not ballots:
        print("No ballots found. Expected server JSONL lines or mailto "
              "'TALLY:' lines.")
        sys.exit(1)
    print(f"Loaded {len(ballots)} ballot(s) from {sys.argv[1]}")

    by_stk = Counter(b["stakeholder"] for b in ballots)
    print("\nStakeholders:")
    for s, c in by_stk.most_common():
        print(f"  {s:22s} {c}")

    report_family("4 in one room, 2 in the other",
                  [b["fourTwo"] for b in ballots])
    report_family("3 in each room",
                  [b["threeThree"] for b in ballots])

    # combined headline: top of each family by Borda
    print("\n--- headline ---")
    for title, key in (("4+2", "fourTwo"), ("3+3", "threeThree")):
        borda = Counter()
        for b in ballots:
            for i, k in enumerate(b[key][:2]):
                borda[k] += 2 - i
        if borda:
            win = borda.most_common(1)[0]
            print(f"  {title} leader: {LABEL.get(win[0], win[0])} "
                  f"({win[1]} pts)")


if __name__ == "__main__":
    main()
