#!/usr/bin/env python3
"""Pack 04 — "Bitcoin = Freedom" (the Admiral, 2026-09-16). Original type + vector only.

Answers the repo/format questions in the same commit:
- every element sits in its own <g inkscape:label="..."> group — opens in Inkscape (or GIMP's
  SVG import) with a named, selectable Objects/Layers list, not one flat blob.
- exported at the print DPI Printful actually wants (150 dpi DTG tee = 1800x2400 px @ 12x16in,
  300 dpi sticker = 1200x1200 px @ 4x4in) PLUS a 600 dpi archival master per file (trivial —
  these are vector; a 600dpi print master would be 7200x9600 px, useful for a giclée/poster
  run later, not needed for a tee).
- PNG is intentionally flat (Printful's API takes one flat raster per placement — that's the
  format, not a limitation of this pipeline). The SVG next to every PNG is the layered,
  human-editable source; open it in Inkscape (flatpak run org.inkscape.Inkscape file.svg) or
  GIMP (File > Open, GIMP rasterizes SVG groups on import — for a true multi-layer .xcf, see
  freedom-tee-back.xcf, built once here via GIMP script-fu as a worked example).

Outputs → ../print5/{front-tee,back-tee,stickers}/*.{svg,png} (+ *-600dpi.png masters).
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
OUT = f"{PACK}/print5"
ORANGE, WHITE, INK, GOLD = "#ff4f00", "#ffffff", "#0b0b0b", "#f7c948"
SANS, PIX = "Adwaita Sans", "Press Start 2P"
INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]
CARE_PATH = open(f"{PACK}/.tracework/btc-care-path.txt").read().strip()
NS = 'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'


import re as _re


def _slug(s):
    return _re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def svg(w, h, groups):
    body = "\n".join(
        f'<g id="layer-{_slug(label)}" inkscape:label="{label}" inkscape:groupmode="layer">{content}</g>'
        for label, content in groups
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {NS} width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>\n'


def care_b(cx, cy, size, fill=WHITE):
    bw, bh, bx, by = 558.6, 747.6, 23.0, 321.2
    k = size / bh
    return f'<g transform="translate({cx - (bx + bw/2)*k:.1f},{cy - (by + bh/2)*k:.1f}) scale({k:.5f})"><path d="{CARE_PATH}" fill="{fill}"/></g>\n'


def key_icon(cx, cy, s, fill=WHITE):
    """a simple vector key — bow (ring) + shaft + two teeth, pointing right."""
    r = s * 0.28
    out = f'<circle cx="{cx - s*0.32:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{fill}" stroke-width="{s*0.09:.1f}"/>'
    out += f'<rect x="{cx - s*0.05:.1f}" y="{cy - s*0.045:.1f}" width="{s*0.62:.1f}" height="{s*0.09:.1f}" fill="{fill}"/>'
    out += f'<rect x="{cx + s*0.30:.1f}" y="{cy - s*0.045:.1f}" width="{s*0.08:.1f}" height="{s*0.20:.1f}" fill="{fill}"/>'
    out += f'<rect x="{cx + s*0.44:.1f}" y="{cy - s*0.045:.1f}" width="{s*0.08:.1f}" height="{s*0.14:.1f}" fill="{fill}"/>'
    return out


def render(name, w, h, groups, sub, print_dpi):
    """w,h = the print file's pixel size (already sized at print_dpi, e.g. 1800x2400 @150dpi
    = 12x16in). Emits: <name>.png at print_dpi (the file Printful actually wants), and
    <name>-600dpi.png — the SAME vector re-rendered at 600dpi over the same physical size
    (a fresh render, not an upscale, so it stays sharp) for archival/giclee use."""
    d = f"{OUT}/{sub}"
    os.makedirs(d, exist_ok=True)
    os.makedirs(f"{OUT}/preview", exist_ok=True)
    src = f"{d}/{name}.svg"
    open(src, "w").write(svg(w, h, groups))
    in_w, in_h = w / print_dpi, h / print_dpi
    jobs = [(f"{d}/{name}.png", 96), (f"{d}/{name}-600dpi.png", 600)]
    for out_png, dpi in jobs:
        px_w = round(in_w * dpi) if dpi != 96 else w
        px_h = round(in_h * dpi) if dpi != 96 else h
        r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={out_png}",
                                      f"--export-width={px_w}", f"--export-height={px_h}",
                                      "--export-background-opacity=0"], capture_output=True, text=True)
        print("ERR" if r.returncode else "ok", sub, name, f"{px_w}x{px_h}@{dpi}dpi", r.stderr[-150:] if r.returncode else "")
    subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={OUT}/preview/{name}.png",
                              "--export-width=450", "--export-background-opacity=0"], capture_output=True, text=True)


# ---------------------------------------------------------------- back: the equation, big
TEE = (1800, 2400, 150)
b = [
    ("backdrop", f'<rect width="1800" height="2400" fill="none"/>'),
    ("BITCOIN word", txt(900, 950, "BITCOIN", 240, fill=ORANGE)),
    ("equals sign", txt(900, 1230, "=", 260, fill=WHITE, weight=700)),
    ("FREEDOM word", txt(900, 1560, "FREEDOM", 240, fill=WHITE)),
    ("key icon", key_icon(900, 1850, 620, fill=ORANGE)),
    ("footline", txt(900, 2260, "self-custody is the sentence", 52, fill="#5ef78a", font=PIX, weight=400)),
]
render("freedom-equation-back", TEE[0], TEE[1], b, "back-tee", TEE[2])

# ---------------------------------------------------------------- back: the care-B + freedom, poster-band
b = [
    ("care B mark", care_b(900, 780, 900, fill=WHITE)),
    ("top band", f'<rect x="0" y="1500" width="1800" height="900" fill="{ORANGE}"/>'),
    ("BITCOIN IS word", txt(900, 1750, "BITCOIN IS", 150, fill=INK)),
    ("FREEDOM word 2", txt(900, 1980, "FREEDOM", 260, fill=INK)),
    ("subline", txt(900, 2250, "no permission \u00b7 no border \u00b7 no ruler", 42, fill=INK, font=PIX, weight=400)),
]
render("freedom-care-b-back", TEE[0], TEE[1], b, "back-tee", TEE[2])

# ---------------------------------------------------------------- front: small equation badge, left chest
FRONT = (1800, 2400, 150)
b = [
    ("badge ring", f'<circle cx="1350" cy="440" r="380" fill="none" stroke="{ORANGE}" stroke-width="20"/>'),
    ("badge B", care_b(1350, 340, 300, fill=WHITE)),
    ("badge equals freedom", txt(1350, 620, "= FREEDOM", 76, fill=WHITE, font=PIX, weight=400)),
]
render("freedom-badge-front", FRONT[0], FRONT[1], b, "front-tee", FRONT[2])

# ---------------------------------------------------------------- sticker: the equation, die-cut friendly
STK = (1200, 1200, 300)
b = [
    ("plate", f'<rect x="40" y="40" width="1120" height="1120" rx="90" fill="{INK}" stroke="{ORANGE}" stroke-width="26"/>'),
    ("BITCOIN word s", txt(600, 380, "BITCOIN", 150, fill=ORANGE)),
    ("equals s", txt(600, 520, "=", 170, fill=WHITE, weight=700)),
    ("FREEDOM word s", txt(600, 700, "FREEDOM", 150, fill=WHITE)),
    ("key icon s", key_icon(600, 900, 340, fill=ORANGE)),
    ("tag", txt(600, 1100, "frens.earth", 44, fill=WHITE, font=PIX, weight=400)),
]
render("freedom-equation-sticker", STK[0], STK[1], b, "stickers", STK[2])

print("done →", OUT)
