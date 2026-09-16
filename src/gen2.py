#!/usr/bin/env python3
"""pack-01 v2 — the Admiral's placement law (2026-09-15): bitcoin logo FRONT · the type on the
BACK · the brand on the SLEEVE cuff — like the Pac's Arcade tee already in the store.

Sizes are Printful's own print files per placement (GET /mockup-generator/printfiles, 150 dpi,
cached in printful/printfiles-818.json):
  tee 818/456   front 1800×2400 · back 1800×2400 · sleeve 600×525
  hoodie 479    front 2100×2100 · back 1800×2400 · sleeve 450×1800 (vertical)
  tote 367      front 1500×1500
  cap 491       embroidery_front_large 1650×600 (2 threads: white + 1987 Orange #E25C27)
Outputs → ../print2/<placement>/… . The back art is the pack-01 typography re-rendered to
1800×2400 from the same SVGs (src/*.svg), so nothing is redrawn by hand twice.
"""
import os, subprocess, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
OUT = f"{PACK}/print2"
ORANGE, WHITE, INK = "#ff4f00", "#ffffff", "#0b0b0b"
THREAD_ORANGE = "#E25C27"
SANS, PIX = "Adwaita Sans", "Press Start 2P"
INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>\n'


def coin(cx, cy, r, fill=ORANGE, glyph=INK):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>\n'
            + txt(cx, cy + r * 0.62, "₿", r * 1.7, fill=glyph, extra=f'transform="rotate(-12 {cx} {cy})"'))


def render(name, w, h, body, sub):
    d = f"{OUT}/{sub}"
    os.makedirs(d, exist_ok=True)
    src = f"{d}/{name}.svg"
    open(src, "w").write(svg(w, h, body))
    r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={d}/{name}.png",
                                  "--export-dpi=96", "--export-background-opacity=0"], capture_output=True, text=True)
    if r.returncode:
        print("ERR", name, r.stderr[-200:])
    else:
        print("ok", sub, name, f"{w}x{h}")


# ---- FRONT: the bitcoin logo, left chest (tee) / centre chest (hoodie) --------------------------
# Tee front area 1800×2400 = 12×16 in. A left-chest mark sits ~3.5 in wide, its centre ~3 in from
# the wearer's left edge (viewer's right) and ~2.5 in below the top of the area.
w, h = 1800, 2400
b = coin(1800 - 450, 380, 250)          # 3.3 in coin, wearer's left chest
render("front-btc-left-chest", w, h, b, "front-tee")
b = coin(900, 700, 420)                 # 5.6 in coin, centre chest — the louder option
b += txt(900, 1330, "frens.earth", 54, fill=WHITE, font=PIX, weight=400)
render("front-btc-centre", w, h, b, "front-tee")
# Hoodie front 2100×2100 (above the pocket): centre coin, smaller
b = coin(1050, 700, 330)
render("front-btc-hoodie", 2100, 2100, b, "front-hoodie")

# ---- SLEEVE: the brand on the cuff ---------------------------------------------------------------
# Tee sleeve 600×525 (4×3.5 in): wordmark on one line, small coin before it.
b = coin(72, 262, 42) + txt(128, 278, "frens.earth", 40, fill=WHITE, font=PIX, weight=400, anchor="start")
render("sleeve-frens-earth", 600, 525, b, "sleeve-tee")
b = coin(72, 262, 42) + txt(128, 278, "frens.earth", 40, fill=INK, font=PIX, weight=400, anchor="start")
render("sleeve-frens-earth-ink", 600, 525, b, "sleeve-tee")   # for light garments
# Hoodie sleeve 450×1800 (vertical): wordmark rotated to run down the arm
b = f'<g transform="rotate(90 225 900)">' + coin(225 - 400, 900, 46) + txt(225 - 330, 922, "frens.earth", 60, fill=WHITE, font=PIX, weight=400, anchor="start") + "</g>"
render("sleeve-frens-earth-hoodie", 450, 1800, b, "sleeve-hoodie")

# ---- BACK: the type — pack-01's SVGs re-rendered to 1800×2400 (half of the 3600×4800 masters) --
for src in sorted(glob.glob(f"{HERE}/D*-tee.svg")):
    name = os.path.basename(src)[:-4]
    d = f"{OUT}/back-tee"; os.makedirs(d, exist_ok=True)
    r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={d}/{name}-back.png",
                                  "--export-dpi=48", "--export-background-opacity=0"], capture_output=True, text=True)
    print("ERR" if r.returncode else "ok", "back-tee", name, "1800x2400")

# ---- TOTE 1500×1500: coin + one line ---------------------------------------------------------------
b = coin(750, 600, 330) + txt(750, 1120, "TICK TOCK", 120, fill=WHITE, font=PIX, weight=400) + txt(750, 1290, "NEXT BLOCK", 120, fill=ORANGE, font=PIX, weight=400)
render("tote-btc-tick-tock", 1500, 1500, b, "tote")
b = coin(750, 640, 380) + txt(750, 1240, "frens.earth", 90, fill=WHITE, font=PIX, weight=400)
render("tote-btc-frens", 1500, 1500, b, "tote")

# ---- CAP embroidery 1650×600: ∞/21M in two threads --------------------------------------------------
b = txt(825, 330, "∞", 380, fill=WHITE) + f'<rect x="605" y="350" width="440" height="34" fill="{THREAD_ORANGE}"/>\n' + txt(825, 560, "21M", 200, fill=WHITE)
render("cap-inf-over-21m", 1650, 600, b, "cap")
b = txt(825, 330, "₿", 400, fill=THREAD_ORANGE)
render("cap-btc", 1650, 600, b, "cap")

json.dump({"law": "front logo · back type · sleeve brand", "sizes": "Printful printfiles @150dpi", "out": OUT},
          open(f"{OUT}/README.json", "w"), indent=1)
print("done →", OUT)
