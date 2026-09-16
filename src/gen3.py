#!/usr/bin/env python3
"""Sticker packs 02 (the Admiral, 2026-09-15): "multiple items on the stickers, multiple bitcoin
logos, different sizes, the coins, maybe a rocket ship."

Printful kiss-cut STICKER SHEET (product 505): one file 1750×2482 px @ 300 dpi (5.83×8.27 in),
transparent background, Printful kiss-cuts around every element and adds a 0.12 in white border —
so elements stay ≥ 0.3 in (90 px) apart. Die-cut singles (957) and holographic (673): square files
at 300 dpi (2–6 in), transparent, cut follows the shape.

Every element is our own vector: coins (flat, inverse, ring, pixel, gold), a pixel rocket, a moon,
stars, the ₿ umbrella (the Admiral's umbrella reference, redrawn), the sats pile, the pixel clock,
and word tiles. Gold only on the coin that IS money (house law).
Outputs → ../print3/sheets/*.png · ../print3/singles/*.png · ../print3/preview/*.png
"""
import os, math, random, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
OUT = f"{PACK}/print3"
ORANGE, WHITE, INK, GREEN, GOLD, GOLD_DK = "#ff4f00", "#ffffff", "#0b0b0b", "#5ef78a", "#f7c948", "#8a5a00"
SANS, PIX = "Adwaita Sans", "Press Start 2P"
INK_CMD = ["flatpak", "run", "org.inkscape.Inkscape"]
SHEET = (1750, 2482)


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{body}\n</svg>\n'


def txt(x, y, s, size, fill=WHITE, font=SANS, weight=900, anchor="middle", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>\n'


# ---------------------------------------------------------------- elements (each centred on cx,cy)
def coin_flat(cx, cy, r, disc=ORANGE, glyph=INK):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{disc}"/>\n' + txt(cx, cy + r * 0.62, "₿", r * 1.7, fill=glyph, extra=f'transform="rotate(-12 {cx} {cy})"')


def coin_inverse(cx, cy, r):
    return coin_flat(cx, cy, r, disc=INK, glyph=ORANGE)


def coin_ring(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}"/>\n<circle cx="{cx}" cy="{cy}" r="{r*0.86}" fill="none" stroke="{ORANGE}" stroke-width="{r*0.09}"/>\n'
            + txt(cx, cy + r * 0.5, "₿", r * 1.4, fill=WHITE, extra=f'transform="rotate(-12 {cx} {cy})"'))


def coin_gold(cx, cy, r, uid):
    """the one that IS money — gold, ring words, ₿ struck in the middle."""
    ring_r = r * 0.78
    circ = 2 * math.pi * ring_r
    words = "BITCOIN · DECENTRALIZED · PEER TO PEER · 21,000,000 · "
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GOLD}"/>\n'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.93}" fill="none" stroke="{GOLD_DK}" stroke-width="{r*0.025}"/>\n'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.64}" fill="none" stroke="{GOLD_DK}" stroke-width="{r*0.025}"/>\n'
            f'<defs><path id="g{uid}" d="M{cx-ring_r},{cy} a{ring_r},{ring_r} 0 1,1 {2*ring_r},0 a{ring_r},{ring_r} 0 1,1 -{2*ring_r},0"/></defs>\n'
            f'<text font-family="{SANS}" font-weight="900" font-size="{r*0.16}" fill="{GOLD_DK}"><textPath xlink:href="#g{uid}" href="#g{uid}" textLength="{circ:.0f}" lengthAdjust="spacing">{words}</textPath></text>\n'
            + txt(cx, cy + r * 0.4, "₿", r * 1.1, fill=GOLD_DK, extra=f'transform="rotate(-12 {cx} {cy})"'))


def pixels(cx, cy, u, rows, palette):
    """rows of characters; palette maps char → colour; '.' = empty. Centred."""
    h, w = len(rows), max(len(r) for r in rows)
    x0, y0 = cx - w * u / 2, cy - h * u / 2
    out = ""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in palette:
                out += f'<rect x="{x0 + i*u:.1f}" y="{y0 + j*u:.1f}" width="{u+0.6:.1f}" height="{u+0.6:.1f}" fill="{palette[ch]}"/>\n'
    return out


ROCKET = [
    "......OO......",
    ".....OOOO.....",
    "....OOOOOO....",
    "....OOOOOO....",
    "...WWWWWWWW...",
    "...WWWWWWWW...",
    "...WWWWWWWW...",
    "...WWBBBBWW...",
    "...WWBBBBWW...",
    "...WWWBBWWW...",
    "...WWWWWWWW...",
    "...WWWWWWWW...",
    "..OWWWWWWWWO..",
    ".OOWWWWWWWWOO.",
    "OOOWWWWWWWWOOO",
    "OOO.WWWWWW.OOO",
    "....FFFFFF....",
    ".....YYYY.....",
    "....FFFFFF....",
    ".....YYYY.....",
    "......FF......",
]
ROCKET_PAL = {"O": ORANGE, "W": WHITE, "B": ORANGE, "F": ORANGE, "Y": "#ffd166"}


def rocket(cx, cy, u):
    body = pixels(cx, cy, u, ROCKET, ROCKET_PAL)
    # the porthole ₿ sits over the B block
    return body + txt(cx, cy - u * 1.6, "₿", u * 4.2, fill=INK)


def moon(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}"/>\n'
            f'<circle cx="{cx - r*0.25}" cy="{cy - r*0.2}" r="{r*0.18}" fill="#c9c4bb"/>\n'
            f'<circle cx="{cx + r*0.3}" cy="{cy + r*0.25}" r="{r*0.13}" fill="#c9c4bb"/>\n'
            f'<circle cx="{cx + r*0.15}" cy="{cy - r*0.45}" r="{r*0.09}" fill="#c9c4bb"/>\n'
            + txt(cx - r * 0.02, cy + r * 0.35, "₿", r * 0.9, fill=ORANGE))


def star(cx, cy, r, fill=WHITE):
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.4
        pts.append(f"{cx + rr*math.sin(a):.1f},{cy - rr*math.cos(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>\n'


def umbrella(cx, cy, s):
    """the ₿ umbrella — a canopy of five scallops, a J handle, ₿ on the cloth."""
    top = cy - s * 0.35
    rr = s / 2
    d = f"M{cx-rr},{top} A{rr},{rr} 0 0,1 {cx+rr},{top} "
    n = 5
    seg = 2 * rr / n
    for k in range(n):
        x1 = cx + rr - (k + 1) * seg
        d += f"A{seg/2},{seg/2*0.9} 0 0,1 {x1:.1f},{top} "
    d += "Z"
    out = f'<path d="{d}" fill="{ORANGE}" stroke="{INK}" stroke-width="{s*0.02}"/>\n'
    out += f'<line x1="{cx}" y1="{top - rr*0.02}" x2="{cx}" y2="{top - rr*0.14}" stroke="{INK}" stroke-width="{s*0.03}" stroke-linecap="round"/>\n'
    out += f'<path d="M{cx},{top} V{cy + s*0.42} a{s*0.09},{s*0.09} 0 0,1 -{s*0.18},0" fill="none" stroke="{INK}" stroke-width="{s*0.035}" stroke-linecap="round"/>\n'
    out += txt(cx, top - rr * 0.3, "₿", s * 0.34, fill=INK)
    return out


def sats_pile(cx, cy, r, seed=21):
    random.seed(seed)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}"/>\n'
    for _ in range(int(r * r / 260)):
        a, d = random.random() * 2 * math.pi, math.sqrt(random.random()) * r * 0.9
        px, py = cx + d * math.cos(a), cy + d * math.sin(a)
        out += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r*0.045 + random.random()*r*0.03:.1f}" fill="{ORANGE}"/>\n'
    out += f'<rect x="{cx - r*0.62}" y="{cy - r*0.2}" width="{r*1.24}" height="{r*0.42}" rx="{r*0.08}" fill="{INK}"/>\n'
    out += txt(cx, cy + r * 0.11, "100M SATS", r * 0.26, fill=WHITE)
    return out


def clock(cx, cy, s):
    n, u = 16, s / 16
    cells = {(i, j) for i in range(n) for j in range(n) if 6.9 <= math.hypot(i + 0.5 - 8, j + 0.5 - 8) <= 7.9}
    ticks = {(7, 1), (8, 1), (7, 14), (8, 14), (1, 7), (1, 8), (14, 7), (14, 8)}
    hands = {(7, 7), (8, 7), (7, 8), (8, 8)} | {(7 - int(k * 0.7), 7 - k) for k in range(1, 5)} | {(8 + int(k * 0.85), 7 - int(k * 0.5)) for k in range(1, 7)}
    out = f'<circle cx="{cx}" cy="{cy}" r="{s*0.56}" fill="{INK}"/>\n'
    for grp, col in ((cells, ORANGE), (ticks, WHITE), (hands, WHITE)):
        for (i, j) in grp:
            out += f'<rect x="{cx - s/2 + i*u:.1f}" y="{cy - s/2 + j*u:.1f}" width="{u+0.6:.1f}" height="{u+0.6:.1f}" fill="{col}"/>\n'
    return out


def tile(cx, cy, w, h, lines, size, fill=INK, ink=WHITE, accent=ORANGE, font=SANS, rx=None):
    """a word tile: dark rounded box, lines of type; a (text, colour) pair colours a line."""
    rx = rx if rx is not None else h * 0.18
    out = f'<rect x="{cx - w/2}" y="{cy - h/2}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>\n'
    n = len(lines)
    for k, ln in enumerate(lines):
        s_, col = (ln if isinstance(ln, tuple) else (ln, ink))
        y = cy + (k - (n - 1) / 2) * size * 1.15 + size * 0.36
        out += txt(cx, y, s_, size, fill=col, font=font, weight=900 if font == SANS else 400)
    return out


def chip(cx, cy, s, ink=WHITE):
    return tile(cx, cy, s * 1.9, s * 0.9, [("21M", ink)], s * 0.55, fill=ORANGE)


# ---------------------------------------------------------------- SHEET A — the coin pack
W, H = SHEET
b = ""
b += coin_flat(430, 420, 300)                      # the big one, 2 in
b += coin_gold(1250, 420, 300, "A")                # the money one
b += coin_inverse(300, 1000, 180)
b += coin_ring(760, 1000, 180)
b += pixels(1300, 1000, 22, ['....OOOOOO....', '..OOOOOOOOOO..', '.OOOOOOOOOOOO.', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', 'OOOOOOOOOOOOOO', '.OOOOOOOOOOOO.', '..OOOOOOOOOO..', '....OOOOOO....'], {"O": ORANGE}) + txt(1300, 1070, "₿", 200, fill=INK, extra='transform="rotate(-12 1300 1000)"')
b += rocket(330, 1650, 30)
b += moon(880, 1600, 210)
b += star(1160, 1400, 40) + star(1290, 1520, 26) + star(1220, 1720, 34, ORANGE) + star(1380, 1660, 22)
b += umbrella(1480, 1620, 420)
b += sats_pile(430, 2200, 210)
b += clock(880, 2200, 300)
b += chip(1420, 2200, 200)
open(f"{OUT}/sheets/sheet-A-coins.svg", "w") if os.path.isdir(f"{OUT}/sheets") else None
SHEETS = {"sheet-A-coins": b}

# ---------------------------------------------------------------- SHEET B — the sayings pack
b = ""
b += tile(560, 300, 980, 360, ["DON'T TRUST.", ("VERIFY.", ORANGE)], 150)
b += coin_flat(1400, 300, 200)
b += tile(430, 760, 720, 320, ["NOT YOUR", "KEYS."], 130, fill=ORANGE, ink=INK)
b += tile(1230, 760, 820, 320, ["TICK TOCK", ("NEXT BLOCK", ORANGE)], 84, font=PIX)
b += coin_inverse(330, 1200, 170)
b += tile(1080, 1200, 1140, 360, ["THE SATS WON'T", ("STACK THEMSELVES.", GREEN)], 112)
b += tile(430, 1660, 720, 340, [("∞", WHITE), ("21M", WHITE)], 130, fill=INK)
b += f'<rect x="{430-180}" y="{1660-14}" width="360" height="26" fill="{ORANGE}"/>\n'
b += tile(1230, 1660, 820, 340, ["hodl", ("(verb)", ORANGE)], 150)
b += tile(560, 2130, 980, 360, ["NO RULERS.", ("NO INFLATION.", ORANGE)], 118)
b += coin_ring(1400, 2130, 200)
SHEETS["sheet-B-sayings"] = b

# ---------------------------------------------------------------- SHEET C — the rocket pack
b = ""
b += rocket(560, 640, 52)
b += moon(1330, 480, 300)
b += star(1080, 260, 60) + star(1560, 900, 44) + star(1000, 900, 36, ORANGE) + star(1650, 200, 30)
b += tile(875, 1330, 1500, 360, ["TO THE MOON", ("ONE BLOCK AT A TIME", ORANGE)], 120)
b += coin_flat(330, 1900, 220) + coin_gold(875, 1900, 220, "C") + coin_inverse(1420, 1900, 220)
b += tile(875, 2300, 1300, 260, [("stack sats · run a node · hodl", WHITE)], 78)
SHEETS["sheet-C-rocket"] = b

# ---------------------------------------------------------------- singles (die-cut / holographic), 1200×1200 = 4 in
SINGLES = {
    "single-coin-flat": coin_flat(600, 600, 560),
    "single-coin-inverse": coin_inverse(600, 600, 560),
    "single-coin-gold": coin_gold(600, 600, 560, "S"),
    "single-rocket": rocket(600, 600, 52),
    "single-moon": moon(600, 600, 540),
    "single-umbrella": umbrella(600, 640, 760),
    "single-sats-pile": sats_pile(600, 600, 560),
    "single-clock": clock(600, 600, 1000),
}


def render(name, w, h, body, sub):
    d = f"{OUT}/{sub}"
    os.makedirs(d, exist_ok=True)
    src = f"{d}/{name}.svg"
    open(src, "w").write(svg(w, h, body))
    for kind, extra in (("png", ["--export-background-opacity=0"]), ):
        r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={d}/{name}.png", "--export-dpi=96", *extra], capture_output=True, text=True)
        print("ERR" if r.returncode else "ok", sub, name, f"{w}x{h}", r.stderr[-120:] if r.returncode else "")
    os.makedirs(f"{OUT}/preview", exist_ok=True)
    subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={OUT}/preview/{name}.png", "--export-dpi=28", "--export-background=#1a1a1a", "--export-background-opacity=1"], capture_output=True, text=True)


if __name__ == "__main__":
    for name, body in SHEETS.items():
        render(name, W, H, body, "sheets")
    for name, body in SINGLES.items():
        render(name, 1200, 1200, body, "singles")
    print("done →", OUT)
