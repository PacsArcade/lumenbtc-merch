# lumenbtc-merch — the frens.earth bitcoin line

Print-ready art for Printful. Original type + vector, no borrowed IP. Built on the Lumen lane
(Pac's Arcade), reviewed by the Admiral. Placement law: **bitcoin logo front · the type on the
back · the brand on the sleeve cuff**.

- `src/gen.py` — the v1 masters (3600×4800 tees, 1500² stickers, hat) · `src/gen2.py` — v2 files at
  Printful's own print sizes (front / back / sleeve / tote / cap) → `print2/`
- `print/`, `print2/` — the files Printful fetches (this repo is the public host)
- `printful/` — catalog cache, `plan.json`, `create-products.py` (token stays on the ship, never here)
- `preview/` — dark-backed previews for the reviewer

Regenerate: `python3 src/gen.py && python3 src/gen2.py` (Inkscape via flatpak).
