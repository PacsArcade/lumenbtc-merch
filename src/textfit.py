"""Text measuring for the merch scripts (Pango, no model, no GPU). Added 970005 for the Admiral's marks:
fit words inside a tile, close the gaps on ring text."""
import math
import gi
gi.require_version('Pango', '1.0'); gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

TILT = 14  # degrees clockwise: the standard bitcoin logo leans RIGHT (up and to the right)
_ctx = PangoCairo.FontMap.get_default().create_context()


def width(text, family="Adwaita Sans", weight=900, size=100.0):
    """advance width in px of text at size (no letter-spacing)."""
    w = {900: "Heavy", 800: "Heavy", 700: "Bold", 600: "Semi-Bold", 400: ""}.get(weight, "Bold")
    d = Pango.FontDescription(f"{family} {w} 1000px".replace("  ", " "))
    lay = Pango.Layout(_ctx)
    lay.set_font_description(d)
    lay.set_text(text, -1)
    return lay.get_size()[0] / Pango.SCALE * size / 1000.0


def fit(text, max_w, size, family="Adwaita Sans", weight=900):
    """largest size <= size so the text is at most max_w wide."""
    w = width(text, family, weight, size)
    return size if w <= max_w else size * max_w / w


def ink(text, family="Adwaita Sans", weight=900, size=100.0):
    """973900: the inked box of text at size, relative to the anchor of an SVG <text text-anchor="middle">:
    (x0, y0, x1, y1) with x from the middle of the advance and y from the baseline (negative = above)."""
    w = {900: "Heavy", 800: "Heavy", 700: "Bold", 600: "Semi-Bold", 400: ""}.get(weight, "Bold")
    d = Pango.FontDescription(f"{family} {w} 1000px".replace("  ", " "))
    lay = Pango.Layout(_ctx)
    lay.set_font_description(d)
    lay.set_text(text, -1)
    ink_r, log_r = lay.get_extents()
    base = lay.get_baseline()
    k = size / 1000.0 / Pango.SCALE
    mid = log_r.x + log_r.width / 2
    return ((ink_r.x - mid) * k, (ink_r.y - base) * k, (ink_r.x + ink_r.width - mid) * k, (ink_r.y + ink_r.height - base) * k)


def ring_spacing(text, r, size, family="Adwaita Sans", weight=900):
    """letter-spacing that makes text close exactly round a circle of radius r."""
    circ = 2 * math.pi * r
    return (circ - width(text, family, weight, size)) / len(text)


def ring_size(text, r, family="Adwaita Sans", weight=900, ls_frac=0.05, max_size=None):
    """font size at which a small even spacing (ls_frac of the size) closes the ring."""
    circ = 2 * math.pi * r
    k = width(text, family, weight, 1.0)
    s = circ / (k + len(text) * ls_frac)
    return min(s, max_size) if max_size else s
