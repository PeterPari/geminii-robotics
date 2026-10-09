"""GEMINII brand kit: drawing library.

Everything the kit draws is built here: palette constants, Arvo text outlining
(HarfBuzz shaping + fontTools outlines, so no <text> and no font dependency in
the output), geometric primitives, and the logo construction.

Logo geometry notes (all numbers derive from the supplied Full Logo / Icon SVGs):
  * Letters G E M I N are Arvo Bold at 300 px, plain advances, baseline y=856.5.
  * The gemini glyph is the Icon.svg outline, mirror-symmetrized about x=750
    (largest deviation corrected: 4.5 of 1441 units) and placed with the same
    scale/offset as the Full Logo.
  * The gem is six concentric regular pointy-top hexagons. The original raster
    glow mask is replaced by a vector radial gradient.
"""
import json
import math
import os

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
BLACK, TEAL, WHITE = "#000000", "#00c7c5", "#ffffff"
PALETTE = (BLACK, TEAL, WHITE)
# Gem facet neutrals: logo artwork only, not part of the palette.
GEM_OFFWHITE, GEM_SILVER, GEM_DARK = "#e0e1dd", "#b3b2b2", "#494949"
GEM_NEUTRALS = (GEM_OFFWHITE, GEM_SILVER, GEM_DARK, "#373737")


def n(v):
    """Compact number formatting for SVG output."""
    s = f"{v:.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def lerp_hex(a, b, u):
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(tuple(x + (y - x) * u for x, y in zip(ra, rb)))


def luminance(h):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def wcag_level(ratio):
    if ratio >= 7:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3:
        return "AA LARGE"
    return "FAIL"


def to_hsl(h):
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0, 0, round(l * 100)
    d = mx - mn
    s = d / (1 - abs(2 * l - 1))
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return round(hh * 60), round(s * 100), round(l * 100)


def to_cmyk(h):
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    k = 1 - max(r, g, b)
    if k >= 1:
        return 0, 0, 0, 100
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)


# ---------------------------------------------------------------- fonts
class Font:
    def __init__(self, woff, ttf):
        tt = TTFont(woff)
        if not os.path.exists(ttf):
            tt.flavor = None
            tt.save(ttf)
        self.tt = TTFont(ttf)
        self.upm = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet()
        self.cap = self.tt["OS/2"].sCapHeight
        self.xh = self.tt["OS/2"].sxHeight
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(ttf)))

    def shape(self, s):
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        return [
            (self.tt.getGlyphName(i.codepoint), p.x_advance)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)
        ]

    def width(self, s, size, tracking=0.0):
        g = self.shape(s)
        return sum(a for _, a in g) * size / self.upm + tracking * size * max(len(g) - 1, 0)

    def path(self, s, x, y, size, tracking=0.0):
        k = size / self.upm
        out, cx = [], x
        for name, adv in self.shape(s):
            pen = SVGPathPen(self.gs, ntos=n)
            self.gs[name].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
            out.append(pen.getCommands())
            cx += adv * k + tracking * size
        return "".join(out)

    def wrap(self, s, size, maxw, tracking=0.0):
        lines, cur = [], ""
        for word in s.split():
            t = f"{cur} {word}".strip()
            if cur and self.width(t, size, tracking) > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines


FONT_DIR = os.path.join(HERE, "fonts")
REG = Font(os.path.join(FONT_DIR, "arvo-latin-400-normal.woff"), os.path.join(FONT_DIR, "Arvo-Regular.ttf"))
BOLD = Font(os.path.join(FONT_DIR, "arvo-latin-700-normal.woff"), os.path.join(FONT_DIR, "Arvo-Bold.ttf"))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------- page
class Page:
    """One kit page: a 1920x1080 SVG fragment with its own defs."""

    W, H = 1920, 1080

    def __init__(self, key, bg=BLACK, title=""):
        self.key, self.bg, self.title = key, bg, title
        self.defs, self.out, self._n, self._once = [], [], 0, {}

    # -- bookkeeping
    def uid(self, p="i"):
        self._n += 1
        return f"{self.key}-{p}{self._n}"

    def once(self, tag, builder):
        """Define a def once per page; builder(id) -> markup."""
        if tag not in self._once:
            i = self.uid("d")
            self.defs.append(builder(i))
            self._once[tag] = i
        return self._once[tag]

    def add(self, s):
        self.out.append(s)

    # -- primitives
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=0, rx=0, dash=None, extra=""):
        a = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'
        if rx:
            a += f' rx="{n(rx)}"'
        a += f' fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{n(sw)}"'
            if dash:
                a += f' stroke-dasharray="{dash}"'
        self.add(a + f"{extra}/>")

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0, dash=None):
        a = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{n(sw)}"'
            if dash:
                a += f' stroke-dasharray="{dash}"'
        self.add(a + "/>")

    def line(self, x1, y1, x2, y2, stroke, sw=2, dash=None, cap="butt"):
        a = f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{stroke}" stroke-width="{n(sw)}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if cap != "butt":
            a += f' stroke-linecap="{cap}"'
        self.add(a + "/>")

    def path(self, d, fill="none", stroke=None, sw=0, rule=None, extra=""):
        a = f'<path d="{d}" fill="{fill}"'
        if rule:
            a += f' fill-rule="{rule}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{n(sw)}" stroke-linejoin="round" stroke-linecap="round"'
        self.add(a + f"{extra}/>")

    def text(self, x, y, s, size, font, fill, anchor="start", tracking=0.0, upper=False, add=True):
        """Outlined text. y is the baseline. Returns (width, d)."""
        if upper:
            s = s.upper()
        w = font.width(s, size, tracking)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        d = font.path(s, x0, y, size, tracking)
        if add:
            self.add(f'<path data-t="{esc(s)}" aria-label="{esc(s)}" fill="{fill}" d="{d}"/>')
        return w

    def para(self, x, y, s, size, font, fill, width, leading, tracking=0.0, anchor="start"):
        """Wrapped paragraph; y is the first baseline. Returns total height."""
        lines = font.wrap(s, size, width, tracking)
        for i, ln in enumerate(lines):
            self.text(x, y + i * leading, ln, size, font, fill, anchor=anchor, tracking=tracking)
        return len(lines) * leading

    # -- svg assembly
    def body(self):
        return "\n".join(
            [f'<rect width="{self.W}" height="{self.H}" fill="{self.bg}"/>'] + self.out
        )

    def svg(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
            f'viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(self.title)}">'
            f"<title>{esc(self.title)}</title>{defs}{self.body()}</svg>"
        )


# ---------------------------------------------------------------- logo geometry
S300 = 300 / 2048                      # Arvo Bold at 300 px
LOGO_BASE = 856.5                      # letter baseline
G_ORIGIN = 7.0898                      # origin of the first letter (from Full Logo)
_adv = {c: BOLD.shape(c)[0][1] for c in "GEMIN"}
LETTER_X = {}
_x = G_ORIGIN
for _c in "GEMIN":
    LETTER_X[_c] = _x
    _x += _adv[_c] * S300
I_CENTER = LETTER_X["I"] + (113 + 762) / 2 * S300     # stem centre of the teal I

# gem
GEM_CX, GEM_CY = I_CENTER, 569.885
GEM_R = (51.66, 48.79, 45.89, 28.38, 25.89, 17.70, 14.64)   # outer .. core
GEM_W = math.sqrt(3) * GEM_R[0]                              # flat-to-flat width = clear-space unit X

# gemini glyph, icon space (Icon.svg), mirror-symmetric about x=750
GLYPH_ICON = (
    "M30 67.5C225 157.5 495 220.5 750 220.5C1005 220.5 1275 157.5 1470 67.5"
    "L1470 120C1395 225 1275 315 1117.5 360L1117.5 1143"
    "C1275 1188 1395 1275 1470 1362L1470 1432.5"
    "C1275 1342.5 1005 1263 750 1263C495 1263 225 1342.5 30 1432.5"
    "L30 1362C105 1275 225 1188 382.5 1143L382.5 360C225 315 105 225 30 120Z"
    "M904.5 396C825 405 675 405 595.5 396L595.5 1110C675 1101 825 1101 904.5 1110Z"
)
GLYPH_BOX = (30, 67.5, 1470, 1432.5)   # x0, y0, x1, y1 in icon space
GLYPH_K = 0.2715                        # icon space -> Full Logo space
GLYPH_TX, GLYPH_TY = 1092.742, 546.119

# overall lockup bbox in logo space
LOGO_X0 = LETTER_X["G"] + 66 * S300
LOGO_X1 = GLYPH_TX + GLYPH_K * GLYPH_BOX[2]
LOGO_Y0 = GEM_CY - GEM_R[0]
LOGO_Y1 = GLYPH_TY + GLYPH_K * GLYPH_BOX[3]
LOGO_W, LOGO_H = LOGO_X1 - LOGO_X0, LOGO_Y1 - LOGO_Y0

with open(os.path.join(HERE, "ref", "gradient_ramp.json")) as _f:
    _RAMP = json.load(_f)


def ramp_u(offset):
    """Interpolated gradient parameter u (0 = teal, 1 = far colour) at offset along the original ramp."""
    pts = _RAMP
    if offset <= pts[0][0]:
        return pts[0][1]
    for (o0, u0), (o1, u1) in zip(pts, pts[1:]):
        if offset <= o1:
            return u0 + (u1 - u0) * ((offset - o0) / (o1 - o0) if o1 > o0 else 0)
    return pts[-1][1]


def ramp_color(t, far):
    """Colour at fraction t from the left edge (0) to the right edge (1)."""
    return lerp_hex(TEAL, far, ramp_u(1 - t))


def hexagon(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z"


def gradient_def(i, far, x1=GLYPH_BOX[2], x2=GLYPH_BOX[0], steps=48):
    stops = "".join(
        f'<stop offset="{n(k / steps)}" stop-color="{lerp_hex(TEAL, far, ramp_u(k / steps))}"/>'
        for k in range(steps + 1)
    )
    return f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{n(x1)}" y1="0" x2="{n(x2)}" y2="0">{stops}</linearGradient>'


def glyph_group(page, fill):
    """The gemini glyph in icon space. fill: colour string or ('grad', far_colour)."""
    if isinstance(fill, tuple):
        gid = page.once(("grad", fill[1]), lambda i: gradient_def(i, fill[1]))
        fill = f"url(#{gid})"
    return f'<path fill="{fill}" fill-rule="evenodd" d="{GLYPH_ICON}"/>'


def gem_group(page, mode="full", color=WHITE):
    """The gem in logo space. mode 'full' (artwork) or 'mono' (single colour)."""
    r = GEM_R
    cx, cy = GEM_CX, GEM_CY
    if mode == "none":
        return ""
    if mode == "mono":
        ring = hexagon(cx, cy, r[0]) + hexagon(cx, cy, 44.0)
        core = hexagon(cx, cy, 29.5)
        return f'<path fill="{color}" fill-rule="evenodd" d="{ring}"/><path fill="{color}" d="{core}"/>'
    gid = page.once(
        "gemglow",
        lambda i: (
            f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{n(cx)}" cy="{n(cy)}" r="{r[4]}">'
            '<stop offset="0.55" stop-color="#7a7a7a"/><stop offset="0.62" stop-color="#6a6a6a"/>'
            '<stop offset="0.70" stop-color="#595959"/><stop offset="0.77" stop-color="#4b4b4b"/>'
            '<stop offset="0.85" stop-color="#414141"/><stop offset="0.93" stop-color="#3c3c3c"/>'
            '<stop offset="1" stop-color="#3a3a3a"/></radialGradient>'
        ),
    )
    layers = [
        (GEM_OFFWHITE, r[0]), (GEM_SILVER, r[1]), (TEAL, r[2]), (GEM_DARK, r[3]),
        (f"url(#{gid})", r[4]), (GEM_OFFWHITE, r[5]), (WHITE, r[6]),
    ]
    return "".join(f'<path fill="{f}" d="{hexagon(cx, cy, rr)}"/>' for f, rr in layers)


def letters_group(page, color, i_color):
    out = []
    for c in "GEMIN":
        col = i_color if c == "I" else color
        d = BOLD.path(c, LETTER_X[c], LOGO_BASE, 300)
        if isinstance(col, tuple):   # ("outline", colour, stroke width): misuse example only
            out.append(f'<path fill="none" stroke="{col[1]}" stroke-width="{col[2]}" stroke-linejoin="round" d="{d}"/>')
        else:
            out.append(f'<path fill="{col}" d="{d}"/>')
    return "".join(out)


def logo_content(page, letters=WHITE, i_color=TEAL, glyph=("grad", WHITE), gem="full", gem_color=WHITE):
    """Wordmark in logo space (origin = original Full Logo artboard coordinates)."""
    g = glyph_group(page, glyph)
    return (
        letters_group(page, letters, i_color)
        + gem_group(page, gem, gem_color)
        + f'<g transform="matrix({GLYPH_K} 0 0 {GLYPH_K} {GLYPH_TX} {GLYPH_TY})">{g}</g>'
    )


VARIANTS = {
    "full-dark": dict(letters=WHITE, i_color=TEAL, glyph=("grad", WHITE), gem="full"),
    "full-light": dict(letters=BLACK, i_color=TEAL, glyph=("grad", BLACK), gem="full"),
    "mono-white": dict(letters=WHITE, i_color=WHITE, glyph=WHITE, gem="mono", gem_color=WHITE),
    "mono-black": dict(letters=BLACK, i_color=BLACK, glyph=BLACK, gem="mono", gem_color=BLACK),
}


def place_logo(page, x, y, w, variant="full-dark", extra_transform="", **over):
    """Draw the wordmark with its bbox top-left at (x, y) and width w. Returns (k, height)."""
    opts = dict(VARIANTS[variant]) if variant else {}
    opts.update(over)
    k = w / LOGO_W
    tf = f"translate({n(x - LOGO_X0 * k)} {n(y - LOGO_Y0 * k)}) scale({k:.6f})"
    if extra_transform:
        tf = f"{extra_transform} {tf}"
    page.add(f'<g role="img" aria-label="GEMINII wordmark" transform="{tf}">{logo_content(page, **opts)}</g>')
    return k, LOGO_H * k


def place_glyph(page, cx, cy, w, fill=("grad", WHITE)):
    """Draw the gemini glyph centred at (cx, cy), total width w."""
    k = w / (GLYPH_BOX[2] - GLYPH_BOX[0])
    gcx = (GLYPH_BOX[0] + GLYPH_BOX[2]) / 2
    gcy = (GLYPH_BOX[1] + GLYPH_BOX[3]) / 2
    tf = f"translate({n(cx - gcx * k)} {n(cy - gcy * k)}) scale({k:.6f})"
    page.add(f'<g role="img" aria-label="GEMINII icon" transform="{tf}">{glyph_group(page, fill)}</g>')
    return k, (GLYPH_BOX[3] - GLYPH_BOX[1]) * k


def place_gem(page, cx, cy, w, mode="full", color=WHITE):
    """Draw the gem centred at (cx, cy) with flat-to-flat width w."""
    k = w / GEM_W
    tf = f"translate({n(cx - GEM_CX * k)} {n(cy - GEM_CY * k)}) scale({k:.6f})"
    page.add(f'<g role="img" aria-label="GEMINII gem" transform="{tf}">{gem_group(page, mode, color)}</g>')
    return k
