#!/usr/bin/env python3
"""frens.earth bitcoin merch pack-01 (built on the Lumen lane) — original typographic designs, print-ready.

Emits SVGs sized in px at 300 DPI:
  tee/hoodie/tote front  12x16 in  -> 3600x4800
  sticker (kiss-cut)      5x5 in   -> 1500x1500
  hat embroidery front  4.5x2.25   -> 1350x675
All designs are original type + simple vector; no third-party IP.
Palette: Lumen 624nm #ff4f00 (never official btc orange), white, near-black.
"""
import os, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
SRC, PRINT, PREV = HERE, f"{PACK}/print", f"{PACK}/preview"

ORANGE = "#ff4f00"
WHITE = "#ffffff"
INK = "#0b0b0b"
GREEN = "#5ef78a"   # fiat green (the Admiral: "could be green fiat")
SANS = "Adwaita Sans"
PIX = "Press Start 2P"
MONO = "Adwaita Mono"

TEE = (3600, 4800)
STK = (1500, 1500)
HAT = (1350, 675)

designs = {}  # name -> (size, svg body, note)


def svg(size, body):
    w, h = size
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n{body}\n</svg>\n')


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle",
        ls=0, extra=""):
    s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" {extra}>{s}</text>\n')


def stack(x, y, lines, size, gap=1.0, **kw):
    """lines: list of (text, fill) or str; y = baseline of first line."""
    out = ""
    for i, ln in enumerate(lines):
        if isinstance(ln, tuple):
            s, fill = ln
        else:
            s, fill = ln, kw.get("fill", WHITE)
        k = {k2: v for k2, v in kw.items() if k2 != "fill"}
        out += txt(x, y + i * size * gap, s, size, fill=fill, **k)
    return out


def sig(w, h, fill=WHITE, size=44):
    """frens.earth tag, bottom centre (arcade line — no persona handle on merch)."""
    return ""  # review 2026-09-15: no brand tag on the art — the brand rides the sleeve (v2)


def btc_mark_inverse(cx, cy, r):
    """the Admiral: keep the orange ₿, make the circle black."""
    return btc_mark(cx, cy, r, fill=INK, glyph_fill=ORANGE)


def btc_mark(cx, cy, r, fill=ORANGE, glyph_fill=INK):
    """A coin: circle + ₿ glyph (Adwaita Sans has U+20BF)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>\n'
            + txt(cx, cy + r * 0.62, "₿", r * 1.7, fill=glyph_fill,
                  font=SANS, weight=900, extra='transform="rotate(-12 %d %d)"' % (cx, cy)))


# ---------------------------------------------------------------- D01
w, h = TEE
b = ""
b += stack(w / 2, 1500, ["YOU'RE NOT", "BUYING", ("BITCOIN.", ORANGE)], 560, gap=0.92, fill=WHITE)
b += txt(w / 2, 3300, "YOU'RE", 560, fill=WHITE)
b += f'<text x="{w/2}" y="3800" font-family="{SANS}" font-weight="900" font-size="470" text-anchor="middle" fill="{WHITE}">SELLING <tspan fill="{GREEN}">FIAT.</tspan></text>\n'
b += sig(w, h)
designs["D01-selling-fiat-tee"] = (TEE, b, "tee/hoodie front, dark garment")

# ---------------------------------------------------------------- D02
b = ""
b += stack(w / 2, 1300, ["BITCOIN", "DOESN'T FIGHT", "GOVERNMENTS."], 400, gap=0.95)
b += stack(w / 2, 3000, [("IT IGNORES", ORANGE), ("THEM.", ORANGE)], 620, gap=0.92)
b += btc_mark_inverse(w / 2, 4100, 300)
b += sig(w, h)
designs["D02-ignores-them-tee"] = (TEE, b, "tee front, dark garment")

# ---------------------------------------------------------------- D03
b = ""
b += txt(w / 2, 2000, "DON'T TRUST.", 500, fill=WHITE)
b += txt(w / 2, 2700, "VERIFY.", 820, fill=ORANGE)
b += txt(w / 2, 3300, "run your own node", 120, fill=WHITE, font=PIX, weight=400)
b += btc_mark(w / 2, 3900, 260)
b += sig(w, h)
designs["D03-dont-trust-verify-tee"] = (TEE, b, "tee front, dark garment")

# D03 sticker
sw, sh = STK
b = f'<rect x="40" y="40" width="{sw-80}" height="{sh-80}" rx="120" fill="{INK}" stroke="{ORANGE}" stroke-width="30"/>\n'
b += txt(sw / 2, 640, "DON'T TRUST.", 190, fill=WHITE)
b += txt(sw / 2, 900, "VERIFY.", 250, fill=ORANGE)
b += btc_mark(sw / 2, 1160, 120)
designs["D03-dont-trust-verify-sticker"] = (STK, b, "kiss-cut sticker 5x5 (order at 4x4)")

# ---------------------------------------------------------------- D04 sats pill
def pill(cx, cy, L, R, fs_big, fs_small):
    """capsule: left solid orange 'bitcoin 1 BTC', right dark with sat dots."""
    out = ""
    x0, y0 = cx - L / 2, cy - R
    out += f'<clipPath id="cap"><rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}"/></clipPath>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="{INK}"/>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L/2}" height="{2*R}" fill="{ORANGE}" clip-path="url(#cap)"/>\n'
    # sat dots on the right half
    import random
    random.seed(21)
    for i in range(140):
        px = cx + L * 0.04 + random.random() * (L / 2 - L * 0.10)
        py = y0 + R * 0.12 + random.random() * (R * 1.76)
        rr = R * (0.045 + random.random() * 0.035)
        out += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{rr:.0f}" fill="{ORANGE}" opacity="0.28"/>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="none" stroke="{WHITE}" stroke-width="{R*0.06}"/>\n'
    out += f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0+2*R}" stroke="{WHITE}" stroke-width="{R*0.05}"/>\n'
    # mirror: the two halves read as the same thing said twice
    out += txt(cx - L / 4, cy - R * 0.05, "1 BTC", fs_big, fill=INK)
    out += txt(cx - L / 4, cy + R * 0.45, "one bitcoin", fs_small, fill=INK, weight=600)
    out += txt(cx + L / 4, cy - R * 0.05, "100M SATS", fs_big * 0.56, fill=WHITE)
    out += txt(cx + L / 4, cy + R * 0.45, "one hundred million sats", fs_small, fill=WHITE, weight=600)
    return out

b = pill(w / 2, 2200, 3300, 620, 420, 130)
b += txt(w / 2, 3300, "1 BTC = 100,000,000 SATS", 118, fill=WHITE, font=PIX, weight=400)
b += txt(w / 2, 3560, "take your orange pill", 100, fill=ORANGE, font=PIX, weight=400)
b += sig(w, h)
designs["D04-100m-sats-pill-tee"] = (TEE, b, "tee front, dark garment")

b = pill(sw / 2, sh / 2, 1380, 300, 190, 60)
designs["D04-100m-sats-pill-sticker"] = (STK, b, "kiss-cut sticker, capsule shape")

# ---------------------------------------------------------------- D05 tick tock
def pixel_block(cx, cy, s, fill=ORANGE):
    """an 8-bit CLOCK (the Admiral: "this doesn't look like a clock") — a 16-px ring, four ticks,
    hands at ten past ten, all on the pixel grid."""
    import math
    out = ""
    n = 16
    u = s / n
    cells = set()
    for i in range(n):
        for j in range(n):
            d = math.hypot(i + 0.5 - n / 2, j + 0.5 - n / 2)
            if 6.9 <= d <= 7.9:
                cells.add((i, j))
    ticks = {(7, 1), (8, 1), (7, 14), (8, 14), (1, 7), (1, 8), (14, 7), (14, 8)}
    hands = {(7, 7), (8, 7), (7, 8), (8, 8)}
    for k in range(1, 5):   # hour hand → 10 o'clock
        hands.add((7 - int(k * 0.7), 7 - k))
    for k in range(1, 7):   # minute hand → 2 o'clock
        hands.add((8 + int(k * 0.85), 7 - int(k * 0.5)))
    for grp, col in ((cells, fill), (ticks, WHITE), (hands, WHITE)):
        for (i, j) in grp:
            out += f'<rect x="{cx - s/2 + i*u:.0f}" y="{cy - s/2 + j*u:.0f}" width="{u+0.5:.1f}" height="{u+0.5:.1f}" fill="{col}"/>\n'
    return out

b = ""
b += txt(w / 2, 1500, "TICK TOCK", 300, fill=WHITE, font=PIX, weight=400)
b += txt(w / 2, 1950, "NEXT BLOCK", 300, fill=ORANGE, font=PIX, weight=400)
b += pixel_block(w / 2, 3200, 1400)
b += txt(w / 2, 4250, "it all comes back to the block", 96, fill=WHITE, font=PIX, weight=400)
b += sig(w, h)
designs["D05-tick-tock-next-block-tee"] = (TEE, b, "tee front, dark garment; pixel face = house arcade tie")

b = f'<rect x="40" y="40" width="{sw-80}" height="{sh-80}" fill="{INK}" stroke="{ORANGE}" stroke-width="30"/>\n'
b += txt(sw / 2, 330, "TICK TOCK", 118, fill=WHITE, font=PIX, weight=400)
b += txt(sw / 2, 500, "NEXT BLOCK", 118, fill=ORANGE, font=PIX, weight=400)
b += pixel_block(sw / 2, 900, 520)
b += txt(sw / 2, 1330, "frens.earth", 48, fill=WHITE, font=PIX, weight=400)
designs["D05-tick-tock-next-block-sticker"] = (STK, b, "kiss-cut sticker, square")

# ---------------------------------------------------------------- D06 hodl
b = ""
b += txt(400, 1300, "hodl", 900, fill=WHITE, anchor="start")
b += btc_mark(3000, 1000, 320)
b += txt(400, 1560, "/ˈhɒd.əl/  ·  verb", 150, fill=ORANGE, anchor="start", weight=600, font=MONO)
b += f'<line x1="400" y1="1700" x2="{w-400}" y2="1700" stroke="{ORANGE}" stroke-width="18"/>\n'
lines = [
    ("1.", ORANGE), ("to refuse to sell one's bitcoin,", WHITE), ("whatever the chart does.", WHITE),
    ("", WHITE),
    ("2.", ORANGE), ("originally a typo.", WHITE), ("now a life philosophy.", WHITE),
    ("", WHITE),
    ("see also:", ORANGE), ("low time preference,", WHITE), ("diamond hands, 21,000,000.", WHITE),
]
y = 2000
for s, f in lines:
    if s:
        b += txt(400, y, s, 190, fill=f, anchor="start", weight=700 if f == WHITE else 900)
    y += 240
b += sig(w, h)
designs["D06-hodl-definition-tee"] = (TEE, b, "tee front, dark garment (dictionary entry)")

# ---------------------------------------------------------------- D07 ctrl key
def keycap(cx, cy, s, label, sub=None):
    out = ""
    out += f'<rect x="{cx-s/2}" y="{cy-s/2+s*0.07}" width="{s}" height="{s}" rx="{s*0.12}" fill="{ORANGE}"/>\n'
    out += f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s*0.93}" rx="{s*0.12}" fill="{WHITE}"/>\n'
    out += f'<rect x="{cx-s/2+s*0.09}" y="{cy-s/2+s*0.08}" width="{s*0.82}" height="{s*0.74}" rx="{s*0.08}" fill="none" stroke="{INK}" stroke-width="{s*0.012}" opacity="0.25"/>\n'
    out += f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s*1.07}" rx="{s*0.12}" fill="none" stroke="{INK}" stroke-width="{s*0.02}"/>\n'
    out += txt(cx - s * 0.36, cy - s * 0.18, label, s * 0.22, fill=INK, anchor="start")
    if sub:
        out += txt(cx + s * 0.02, cy + s * 0.28, sub, s * 0.46, fill=ORANGE, anchor="middle")
    return out

b = ""
b += txt(w / 2, 1000, "INFLATION IS", 380, fill=WHITE)
b += txt(w / 2, 1420, "UNDER", 380, fill=WHITE)
b += keycap(w / 2, 2650, 1700, "Ctrl", "$")
b += txt(w / 2, 3900, "— every central banker, every year", 110, fill=ORANGE, font=MONO, weight=600)
b += sig(w, h)
designs["D07-under-ctrl-tee"] = (TEE, b, "tee front, dark garment (keycap joke)")

b = keycap(sw / 2, sh / 2 - 40, 1200, "Ctrl", "$")
designs["D07-under-ctrl-sticker"] = (STK, b, "kiss-cut sticker, keycap shape")

# ---------------------------------------------------------------- D08 survival
def shield(cx, cy, s):
    p = (f'M{cx-s/2},{cy-s*0.45} L{cx+s/2},{cy-s*0.45} L{cx+s/2},{cy+s*0.05} '
         f'Q{cx+s/2},{cy+s*0.42} {cx},{cy+s*0.55} Q{cx-s/2},{cy+s*0.42} {cx-s/2},{cy+s*0.05} Z')
    out = f'<path d="{p}" fill="none" stroke="{ORANGE}" stroke-width="{s*0.09}" stroke-linejoin="round"/>\n'
    out += txt(cx, cy + s * 0.26, "₿", s * 0.6, fill=WHITE)
    return out

b = ""
b += txt(w / 2, 800, "SURVIVAL,", 460, fill=WHITE)
b += txt(w / 2, 1280, "NOT SPECULATION.", 330, fill=ORANGE)
rows = [("NO ONE CAN", "PRINT MORE."), ("NO BANK CAN", "FREEZE IT."), ("NO BORDER CAN", "STOP IT.")]
y = 2000
for a, c in rows:
    b += shield(700, y, 520)
    b += txt(1100, y - 40, a, 220, fill=WHITE, anchor="start")
    b += txt(1100, y + 220, c, 260, fill=ORANGE, anchor="start")
    y += 800
b += sig(w, h)
designs["D08-survival-not-speculation-tee"] = (TEE, b, "tee front or back print, dark garment")

# ---------------------------------------------------------------- D09 ∞/21M mark
def fraction(cx, cy, s, top=WHITE, bar=ORANGE, bot=WHITE):
    out = txt(cx, cy - s * 0.12, "∞", s * 0.95, fill=top)
    out += f'<rect x="{cx - s*0.55}" y="{cy - s*0.06}" width="{s*1.1}" height="{s*0.09}" fill="{bar}"/>\n'
    out += txt(cx, cy + s * 0.5, "21M", s * 0.5, fill=bot)
    return out

hw, hh = HAT
THREAD_ORANGE = "#E25C27"  # Printful flat-embroidery thread 1987 Orange, nearest to 624nm
HAT = (760, 700)  # cropped to the content (the Admiral: "crop this to fit")
hw, hh = HAT
b = fraction(hw / 2, hh / 2 + 20, 600, bar=THREAD_ORANGE)
designs["D09-inf-over-21m-hat"] = (HAT, b, "cap/beanie embroidery front — 3 thread colours max (white, 624 orange)")

b = f'<circle cx="{sw/2}" cy="{sh/2}" r="{sw/2-40}" fill="{INK}" stroke="{ORANGE}" stroke-width="30"/>\n'
b += fraction(sw / 2, sh / 2 + 10, 860)
designs["D09-inf-over-21m-sticker"] = (STK, b, "kiss-cut sticker, round")

b = fraction(w / 2, 2300, 2100)
b += sig(w, h)
designs["D09-inf-over-21m-tee"] = (TEE, b, "tee front (also works small, left chest)")

# ---------------------------------------------------------------- D10 not yours
b = ""
b += txt(w / 2, 900, "“MY MONEY'S", 330, fill=WHITE)
b += txt(w / 2, 1280, "IN THE BANK.”", 330, fill=WHITE)
b += txt(w / 2, 2200, "IT'S NOT", 640, fill=ORANGE)
b += txt(w / 2, 2860, "YOURS.", 640, fill=ORANGE)
b += stack(w / 2, 3500, ["you have to ask", "permission to use it."], 170, gap=1.25, fill=WHITE, weight=700)
b += txt(w / 2, 4200, "not your keys, not your coins", 96, fill=ORANGE, font=PIX, weight=400)
b += sig(w, h)
designs["D10-not-yours-tee"] = (TEE, b, "tee front, dark garment")

b = f'<rect x="40" y="40" width="{sw-80}" height="{sh-80}" rx="80" fill="{ORANGE}"/>\n'
b += txt(sw / 2, 560, "NOT YOUR", 210, fill=INK)
b += txt(sw / 2, 800, "KEYS,", 210, fill=INK)
b += txt(sw / 2, 1060, "NOT YOUR COINS.", 150, fill=WHITE)
b += btc_mark(sw / 2, 1270, 110, fill=INK, glyph_fill=ORANGE)
designs["D10-not-your-keys-sticker"] = (STK, b, "kiss-cut sticker, orange field")

# ---------------------------------------------------------------- D11 no rulers ring
def ring_text(cx, cy, r, s, size, fill):
    """the words fill the whole circle (textLength = circumference) so the gaps are even."""
    import math
    circ = 2 * math.pi * r
    return (f'<defs><path id="ring" d="M{cx-r},{cy} a{r},{r} 0 1,1 {2*r},0 a{r},{r} 0 1,1 -{2*r},0"/></defs>\n'
            f'<text font-family="{SANS}" font-weight="900" font-size="{size}" fill="{fill}">'
            f'<textPath href="#ring" startOffset="0" textLength="{circ:.0f}" lengthAdjust="spacing">{s}</textPath></text>\n')

b = btc_mark_inverse(w / 2, 2400, 900)
b += f'<circle cx="{w/2}" cy="2400" r="1150" fill="none" stroke="{WHITE}" stroke-width="24"/>\n'
b += ring_text(w / 2, 2400, 1320, "NO RULERS · 21 MILLION CAP · NO INFLATION · NO PERMISSION ·", 230, WHITE)
b += sig(w, h)
designs["D11-no-rulers-ring-tee"] = (TEE, b, "tee front, dark garment")

b = f'<circle cx="{sw/2}" cy="{sh/2}" r="{sw/2-40}" fill="{INK}" stroke="{ORANGE}" stroke-width="24"/>\n'
b += btc_mark_inverse(sw / 2, sh / 2, 360)
b += f'<circle cx="{sw/2}" cy="{sh/2}" r="460" fill="none" stroke="{WHITE}" stroke-width="12"/>\n'
b += ring_text(sw / 2, sh / 2, 540, "NO RULERS \u00b7 21 MILLION CAP \u00b7 NO INFLATION \u00b7 NO PERMISSION \u00b7 ", 78, WHITE)
designs["D11-no-rulers-ring-sticker"] = (STK, b, "kiss-cut sticker, round, dark field")


# ---------------------------------------------------------------- write + render
def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

manifest = []
for name, (size, body, note) in designs.items():
    path = f"{SRC}/{name}.svg"
    open(path, "w").write(svg(size, body))
    manifest.append({"name": name, "w": size[0], "h": size[1], "note": note,
                     "svg": os.path.relpath(path, PACK),
                     "print": f"print/{name}.png", "preview": f"preview/{name}.png"})
json.dump(manifest, open(f"{PACK}/manifest.json", "w"), indent=2)
print("wrote", len(manifest), "svgs")

if os.environ.get("RENDER", "1") == "1":
    INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]
    for m in manifest:
        s = f"{PACK}/{m['svg']}"
        # print file: transparent, full 300dpi px size (1 user unit = 1 px)
        r = run(INK_CMD + [s, "--export-type=png", f"--export-filename={PACK}/{m['print']}",
                           "--export-dpi=96", "--export-background-opacity=0"])
        if r.returncode:
            print("ERR", m["name"], r.stderr[-300:])
        # preview: dark backer, 1/4 scale
        r = run(INK_CMD + [s, "--export-type=png", f"--export-filename={PACK}/{m['preview']}",
                           "--export-dpi=24", "--export-background=#1a1a1a", "--export-background-opacity=1"])
        print("ok", m["name"])
