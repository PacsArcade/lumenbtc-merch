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
import textfit
from textfit import TILT   # 970005: every B leans RIGHT (up and to the right), 14 degrees

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
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{disc}"/>\n' + txt(cx, cy + r * 0.62, "₿", r * 1.7, fill=glyph, extra=f'transform="rotate({TILT} {cx} {cy})"')


def coin_inverse(cx, cy, r):
    return coin_flat(cx, cy, r, disc=INK, glyph=ORANGE)


def coin_ring(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}"/>\n<circle cx="{cx}" cy="{cy}" r="{r*0.86}" fill="none" stroke="{ORANGE}" stroke-width="{r*0.09}"/>\n'
            + txt(cx, cy + r * 0.5, "₿", r * 1.4, fill=WHITE, extra=f'transform="rotate({TILT} {cx} {cy})"'))


def coin_gold(cx, cy, r, uid):
    """the one that IS money — gold, ring words, ₿ struck in the middle."""
    # 973900 (the Admiral: "big gap between the bitcoin and the 21000000 numbers, make the letters bigger so the spaces
    # are even around the coin"): one gap G everywhere — rim -> top of the words -> inner ring -> the B. The words are
    # as big as the ring allows (thin spaces round the dots, a tight even spacing), the inner ring sits G under them,
    # and the B grows to G inside the inner ring. The circumference caps the word size, so the B and ring move instead.
    words = "BITCOIN · DECENTRALIZED · PEER TO PEER · 21,000,000 · "
    sw, G = r * 0.025, r * 0.05
    rim = r * 0.93
    cap = -textfit.ink("BITCOIN", size=1.0)[1]
    a = textfit.ring_size(words, 1000.0, ls_frac=0.03) / 1000.0     # size per unit of radius
    ring_r = (rim - sw / 2 - G) / (1 + cap * a)                     # baseline radius of the words
    fsz = a * ring_r
    ls = textfit.ring_spacing(words, ring_r, fsz)
    desc = textfit.ink(words, size=fsz)[3]                           # the commas hang below the baseline
    inner = ring_r - desc - G - sw / 2                               # centre line of the inner ring
    x0, y0, x1, y1 = textfit.ink("₿", size=1.0)
    reach = 0.885 * math.hypot((x1 - x0) / 2, (y1 - y0) / 2)         # farthest ink from the B's centre, per unit size (measured on the render)
    bs = (inner - sw / 2 - G) / reach
    bx, by = cx - (x0 + x1) / 2 * bs, cy - (y0 + y1) / 2 * bs            # text anchor that puts the B's ink centre on the coin centre
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GOLD}"/>\n'
            f'<circle cx="{cx}" cy="{cy}" r="{rim}" fill="none" stroke="{GOLD_DK}" stroke-width="{sw}"/>\n'
            f'<circle cx="{cx}" cy="{cy}" r="{inner:.1f}" fill="none" stroke="{GOLD_DK}" stroke-width="{sw}"/>\n'
            f'<defs><path id="g{uid}" d="M{cx-ring_r:.1f},{cy} a{ring_r:.1f},{ring_r:.1f} 0 1,1 {2*ring_r:.1f},0 a{ring_r:.1f},{ring_r:.1f} 0 1,1 -{2*ring_r:.1f},0"/></defs>\n'
            f'<text font-family="{SANS}" font-weight="900" font-size="{fsz:.1f}" letter-spacing="{ls:.2f}" fill="{GOLD_DK}"><textPath xlink:href="#g{uid}" href="#g{uid}">{words}</textPath></text>\n'
            + txt(f"{bx:.1f}", f"{by:.1f}", "₿", f"{bs:.1f}", fill=GOLD_DK, extra=f'transform="rotate({TILT} {cx} {cy})"'))


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
    return body + txt(cx, cy - u * 1.6, "₿", u * 4.2, fill=INK, extra=f'transform="rotate({TILT} {cx} {cy - u * 3.1})"')


MOON_N = 16
MOON_CRATERS = {(3, 4), (4, 4), (3, 5), (4, 5), (11, 3), (12, 3), (11, 4), (11, 10), (12, 10), (11, 11), (12, 11), (5, 12), (6, 12), (5, 13)}


def moon(cx, cy, r):
    """970005 (the Admiral: "a block moon to match the rocket style"): a 16 x 16 pixel disc of white blocks like the
    rocket's body, grey crater blocks, the orange B leaning right. Same blocky seams as the rocket."""
    n = MOON_N
    u = 2 * r / n
    out = ""
    for j in range(n):
        for i in range(n):
            if math.hypot(i + 0.5 - n / 2, j + 0.5 - n / 2) <= n / 2 - 0.1:
                col = "#c9c4bb" if (i, j) in MOON_CRATERS else WHITE
                out += f'<rect x="{cx - r + i*u:.1f}" y="{cy - r + j*u:.1f}" width="{u+0.6:.1f}" height="{u+0.6:.1f}" fill="{col}"/>\n'
    out += txt(cx, cy + r * 0.3, "₿", r * 0.85, fill=ORANGE, extra=f'transform="rotate({TILT} {cx} {cy})"')
    return out


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
    out += txt(cx, top - rr * 0.3, "₿", s * 0.34, fill=INK, extra=f'transform="rotate({TILT} {cx} {top - rr * 0.3 - s * 0.12})"')
    return out


def pill(cx, cy, L, R, fs_big, fs_small, uid="p"):
    """970005: the 1 BTC = 100M SATS pill (same art as D04), used where the sats pile was. Every line is fitted inside its
    half with a buffer; the sat dots are clipped to the capsule."""
    out = ""
    x0, y0 = cx - L / 2, cy - R
    out += f'<clipPath id="cap{uid}"><rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}"/></clipPath>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="{INK}"/>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L/2}" height="{2*R}" fill="{ORANGE}" clip-path="url(#cap{uid})"/>\n'
    rnd = random.Random(21)
    for _ in range(int(140 * L / 1380)):
        px_ = cx + L * 0.04 + rnd.random() * (L / 2 - L * 0.10)
        py_ = y0 + R * 0.12 + rnd.random() * (R * 1.76)
        rr = R * (0.045 + rnd.random() * 0.035)
        out += f'<circle cx="{px_:.0f}" cy="{py_:.0f}" r="{rr:.0f}" fill="{ORANGE}" opacity="0.28" clip-path="url(#cap{uid})"/>\n'
    out += f'<rect x="{x0}" y="{y0}" width="{L}" height="{2*R}" rx="{R}" fill="none" stroke="{WHITE}" stroke-width="{R*0.06}"/>\n'
    out += f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0+2*R}" stroke="{WHITE}" stroke-width="{R*0.05}"/>\n'
    room = L / 2 * 0.80
    f = textfit.fit
    out += txt(cx - L / 4, cy - R * 0.05, "1 BTC", f("1 BTC", room, fs_big), fill=INK)
    out += txt(cx - L / 4, cy + R * 0.45, "one bitcoin", f("one bitcoin", room, fs_small, weight=600), fill=INK, weight=600)
    out += txt(cx + L / 4, cy - R * 0.05, "100M SATS", f("100M SATS", room, fs_big * 0.56), fill=WHITE)
    out += txt(cx + L / 4, cy + R * 0.45, "one hundred million sats", f("one hundred million sats", room, fs_small, weight=600), fill=WHITE, weight=600)
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
    # 970005: one size for every line, shrunk until the widest line sits inside the tile with a buffer (the Admiral:
    # "words go outside the sticker"); the buffer is 11% of the tile width on each side (never under 70 px).
    fam, wt = ("Adwaita Sans", 900) if font == SANS else ("Press Start 2P", 400)
    room = w - 2 * max(w * 0.11, 70)   # 973900: 7% -> 11% (the Admiral: "very close to the edges on the next block")
    size = min([size] + [textfit.fit(l[0] if isinstance(l, tuple) else l, room, size, fam, wt) for l in lines])
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
# 970005 (the Admiral: "the corners are clipped on the right and left, please extend them"): the old rows had flat
# vertical sides with cut corners; this is a true 16 x 16 pixel circle, the B leaning right.
PIXCOIN = ["".join("O" if math.hypot(i + 0.5 - 8, j + 0.5 - 8) <= 8.0 else "." for i in range(16)) for j in range(16)]
b += pixels(1300, 1000, 20, PIXCOIN, {"O": ORANGE}) + txt(1300, 1075, "₿", 210, fill=INK, extra=f'transform="rotate({TILT} 1300 1000)"')
b += rocket(330, 1650, 30)
b += moon(880, 1600, 210)
b += star(1160, 1400, 40) + star(1290, 1520, 26) + star(1220, 1720, 34, ORANGE) + star(1380, 1660, 22)
b += umbrella(1480, 1620, 420)
b += pill(436, 2200, 600, 130, 96, 36, "A")    # 970005: the 1 BTC = 100M sats pill replaces the sats pile
b += clock(1004, 2200, 300)
b += chip(1443, 2200, 180)
# 970005: the old line here, open(...sheet-A-coins.svg, "w"), truncated the sheet svg on every import; removed (render() writes it)
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
b += star(975, 180, 60) + star(1560, 900, 44) + star(1000, 900, 36, ORANGE) + star(1650, 200, 30)
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
    "single-pill-1btc-100m-sats": pill(600, 600, 1120, 270, 300, 80, "S"),   # 970005: replaces single-sats-pile
    "single-clock": clock(600, 600, 1000),
}


PROOF = os.environ.get("PROOF_DIR")   # 970005: proof mode renders only the names in PROOF_ONLY into PROOF_DIR; print3/ is left as it was
ONLY = set(os.environ.get("PROOF_ONLY", "").split(",")) - {""}
WORK = os.environ.get("WORK_DIR", "/tmp")


def render(name, w, h, body, sub):
    if PROOF:
        if name not in ONLY:
            return
        os.makedirs(WORK, exist_ok=True)
        src = f"{WORK}/{name}.svg"
        open(src, "w").write(svg(w, h, body))
        r = subprocess.run(INK_CMD + [src, "--export-type=png", f"--export-filename={PROOF}/{name}.png", "--export-dpi=96", "--export-background-opacity=0"], capture_output=True, text=True)
        print("ERR" if r.returncode else "ok", name, f"{w}x{h}", r.stderr[-120:] if r.returncode else "")
        return
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
