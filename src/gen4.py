#!/usr/bin/env python3
"""Pack 03 — the Admiral's picks from the folder (2026-09-15), rebuilt as ours:

1. THE CARE ₿ — the cream, speckled ₿ from "btc doesnt care.webp" (he likes the font + colouring).
   The glyph is traced from the reference (Inkscape, .tracework/btc-care-path.txt), then rebuilt at
   any size with a grain filter, transparent: sticker 4 in · tee front left-chest · tee front centre ·
   a poster-style back with the reference's line in the same cream/orange register.
2. THE SATS PILL — closer to satspill.webp (he prefers the original): a glossy 3-D capsule, orange
   half, glass half full of sat pellets, "bitcoin 1 BTC" / "100M SATS".
3. HARD vs WEAK — our own infographic of the folder's comparison (their graphic carries someone's
   watermark; the idea is public, the drawing is ours): two columns, coin vs bill, six rows.
Outputs → ../print4/ (tee front/back at 1800×2400, stickers 1200², previews).
"""
import os, math, random, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
OUT = f"{PACK}/print4"
CREAM, ORANGE_C, NAVY = "#ecdcb6", "#d9782c", "#1a2230"   # the reference's palette
ORANGE, WHITE, INK, GREEN, RED = "#ff4f00", "#ffffff", "#0b0b0b", "#5ef78a", "#ff5c5c"
SANS, PIX = "Adwaita Sans", "Press Start 2P"
INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]
CARE_PATH = open(f"{PACK}/.tracework/btc-care-path.txt").read().strip() if os.path.exists(f"{PACK}/.tracework/btc-care-path.txt") else None


def svg(w, h, body, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>\n{body}\n</svg>\n'


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>\n'


GRAIN = ('<filter id="grain" x="-5%" y="-5%" width="110%" height="110%">'
         '<feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="7" result="n"/>'
         '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.7 0.62" result="holes"/>'
         '<feComposite in="SourceGraphic" in2="holes" operator="out"/></filter>')


def care_b(cx, cy, size, fill=CREAM, grain=True):
    """the traced ₿, centred at cx,cy, `size` = height in px, speckled like the print."""
    if not CARE_PATH:
        return txt(cx, cy + size * 0.36, "₿", size, fill=fill)
    # the trace lives in a 1200×1200 box; the glyph occupies roughly x 380–860, y 130–1070
    bw, bh, bx, by = 558.6, 747.6, 23.0, 321.2   # measured with inkscape --query
    k = size / bh
    flt = ' filter="url(#grain)"' if grain else ''
    return (f'<g transform="translate({cx - (bx + bw/2)*k:.1f},{cy - (by + bh/2)*k:.1f}) scale({k:.5f})"{flt}>'
            f'<path d="{CARE_PATH}" fill="{fill}"/></g>\n')


def render(name, w, h, body, sub, defs=""):
    d = f"{OUT}/{sub}"
    os.makedirs(d, exist_ok=True); os.makedirs(f"{OUT}/preview", exist_ok=True)
    src = f"{d}/{name}.svg"
    open(src, "w").write(svg(w, h, body, defs))
    r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={d}/{name}.png", "--export-dpi=96", "--export-background-opacity=0"], capture_output=True, text=True)
    print("ERR" if r.returncode else "ok", sub, name, f"{w}x{h}", r.stderr[-150:] if r.returncode else "")
    subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={OUT}/preview/{name}.png", "--export-dpi=24", "--export-background-opacity=0"], capture_output=True, text=True)


# ---------------------------------------------------------------- 1. the care ₿ — TIGHT, transparent (the Admiral: "crop around the b")
TW, TH = 1850, 2400   # the glyph's own proportions (558.6 : 747.6) at 2400 px tall
for nm, fill, grain in (("care-b-cream-grain", CREAM, True), ("care-b-cream-solid", CREAM, False),
                        ("care-b-orange-grain", ORANGE_C, True), ("care-b-orange-solid", ORANGE_C, False)):
    render(nm, TW, TH, care_b(TW / 2, TH / 2, TH * 0.96, fill=fill, grain=grain), "care-b", GRAIN)
# the same four at sticker size (4 in die-cut, 1200 tall)
for nm, fill, grain in (("care-b-sticker-cream-grain", CREAM, True), ("care-b-sticker-cream-solid", CREAM, False),
                        ("care-b-sticker-orange-grain", ORANGE_C, True), ("care-b-sticker-orange-solid", ORANGE_C, False)):
    render(nm, 925, 1200, care_b(925 / 2, 600, 1200 * 0.96, fill=fill, grain=grain), "stickers", GRAIN)
# the poster back: navy block + orange block, the line, the ₿ — the reference's register, our type
b = (f'<rect x="150" y="200" width="1500" height="900" fill="{NAVY}"/>'
     f'<rect x="150" y="1100" width="1500" height="1000" fill="{ORANGE_C}"/>')
b += txt(900, 560, "BITCOIN", 280, fill=ORANGE_C)
b += txt(900, 780, "DOESN'T FIGHT", 140, fill=CREAM) + txt(900, 950, "GOVERNMENTS.", 140, fill=CREAM)
b += txt(900, 1400, "IT IGNORES", 190, fill=NAVY) + txt(900, 1600, "THEM.", 190, fill=NAVY)
b += care_b(900, 1860, 260)
b += f'<rect x="150" y="200" width="1500" height="1900" fill="none" stroke="{CREAM}" stroke-width="10"/>'
render("care-poster-back", 1800, 2400, b, "back-tee", GRAIN)

# ---------------------------------------------------------------- 2. the sats pill, glossy
PILL_DEFS = (
    f'<linearGradient id="orangeG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff8a3d"/><stop offset="0.55" stop-color="{ORANGE}"/><stop offset="1" stop-color="#b93200"/></linearGradient>'
    '<linearGradient id="glassG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0.04"/><stop offset="1" stop-color="#000000" stop-opacity="0.35"/></linearGradient>'
    '<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
    '<radialGradient id="pellet" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffb070"/><stop offset="0.6" stop-color="#ff5a00"/><stop offset="1" stop-color="#a12b00"/></radialGradient>'
)


def pill(cx, cy, L, R, label_big, label_small, seed=624):
    x0, y0 = cx - L / 2, cy - R
    random.seed(seed)
    out = f'<clipPath id="capclip"><rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}"/></clipPath>'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="#2a1a12"/>'
    out += f'<g clip-path="url(#capclip)">'
    out += f'<rect x="{x0}" y="{y0}" width="{L/2}" height="{2*R}" fill="url(#orangeG)"/>'
    # pellets in the glass half
    for _ in range(420):
        px = cx + 40 + random.random() * (L / 2 - 80)
        py = y0 + R * 0.08 + random.random() * (R * 1.84)
        rr = R * (0.045 + random.random() * 0.04)
        out += f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rr*1.25:.0f}" ry="{rr:.0f}" fill="url(#pellet)" transform="rotate({random.randint(-40,40)} {px:.0f} {py:.0f})"/>'
    out += f'<rect x="{cx}" y="{y0}" width="{L/2}" height="{2*R}" fill="url(#glassG)"/>'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" fill="url(#glassG)" opacity="0.6"/>'
    out += f'<rect x="{x0 + R*0.3}" y="{y0 + R*0.12}" width="{L - R*0.6}" height="{R*0.55}" rx="{R*0.27}" fill="url(#gloss)"/>'
    out += '</g>'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="none" stroke="#3a1f12" stroke-width="{R*0.05}"/>'
    out += f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0+2*R}" stroke="#3a1f12" stroke-width="{R*0.05}"/>'
    out += txt(cx - L / 4, cy - R * 0.02, label_big, R * 0.62, fill=WHITE, weight=800)
    out += txt(cx - L / 4, cy + R * 0.5, label_small, R * 0.3, fill=WHITE, weight=600)
    out += txt(cx + L / 4, cy - R * 0.02, "sats", R * 0.62, fill=WHITE, weight=800)
    out += txt(cx + L / 4, cy + R * 0.5, "100M SATS", R * 0.3, fill=WHITE, weight=600)
    return out


render("sats-pill-glossy-back", 1800, 2400, pill(900, 1200, 1700, 330, "bitcoin", "1 BTC"), "back-tee", PILL_DEFS)
render("sats-pill-glossy-sticker", 1200, 1200, pill(600, 600, 1150, 230, "bitcoin", "1 BTC"), "stickers", PILL_DEFS)

# ---------------------------------------------------------------- 3. hard vs weak — our infographic
def coin_half(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ORANGE}"/>' + txt(cx, cy + r * 0.62, "₿", r * 1.7, fill=INK, extra=f'transform="rotate(-12 {cx} {cy})"'))


def bill(cx, cy, w, h):
    return (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{h*0.08}" fill="#2f6b3a"/>'
            f'<rect x="{cx-w/2+h*0.1}" y="{cy-h/2+h*0.1}" width="{w-h*0.2}" height="{h-h*0.2}" rx="{h*0.05}" fill="none" stroke="#bfe0c3" stroke-width="{h*0.03}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{h*0.3}" fill="#bfe0c3"/>' + txt(cx, cy + h * 0.11, "$", h * 0.36, fill="#2f6b3a"))


b = ""
b += txt(430, 260, "HARD MONEY", 104, fill=ORANGE) + txt(1370, 260, "WEAK MONEY", 104, fill=RED)
b += txt(900, 252, "vs", 64, fill=WHITE, weight=700)
b += care_b(470, 560, 330, fill=CREAM, grain=False) + bill(1330, 560, 460, 260)
rows = [("21M CAP", "UNLIMITED PRINTING"), ("MATH-BASED", "POLICY-BASED"), ("OWNED BY YOU", "CONTROLLED"),
        ("DEFLATIONARY", "INFLATIONARY"), ("DECENTRALIZED", "CENTRALIZED"), ("FREEDOM MONEY", "DEBT MONEY")]
y = 900
for left, right in rows:
    b += f'<rect x="120" y="{y-95}" width="1560" height="170" rx="30" fill="#151515"/>'
    b += f'<line x1="900" y1="{y-80}" x2="900" y2="{y+60}" stroke="#333" stroke-width="6"/>'
    b += txt(470, y + 22, left, 66, fill=GREEN) + txt(1300, y + 22, right, 60, fill=RED)
    y += 205
render("hard-vs-weak-back", 1800, 2400, b, "back-tee", GRAIN)
print("done →", OUT)
