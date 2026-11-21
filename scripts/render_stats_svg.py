#!/usr/bin/env python3
"""
Render the streak / numbers card from data/contributions.json as a terminal-window SVG.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "stats.svg")

BG = "#0d1117"
BG2 = "#111722"
TILE = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
GREEN = "#39d353"
BAR = "#26a641"

W, H = 840, 880
PAD = 20
TITLEBAR_H = 30
COLS, ROWS = 2, 3
GAP = 16
TILE_W = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
TILE_H = 150
TILES_TOP = TITLEBAR_H + PAD + 4
CHART_TOP = TILES_TOP + ROWS * TILE_H + (ROWS - 1) * GAP + GAP

TILE_STAGGER = 0.15
SLIDE_DUR = 0.45
BAR_START = TILE_STAGGER * COLS * ROWS + 0.4
BAR_STAGGER = 0.06
BAR_DUR = 0.6


def short(d):
    if not d or d == "N/A":
        return "—"
    try:
        return datetime.date.fromisoformat(d).strftime("%b %-d")
    except Exception:
        return d


def span(s):
    return f'{short(s.get("start"))} – {short(s.get("end"))}' if s.get("length") else "—"


if os.path.exists(SRC):
    data = json.load(open(SRC, encoding="utf-8"))
else:
    data = {
        "current_streak": {"length": 0},
        "longest_streak": {"length": 1},
        "total_contributions": 1,
        "active_days": 1,
        "best_day": {"count": 1, "date": "2026-01-06"},
        "avg_per_active_day": 1.0,
        "days": [],
        "monthly": [{"month": "2026-01", "total": 1}]
    }

cur, lng, best = data.get("current_streak", {}), data.get("longest_streak", {}), data.get("best_day", {})
n_days = len(data.get("days", [])) or 365

tiles = [
    ("current streak", cur.get("length", 0), " days", span(cur), GREEN),
    ("longest streak", lng.get("length", 0), " days", span(lng), INK),
    ("contributions", data.get("total_contributions", 0), "", "in the last year", INK),
    ("active days", data.get("active_days", 0), f" / {n_days}", f'{data.get("active_days", 0) / n_days:.0%} of the year', INK),
    ("best day", best.get("count", 0), "", short(best.get("date")), INK),
    ("avg / active day", data.get("avg_per_active_day", 0), "", "contributions", INK),
]

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<style>'
    f'.t{{opacity:0;animation:in {SLIDE_DUR}s ease-out both}}'
    '@keyframes in{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:translateY(0)}}'
    f'.b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow {BAR_DUR}s ease-out both}}'
    '@keyframes grow{to{transform:scaleY(1)}}'
    '@media (prefers-reduced-motion: reduce){.t,.b{opacity:1!important;transform:none!important;animation:none!important}}'
    '</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">sayyed@github: ~$ ./stats.sh</text>')

for idx, (lbl, val, suf, cap, accent) in enumerate(tiles):
    c, r = idx % COLS, idx // COLS
    x = PAD + c * (TILE_W + GAP)
    y = TILES_TOP + r * (TILE_H + GAP)
    delay = idx * TILE_STAGGER
    parts.append(
        f'<g class="t" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="{TILE}" stroke="{FRAME}" stroke-width="0.8"/>'
        f'<text x="{x + 16}" y="{y + 28}" fill="{MUTED}" font-size="12" text-transform="uppercase" letter-spacing="1">{lbl}</text>'
        f'<text x="{x + 16}" y="{y + 82}" fill="{accent}" font-size="36" font-weight="bold">{val}<tspan font-size="18" fill="{MUTED}">{suf}</tspan></text>'
        f'<text x="{x + 16}" y="{y + 118}" fill="{MUTED}" font-size="12">{cap}</text>'
        f'</g>'
    )

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {len(svg)//1024} KB")
