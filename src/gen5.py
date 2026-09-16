#!/usr/bin/env python3
"""Pack 03b — the forge pieces composed (2026-09-15): the four picks that needed the GPU.

Sources (our own renders on the local forge, copied to ../print4/src-forge/):
  eco-x4.png        the circuitry schematic upscaled 4× (RealESRGAN x4plus) → 4096²
  vintage-man.png   Z-Image t2i, a 1950s ad man raising a glass (ours, not the meme's stock art)
  poster.png        Z-Image t2i, a 50s monster-poster painting (ours)
  window.png        Z-Image t2i, rain-streaked window, hooded figure, autumn forest (ours; no mask)
Composed at Printful's tee back size 1800×2400. Type is ours. Outputs → ../print4/back-tee + preview.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
OUT = f"{PACK}/print4"
SRC = f"{OUT}/src-forge"
CREAM, ORANGE_C, NAVY = "#ecdcb6", "#d9782c", "#1a2230"
ORANGE, WHITE, INK, GREEN, RED = "#ff4f00", "#ffffff", "#0b0b0b", "#5ef78a", "#d0261c"
SANS, PIX = "Adwaita Sans", "Press Start 2P"
INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]
CARE_PATH = open(f"{PACK}/.tracework/btc-care-path.txt").read().strip()
GRAIN = ('<filter id="grain" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="7" result="n"/>'
         '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.7 0.62" result="holes"/><feComposite in="SourceGraphic" in2="holes" operator="out"/></filter>')
DRIP = ('<filter id="drip" x="-10%" y="-10%" width="120%" height="140%"><feTurbulence type="turbulence" baseFrequency="0.012 0.05" numOctaves="2" seed="3" result="t"/>'
        '<feDisplacementMap in="SourceGraphic" in2="t" scale="26" xChannelSelector="R" yChannelSelector="G"/></filter>')


def svg(w, h, body, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>\n{body}\n</svg>\n'


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>\n'


def img(path, x, y, w, h, extra=""):
    return f'<image xlink:href="{path}" href="{path}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" {extra}/>\n'


def care_b(cx, cy, size, fill=CREAM):
    bw, bh, bx, by = 558.6, 747.6, 23.0, 321.2
    k = size / bh
    return f'<g transform="translate({cx - (bx + bw/2)*k:.1f},{cy - (by + bh/2)*k:.1f}) scale({k:.5f})" filter="url(#grain)"><path d="{CARE_PATH}" fill="{fill}"/></g>\n'


def render(name, w, h, body, sub, defs=""):
    d = f"{OUT}/{sub}"
    os.makedirs(d, exist_ok=True); os.makedirs(f"{OUT}/preview", exist_ok=True)
    src = f"{d}/{name}.svg"
    open(src, "w").write(svg(w, h, body, defs))
    r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={d}/{name}.png", "--export-dpi=96", "--export-background-opacity=0"], capture_output=True, text=True)
    print("ERR" if r.returncode else "ok", sub, name, r.stderr[-160:] if r.returncode else "")
    subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={OUT}/preview/{name}.png", "--export-dpi=24", "--export-background-opacity=0"], capture_output=True, text=True)


# 1. the vintage man — cream card, the D01 line, our man
b = f'<rect x="60" y="60" width="1680" height="2280" rx="40" fill="{CREAM}"/>'
b += txt(900, 330, "YOU'RE NOT", 200, fill=NAVY) + txt(900, 540, "BUYING", 200, fill=NAVY) + txt(900, 750, "BITCOIN.", 200, fill=ORANGE_C)
b += img(f"{SRC}/vintage-man-alpha.png", 250, 820, 1300, 1300)
b += f'<rect x="60" y="2080" width="1680" height="260" fill="{NAVY}"/>'
b += txt(900, 2260, "YOU'RE SELLING FIAT.", 150, fill=CREAM)
render("vintage-man-selling-fiat-back", 1800, 2400, b, "back-tee")
if os.path.exists(f"{SRC}/joint-man-alpha.png"):
    b = b.replace("vintage-man-alpha.png", "joint-man-alpha.png")
    render("joint-man-selling-fiat-back", 1800, 2400, b, "back-tee")

# 2. the monster poster — painting on top, our title block over the bottom
b = f'<clipPath id="pc"><rect x="60" y="60" width="1680" height="2280"/></clipPath><g clip-path="url(#pc)">'
b += img(f"{SRC}/poster.png", 60, 420, 1680, 1680 * 1536 / 1024, 'preserveAspectRatio="xMinYMin slice"')
b += '</g>'
b += f'<rect x="60" y="60" width="1680" height="360" fill="{INK}"/>'
b += f'<rect x="60" y="1720" width="1680" height="620" fill="{INK}"/>'
b += txt(900, 180, "UNSTOPPABLE!", 96, fill=RED, weight=900) + txt(900, 290, "UNCENSORABLE!", 96, fill=RED, weight=900)
b += txt(900, 380, "21 MILLION, AND NOT ONE MORE.", 56, fill=WHITE, weight=800)
b += txt(900, 1960, "BITCOIN", 300, fill=RED, extra='filter="url(#drip)"')
b += txt(900, 2130, "in COLOR", 120, fill=WHITE, weight=800)
b += txt(900, 2270, "THE MONEY BANKERS CAN'T PRINT AND POLITICIANS CAN'T STOP", 46, fill="#bdbdbd", weight=700)
b += f'<rect x="60" y="60" width="1680" height="2280" fill="none" stroke="{CREAM}" stroke-width="8"/>'
render("bitcoin-in-color-poster-back", 1800, 2400, b, "back-tee", DRIP)

# 3. the window — our scene, dripping words on the glass, the care ₿
b = f'<clipPath id="wc"><rect x="0" y="0" width="1800" height="2400" rx="60"/></clipPath><g clip-path="url(#wc)">'
b += img(f"{SRC}/window.png", 0, 0, 1800, 2700)
b += '</g>'
b += care_b(1420, 380, 380)
b += txt(900, 1900, "THANK YOU,", 230, fill=CREAM, extra='filter="url(#drip)"')
b += txt(900, 2170, "SATOSHI", 300, fill=CREAM, extra='filter="url(#drip)"')
render("thank-you-satoshi-window-back", 1800, 2400, b, "back-tee", DRIP + GRAIN)

# 4. the ecosystem schematic — a white card with the line work (the 4× upscale), tee back
b = txt(900, 300, "THE BITCOIN ECOSYSTEM", 96, fill=WHITE) + txt(900, 400, "proof of work · nodes · miners · the grid", 34, fill=ORANGE, font=PIX, weight=400)
b += f'<rect x="90" y="520" width="1620" height="1620" rx="30" fill="{WHITE}"/>'
b += img(f"{SRC}/eco-x4.png", 120, 550, 1560, 1560)
render("bitcoin-ecosystem-card-back", 1800, 2400, b, "back-tee")
print("done →", OUT)
