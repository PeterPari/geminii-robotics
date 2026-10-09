"""GEMINII brand kit builder.

    python3 src/build.py            # writes dist/

Outputs:
    dist/GEMINII_Brandkit.svg       master, all pages stacked
    dist/pages/NN-name.svg          one SVG per page (1920 x 1080)
    dist/logos/*.svg                production logo assets (transparent, tight-cropped: add 1X clear space when placing)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kitlib import *  # noqa: E402,F401,F403
import kitlib as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.environ.get("GEMINII_KIT_DIST") or os.path.join(ROOT, "dist")
M, W, H = 96, K.Page.W, K.Page.H
TOTAL = 12
SECTIONS = [("01", "Logo", 3, 6), ("02", "Color", 7, 8), ("03", "Typography", 9, 10), ("04", "UI Components", 11, 12)]
B, R = K.BOLD, K.REG


def ink(dark):
    return WHITE if dark else BLACK


def paper(dark):
    return BLACK if dark else WHITE


def chrome(p, num, section, title, dark):
    fg = ink(dark)
    p.text(M, 112, section, 20, B, fg, tracking=0.14, upper=True)
    p.text(W - M, 112, f"{num:02d} / {TOTAL:02d}", 20, R, fg, anchor="end", tracking=0.14)
    p.rect(M, 134, 72, 6, fill=TEAL)
    p.text(M, 236, title, 84, B, fg, upper=True)
    place_logo(p, M, 972, 150, "mono-white" if dark else "mono-black")
    p.text(W - M, 1000, "BRAND KIT 2026", 18, R, fg, anchor="end", tracking=0.14)


def label(p, x, y, s, fg, size=16, anchor="start", font=B):
    return p.text(x, y, s, size, font, fg, anchor=anchor, tracking=0.14, upper=True)


def tile(p, x, y, w, h, fill, stroke=None, sw=2, name=None, sub=None, fg=None):
    p.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw)
    if name:
        label(p, x + 24, y + 38, name, fg)
    if sub:
        p.text(x + 24, y + 64, sub, 16, R, fg)


def badge_x(p, cx, cy, r=20):
    """Circle with a cross: used to mark misuse."""
    p.circle(cx, cy, r, fill=WHITE, stroke=BLACK, sw=3)
    d = r * 0.42
    p.line(cx - d, cy - d, cx + d, cy + d, BLACK, 4, cap="round")
    p.line(cx - d, cy + d, cx + d, cy - d, BLACK, 4, cap="round")


# =============================================================== pages
def page_cover():
    p = Page("p01", BLACK, "GEMINII Brand Kit")
    w = 1240
    place_logo(p, (W - w) / 2, 290, w, "full-dark")
    p.rect(W / 2 - 48, 730, 96, 6, fill=TEAL)
    p.text(W / 2, 812, "BRAND KIT", 40, B, WHITE, anchor="middle", tracking=0.5)
    p.text(M, 1000, "VERSION 1.0", 20, R, WHITE, tracking=0.14)
    p.text(W - M, 1000, "2026", 20, R, WHITE, anchor="end", tracking=0.14)
    return p


def page_contents():
    p = Page("p02", WHITE, "Contents")
    chrome(p, 2, "Brand kit", "Contents", False)
    items = [(num, name, f"PAGES {a_:02d} TO {b_:02d}") for num, name, a_, b_ in SECTIONS]
    y0, rh, xr = 330, 150, 1260
    for i, (num, name, pages) in enumerate(items):
        y = y0 + i * rh
        p.line(M, y, xr, y, BLACK, 3)
        p.circle(M + 48, y + 75, 40, fill=TEAL, stroke=BLACK, sw=4)
        p.text(M + 48, y + 75 + 11, num, 32, B, BLACK, anchor="middle")
        p.text(M + 130, y + 75 + 22, name, 64, B, BLACK, upper=True)
        p.text(xr, y + 75 + 7, pages, 20, R, BLACK, anchor="end", tracking=0.14)
    p.line(M, y0 + 4 * rh, xr, y0 + 4 * rh, BLACK, 3)
    cx = 1640
    p.circle(cx, 400, 100, fill=BLACK, stroke=BLACK, sw=4)
    p.circle(cx, 620, 100, fill=TEAL, stroke=BLACK, sw=4)
    p.circle(cx, 840, 100, fill=WHITE, stroke=BLACK, sw=4)
    return p


def page_suite():
    p = Page("p03", BLACK, "Logo suite")
    chrome(p, 3, "01 Logo", "Logo suite", True)
    # primary wordmark
    y1, h1 = 290, 340
    tile(p, M, y1, 1728, h1, "none", WHITE, 2, "Primary wordmark", "Full color on black", WHITE)
    w = 880
    place_logo(p, (W - w) / 2, y1 + 56 + (h1 - 56 - w / LOGO_W * LOGO_H) / 2, w, "full-dark")
    # row 2
    y2, h2, tw, gap = 660, 280, 552, 36
    cy = y2 + 160
    xs = [M + i * (tw + gap) for i in range(3)]
    # icon
    tile(p, xs[0], y2, tw, h2, "none", WHITE, 2, "Icon", "Gemini glyph, gradient", WHITE)
    place_glyph(p, xs[0] + tw / 2, cy + 22, 168, ("grad", WHITE))
    # profile mark
    tile(p, xs[1], y2, tw, h2, "none", WHITE, 2, "Profile mark", "Square and circle crop", WHITE)
    s = 160
    sx = xs[1] + tw / 2 - s - 24
    p.rect(sx, cy - s / 2 + 22, s, s, fill=TEAL)
    place_glyph(p, sx + s / 2, cy + 22, s * 0.6905, WHITE)
    cx2 = xs[1] + tw / 2 + 24 + s / 2
    p.circle(cx2, cy + 22, s / 2, fill=TEAL)
    place_glyph(p, cx2, cy + 22, s * 0.6905, WHITE)
    # gem
    tile(p, xs[2], y2, tw, h2, "none", WHITE, 2, "Gem", "Full artwork and one-color", WHITE)
    place_gem(p, xs[2] + tw / 2 - 100, cy + 22, 120, "full")
    place_gem(p, xs[2] + tw / 2 + 100, cy + 22, 120, "mono", WHITE)
    return p


def page_anatomy():
    p = Page("p04", WHITE, "Wordmark construction, clear space and minimum size")
    chrome(p, 4, "01 Logo", "Wordmark", False)
    # stage
    lw = 640
    k = lw / LOGO_W
    X = GEM_W * k
    lh = LOGO_H * k
    stage_w = 1128
    rx0 = M + (stage_w - (lw + 2 * X)) / 2
    ry0 = 330
    lx, ly = rx0 + X, ry0 + X
    place_logo(p, lx, ly, lw, "full-light")
    p.rect(rx0, ry0, lw + 2 * X, lh + 2 * X, stroke=BLACK, sw=2, dash="10 8")

    def xsq(x, y):
        p.rect(x, y, X, X, fill=TEAL, stroke=BLACK, sw=2)
        p.text(x + X / 2, y + X / 2 + 7, "X", 20, B, BLACK, anchor="middle")

    gem_x = lx + (GEM_CX - LOGO_X0) * k
    xsq(rx0, ly + lh / 2 - X / 2)
    xsq(lx + lw, ly + lh / 2 - X / 2)
    xsq(gem_x - X / 2, ry0)
    xsq(lx + lw / 2 - X / 2, ly + lh)
    label(p, rx0, ry0 - 24, "Clear space: 1X on every side", BLACK, 16)
    p.text(rx0, ry0 + lh + 2 * X + 36, "X is the flat-to-flat width of the gem.", 18, R, BLACK)
    # anatomy row
    ay, cw = 668, 282
    cells = ["Gem", "Letters", "Accent I", "Glyph"]
    subs = ["Seven layers, hexagon", "Arvo Bold 700", "Teal, carries the gem", "Gemini, gradient"]
    cy = ay + 70
    for i, (nm, sb) in enumerate(zip(cells, subs)):
        cx0 = M + i * cw
        p.rect(cx0, ay, cw - 24, 140, stroke=BLACK, sw=2)
        mx = cx0 + (cw - 24) / 2
        if i == 0:
            place_gem(p, mx, cy, 66, "full")
        elif i == 1:
            kk = 200 / 1135.6
            p.add(f'<g transform="translate({n(mx - 100 - LOGO_X0 * kk)} {n(cy + 28 - LOGO_BASE * kk)}) scale({kk:.5f})">{letters_group(p, BLACK, TEAL)}</g>')
        elif i == 2:
            kk = 0.26
            ix = I_CENTER
            p.add(f'<g transform="translate({n(mx - ix * kk)} {n(cy + 56 - LOGO_BASE * kk)}) scale({kk:.5f})">'
                  f'{BOLD_I(p)}{gem_group(p, "full")}</g>')
        else:
            place_glyph(p, mx, cy, 84, ("grad", BLACK))
        label(p, cx0, ay + 170, nm, BLACK, 16)
        p.text(cx0, ay + 196, sb, 16, R, BLACK)
    # right column
    rx = 1290
    label(p, rx, 330, "Minimum size", BLACK, 20)
    p.line(rx, 346, W - M, 346, BLACK, 3)
    p.text(rx, 400, "Wordmark", 18, B, BLACK)
    place_logo(p, rx, 424, 160, "mono-black")
    p.text(rx, 520, "160 PX digital  /  40 MM print", 16, R, BLACK)
    p.text(rx, 580, "Icon", 18, B, BLACK)
    x = rx
    for sz in (24, 32, 48):
        place_glyph(p, x + sz / 2, 640, sz, BLACK)
        p.text(x + sz / 2, 690, f"{sz} PX", 14, R, BLACK, anchor="middle")
        x += sz + 40
    p.text(rx, 740, "8 MM print minimum for the icon.", 16, R, BLACK)
    p.text(rx, 790, "Below minimum, use the icon.", 16, R, BLACK)
    return p


def BOLD_I(p):
    d = BOLD.path("I", LETTER_X["I"], LOGO_BASE, 300)
    return f'<path fill="{TEAL}" d="{d}"/>'


def page_versions():
    p = Page("p05", WHITE, "Wordmark color versions")
    chrome(p, 5, "01 Logo", "Color versions", False)
    tw, th, gap = 552, 300, 36
    specs = [
        ("Full color", "On black", BLACK, "full-dark", WHITE, None),
        ("Full color", "On white", WHITE, "full-light", BLACK, BLACK),
        ("One color white", "On black only", BLACK, "mono-white", WHITE, None),
        ("One color black", "On white", WHITE, "mono-black", BLACK, BLACK),
        ("One color black", "On teal", TEAL, "mono-black", BLACK, None),
    ]
    for i, (nm, sb, bg, var, fg, stroke) in enumerate(specs):
        x = M + (i % 3) * (tw + gap)
        y = 290 + (i // 3) * (th + gap)
        p.rect(x, y, tw, th, fill=bg, stroke=stroke, sw=2)
        label(p, x + 24, y + 38, nm, fg)
        p.text(x + 24, y + 64, sb, 16, R, fg)
        lw = 400
        place_logo(p, x + (tw - lw) / 2, y + 74 + (th - 74 - lw / LOGO_W * LOGO_H) / 2, lw, var)
    # rules tile
    x, y = M + 2 * (tw + gap), 290 + th + gap
    p.rect(x, y, tw, th, fill=BLACK)
    label(p, x + 24, y + 38, "Rules", WHITE)
    rules = ["The glyph gradient runs from teal to the highest contrast color.",
             "White wordmark only on black.",
             "Black wordmark on white or teal.",
             "Never place full color on teal."]
    yy = y + 78
    for r_ in rules:
        p.circle(x + 30, yy - 5, 4, fill=TEAL)
        hh = p.para(x + 48, yy, r_, 18, R, WHITE, tw - 72, 26)
        yy += hh + 12
    return p


def page_misuse():
    p = Page("p06", WHITE, "Wordmark misuse")
    chrome(p, 6, "01 Logo", "Misuse", False)
    tw, th, gap = 405, 230, 36
    lw = 300
    cases = [
        ("Do not stretch or squash.", BLACK, WHITE),
        ("Do not rotate or skew.", BLACK, WHITE),
        ("Do not swap the color roles.", BLACK, WHITE),
        ("Do not outline the letters.", BLACK, WHITE),
        ("Do not use full color on teal.", TEAL, BLACK),
        ("Do not move or resize the gem.", BLACK, WHITE),
        ("Do not crop the wordmark.", BLACK, WHITE),
        ("Do not use the dark version on white.", WHITE, BLACK),
    ]
    for i, (cap, bg, fg) in enumerate(cases):
        x = M + (i % 4) * (tw + gap)
        y = 290 + (i // 4) * (th + 96 + 30)
        p.rect(x, y, tw, th, fill=bg, stroke=BLACK, sw=2)
        cx, cy = x + tw / 2, y + th / 2
        lh = lw / LOGO_W * LOGO_H
        lx, ly = cx - lw / 2, cy - lh / 2
        if i == 0:
            p.add(f'<g transform="translate({n(cx)} {n(cy)}) scale(1.28 0.62) translate({n(-cx)} {n(-cy)})">')
            place_logo(p, lx, ly, lw, "full-dark")
            p.add("</g>")
        elif i == 1:
            p.add(f'<g transform="translate({n(cx)} {n(cy)}) rotate(-12) skewX(-14) translate({n(-cx)} {n(-cy)})">')
            place_logo(p, lx, ly, lw, "full-dark")
            p.add("</g>")
        elif i == 2:
            place_logo(p, lx, ly, lw, "full-dark", letters=TEAL, i_color=WHITE)
        elif i == 3:
            place_logo(p, lx, ly, lw, "full-dark", letters=("outline", WHITE, 12), i_color=("outline", TEAL, 12))
        elif i == 4:
            place_logo(p, lx, ly, lw, "full-dark")
        elif i == 5:
            k = lw / LOGO_W
            gx = (GEM_CX - LOGO_X0) * k + lx
            gy = (GEM_CY - LOGO_Y0) * k + ly
            place_logo(p, lx, ly, lw, "full-dark", gem="none")
            place_gem(p, gx + 78, gy + 70, GEM_W * k * 1.9, "full")
        elif i == 6:
            cid = p.uid("c")
            p.defs.append(f'<clipPath id="{cid}"><rect x="{n(x + 2)}" y="{n(y + 2)}" width="{n(tw - 4)}" height="{n(th - 4)}"/></clipPath>')
            p.add(f'<g clip-path="url(#{cid})">')
            place_logo(p, x - 88, ly, lw + 40, "full-dark")
            p.add("</g>")
        else:
            place_logo(p, lx, ly, lw, "full-dark")
        badge_x(p, x + tw - 28, y + 28)
        p.para(x, y + th + 34, cap, 18, R, BLACK, tw, 26)
    return p


def page_palette():
    p = Page("p07", WHITE, "Color palette")
    chrome(p, 7, "02 Color", "Palette", False)
    cols = [("PRIMARY", "Primary", BLACK, WHITE, WHITE, B, 40, True),
            ("secondary", "Secondary", TEAL, BLACK, BLACK, R, 38, False),
            ("tertiary", "Tertiary", WHITE, BLACK, BLACK, R, 34, False)]
    cw, gap, d = 552, 36, 320
    for i, (lab, role, col, text_col, stroke_col, font, fs, up) in enumerate(cols):
        x = M + i * (cw + gap)
        cx, cy = x + cw / 2, 290 + d / 2
        p.circle(cx, cy, d / 2, fill=col, stroke=stroke_col if col != BLACK else BLACK, sw=6)
        p.text(cx, cy + fs * 0.35, lab, fs, font, text_col, anchor="middle")
        rgb = hex_to_rgb(col)
        h, s_, l_ = to_hsl(col)
        c, m, y_, k_ = to_cmyk(col)
        rows = [("HEX", col.upper()), ("RGB", f"{rgb[0]}  {rgb[1]}  {rgb[2]}"),
                ("HSL", f"{h}  {s_}%  {l_}%"), ("CMYK", f"{c}  {m}  {y_}  {k_}")]
        ty = 664
        p.line(x, ty, x + cw, ty, BLACK, 3)
        for j, (a, b) in enumerate(rows):
            yy = ty + 46 + j * 48
            label(p, x, yy, a, BLACK, 18)
            p.text(x + cw, yy, b, 26, B, BLACK, anchor="end")
            p.line(x, yy + 16, x + cw, yy + 16, BLACK, 1)
    p.text(M, 932, "Exactly three colors. No tints, no shades. CMYK is a direct conversion from sRGB: proof before print.", 18, R, BLACK)
    return p


def page_contrast():
    p = Page("p08", BLACK, "Contrast pairings and gradient")
    chrome(p, 8, "02 Color", "Contrast + gradient", True)
    label(p, M, 316, "Contrast pairings (WCAG 2.2)", WHITE, 18)
    pairs = [(BLACK, WHITE), (WHITE, BLACK), (BLACK, TEAL), (TEAL, BLACK), (WHITE, TEAL), (TEAL, WHITE)]
    cw, ch, gap = 266, 270, 20
    for i, (fg, bg) in enumerate(pairs):
        x = M + (i % 3) * (cw + gap)
        y = 340 + (i // 3) * (ch + gap)
        p.rect(x, y, cw, ch, fill=bg, stroke=WHITE, sw=2)
        lab = WHITE if bg == BLACK else BLACK          # label ink is always readable on the cell
        p.text(x + 24, y + 110, "Aa", 84, B, fg)
        ratio = contrast(fg, bg)
        lvl = wcag_level(ratio)
        txt = f"{round(ratio)}:1" if abs(ratio - round(ratio)) < 0.005 else f"{ratio:.2f}:1"
        p.text(x + 24, y + 176, txt, 36, B, lab)
        bw = R.width(lvl, 16, 0.14) + 28
        p.rect(x + 24, y + 200, bw, 36, fill=lab, rx=18)
        p.text(x + 24 + 14, y + 224, lvl, 16, B, bg, tracking=0.14)
        hx = {BLACK: "BLACK", TEAL: "TEAL", WHITE: "WHITE"}
        p.text(x + cw - 24, y + 36, f"{hx[fg]} ON {hx[bg]}", 14, R, lab, anchor="end", tracking=0.1)
    # gradient
    gx, gw = 1010, W - M - 1010
    label(p, gx, 316, "Signature gradient", WHITE, 18)
    pw, ph, pad = gw, 170, 16
    gid = p.once(("grad", WHITE), lambda i: gradient_def(i, WHITE, x1=gx + gw - pad, x2=gx + pad))
    p.rect(gx, 340, pw, ph, fill=BLACK, stroke=WHITE, sw=2)
    p.rect(gx + pad, 340 + pad, pw - 2 * pad, ph - 2 * pad, fill=f"url(#{gid})")
    p.text(gx, 540, "On black: teal to white", 18, B, WHITE)
    gid2 = p.once(("grad2", BLACK), lambda i: gradient_def(i, BLACK, x1=gx + gw - pad, x2=gx + pad))
    p.rect(gx, 580, pw, ph, fill=WHITE)
    p.rect(gx + pad, 580 + pad, pw - 2 * pad, ph - 2 * pad, fill=f"url(#{gid2})")
    p.text(gx, 780, "On white: teal to black", 18, B, WHITE)
    stops = [(0, 0.0), (19, 0.1875), (50, 0.5), (75, 0.75), (100, 1.0)]
    sx = gx
    for pc, t in stops:
        col = ramp_color(t, WHITE)
        label(p, sx, 836, f"{pc}%", WHITE, 14)
        p.rect(sx, 850, 24, 24, fill=col, stroke=WHITE, sw=2)
        p.text(sx + 34, 870, col.upper(), 16, R, WHITE)
        sx += gw / 5
    p.para(gx, 914, "Direction: left to right, teal solid for the first 19%, then eased to the far color. Dark-background stops shown.", 16, R, WHITE, gw, 24)
    return p


def page_type():
    p = Page("p09", WHITE, "Typography: Arvo")
    chrome(p, 9, "03 Typography", "Typeface", False)
    # specimen (mirrors the original sketch: ARVO bold, arvo regular beneath, right aligned)
    p.text(M, 500, "ARVO", 240, B, BLACK)
    wA = B.width("ARVO", 240)
    p.text(M + wA, 650, "arvo", 150, R, BLACK, anchor="end")
    # info column
    ix = 1120
    label(p, ix, 330, "Arvo", BLACK, 20)
    p.line(ix, 346, W - M, 346, BLACK, 3)
    info = [("Weights", "Regular 400, Bold 700"), ("Designer", "Anton Koovit"),
            ("License", "SIL Open Font License 1.1"), ("Source", "Google Fonts")]
    for j, (a, b) in enumerate(info):
        yy = 392 + j * 46
        label(p, ix, yy, a, BLACK, 14)
        p.text(W - M, yy, b, 20, R, BLACK, anchor="end")
        p.line(ix, yy + 14, W - M, yy + 14, BLACK, 1)
    p.text(ix, 590, "Bold, uppercase: primary text.", 18, B, BLACK)
    p.text(ix, 622, "Regular, sentence case: secondary text.", 18, R, BLACK)
    # glyph rows
    gy = 776
    p.text(M, gy, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 64, B, BLACK)
    p.text(M, gy + 78, "abcdefghijklmnopqrstuvwxyz", 64, R, BLACK)
    p.text(M, gy + 156, "0123456789  &@#%!?.,:;()/-+=$", 64, B, BLACK)
    return p


def page_scale():
    p = Page("p10", BLACK, "Type scale")
    chrome(p, 10, "03 Typography", "Type scale", True)
    rows = [
        ("Display", B, 120, 120, "GEMINII", True, 0.0, "Bold 120 / 120"),
        ("H1", B, 72, 80, "BRAND KIT", True, 0.0, "Bold 72 / 80"),
        ("H2", B, 48, 56, "SECTION TITLE", True, 0.0, "Bold 48 / 56"),
        ("H3", B, 32, 40, "Subsection title", False, 0.0, "Bold 32 / 40"),
        ("Body large", R, 24, 36, "The quick brown fox jumps over the lazy dog.", False, 0.0, "Regular 24 / 36"),
        ("Body", R, 18, 28, "The quick brown fox jumps over the lazy dog.", False, 0.0, "Regular 18 / 28"),
        ("Label", B, 14, 20, "LABEL TEXT", True, 0.14, "Bold 14 / 20, +14% tracking"),
    ]
    y = 296
    for role, font, size, lead, sample, up, tr, spec in rows:
        rh = max(lead, 44) + 28
        p.line(M, y, W - M, y, WHITE, 1)
        label(p, M, y + rh / 2 + 6, role, WHITE, 16)
        p.text(M + 230, y + rh / 2 + 6, spec, 16, R, WHITE)
        p.text(M + 700, y + rh / 2 + size * 0.35 + (4 if size < 40 else 0), sample, size, font, WHITE, tracking=tr, upper=up)
        y += rh
    p.line(M, y, W - M, y, WHITE, 1)
    return p


# ------------------------------------------------------------ ui kit
def surf(dark):
    return ("dark" if dark else "light")


def button(p, x, y, w, h, kind, state, dark, text="BUTTON"):
    fg = ink(dark)
    bgp = paper(dark)
    if dark:
        base = {"primary": (WHITE, BLACK, WHITE), "secondary": (TEAL, BLACK, TEAL), "tertiary": (BLACK, WHITE, WHITE)}[kind]
        inv = {"primary": (TEAL, BLACK, TEAL), "secondary": (BLACK, TEAL, TEAL), "tertiary": (WHITE, BLACK, WHITE)}[kind]
        bar = {"primary": TEAL, "secondary": BLACK, "tertiary": TEAL}[kind]
    else:
        base = {"primary": (BLACK, WHITE, BLACK), "secondary": (TEAL, BLACK, BLACK), "tertiary": (WHITE, BLACK, BLACK)}[kind]
        inv = {"primary": (TEAL, BLACK, BLACK), "secondary": (BLACK, TEAL, BLACK), "tertiary": (BLACK, WHITE, BLACK)}[kind]
        bar = {"primary": TEAL, "secondary": BLACK, "tertiary": TEAL}[kind]
    fill, tcol, stroke = base
    tfont = B
    if state == "pressed":
        fill, tcol, stroke = inv
    if state == "disabled":
        p.rect(x + 1, y + 1, w - 2, h - 2, fill="none", stroke=fg, sw=2, rx=4, dash="7 6")
        p.text(x + w / 2, y + h / 2 + 6, text, 16, R, fg, anchor="middle", tracking=0.12)
        return
    if state == "focus":
        p.rect(x - 4, y - 4, w + 8, h + 8, stroke=fg, sw=2, rx=7)
        p.rect(x - 9, y - 9, w + 18, h + 18, stroke=TEAL, sw=3, rx=11)
    p.rect(x + 1, y + 1, w - 2, h - 2, fill=fill, stroke=stroke, sw=2, rx=4)
    if state == "hover":
        cid = p.uid("c")
        p.defs.append(f'<clipPath id="{cid}"><rect x="{n(x + 1)}" y="{n(y + 1)}" width="{n(w - 2)}" height="{n(h - 2)}" rx="4"/></clipPath>')
        p.add(f'<rect x="{n(x)}" y="{n(y + h - 7)}" width="{n(w)}" height="8" fill="{bar}" clip-path="url(#{cid})"/>')
    p.text(x + w / 2, y + h / 2 + 6 - (2 if state == "hover" else 0), text, 16, tfont, tcol, anchor="middle", tracking=0.12)


def field(p, x, y, w, state, dark, name="LABEL", value="Value", placeholder="Placeholder"):
    fg = ink(dark)
    label(p, x, y, name, fg, 14)
    fy, fh = y + 14, 56
    if state == "focus":
        p.rect(x - 5, fy - 5, w + 10, fh + 10, stroke=TEAL, sw=3, rx=9)
    if state == "disabled":
        p.rect(x + 1, fy + 1, w - 2, fh - 2, fill="none", stroke=fg, sw=2, rx=4, dash="7 6")
    else:
        sw = 4 if state == "error" else 2
        p.rect(x + sw / 2, fy + sw / 2, w - sw, fh - sw, fill=paper(dark), stroke=fg, sw=sw, rx=4)
    ty = fy + fh / 2 + 6
    if state in ("default",):
        p.text(x + 18, ty, placeholder, 18, R, fg)
    elif state == "focus":
        p.text(x + 18, ty, value, 18, B, fg)
        cx = x + 18 + B.width(value, 18) + 3
        p.rect(cx, fy + 14, 2, fh - 28, fill=fg)
    elif state == "filled":
        p.text(x + 18, ty, value, 18, B, fg)
    elif state == "disabled":
        p.text(x + 18, ty, placeholder, 18, R, fg)
    elif state == "error":
        p.text(x + 18, ty, value, 18, B, fg)
        cx, cy = x + w - 32, fy + fh / 2
        p.circle(cx, cy, 13, fill=fg)
        p.rect(cx - 1.5, cy - 7, 3, 9, fill=paper(dark))
        p.circle(cx, cy + 7, 1.8, fill=paper(dark))
        p.text(x, fy + fh + 28, "Error message text.", 16, B, fg)


def checkbox(p, x, y, checked, dark):
    fg = ink(dark)
    p.rect(x + 1, y + 1, 24, 24, fill=fg if checked else paper(dark), stroke=fg, sw=2, rx=3)
    if checked:
        p.path(f"M{n(x + 7)} {n(y + 14)}L{n(x + 11.5)} {n(y + 18.5)}L{n(x + 19.5)} {n(y + 8)}", stroke=paper(dark), sw=3)


def radio(p, x, y, selected, dark):
    fg = ink(dark)
    p.circle(x + 13, y + 13, 12, fill=paper(dark), stroke=fg, sw=2)
    if selected:
        p.circle(x + 13, y + 13, 6, fill=fg)


def toggle(p, x, y, on, dark):
    fg = ink(dark)
    p.rect(x + 1, y + 1, 54, 30, fill=TEAL if on else paper(dark), stroke=fg if not (on and dark) else TEAL, sw=2, rx=15)
    kc = BLACK if (on or not dark) else WHITE
    p.circle(x + (41 if on else 15), y + 16, 9, fill=kc)


def link(p, x, y, text, dark, hover=False):
    fg = ink(dark)
    w = p.text(x, y, text, 20, R, fg)
    if hover:
        p.rect(x, y + 6, w, 4, fill=TEAL)
    else:
        p.rect(x, y + 6, w, 2, fill=fg)
    return w


def page_ui_light():
    p = Page("p11", WHITE, "UI components, light surface")
    chrome(p, 11, "04 UI Components", "Buttons + forms", False)
    states = ["default", "hover", "pressed", "focus", "disabled"]
    bx, by, bw, bh, cg = M + 150, 330, 240, 56, 72
    for j, s_ in enumerate(states):
        label(p, bx + j * (bw + cg), by - 20, s_, BLACK, 14)
    for i, kind in enumerate(("primary", "secondary", "tertiary")):
        yy = by + 16 + i * 92
        label(p, M, yy + 34, kind, BLACK, 14)
        for j, s_ in enumerate(states):
            button(p, bx + j * (bw + cg), yy, bw, bh, kind, s_, False)
    # row B
    y0 = 640
    p.line(M, y0 - 30, W - M, y0 - 30, BLACK, 1)
    label(p, M, y0, "Text fields", BLACK, 18)
    fw = 250
    positions = [(M, y0 + 50), (M + fw + 28, y0 + 50), (M + 2 * (fw + 28), y0 + 50),
                 (M, y0 + 176), (M + fw + 28, y0 + 176)]
    for (fx, fy), st in zip(positions, ("default", "focus", "filled", "disabled", "error")):
        field(p, fx, fy, fw, st, False, name=st)
    # links
    lx = 1010
    label(p, lx, y0, "Links", BLACK, 18)
    link(p, lx, y0 + 60, "Inline link", False)
    p.text(lx + 150, y0 + 60, "default", 14, R, BLACK, tracking=0.1)
    link(p, lx, y0 + 110, "Inline link", False, hover=True)
    p.text(lx + 150, y0 + 110, "hover", 14, R, BLACK, tracking=0.1)
    # controls
    cx = 1330
    label(p, cx, y0, "Controls", BLACK, 18)
    checkbox(p, cx, y0 + 40, False, False)
    checkbox(p, cx + 40, y0 + 40, True, False)
    p.text(cx + 90, y0 + 60, "Checkbox", 18, R, BLACK)
    radio(p, cx, y0 + 90, False, False)
    radio(p, cx + 40, y0 + 90, True, False)
    p.text(cx + 90, y0 + 110, "Radio", 18, R, BLACK)
    toggle(p, cx, y0 + 138, False, False)
    toggle(p, cx + 70, y0 + 138, True, False)
    p.text(cx + 140, y0 + 160, "Toggle", 18, R, BLACK)
    return p


def page_ui_dark():
    p = Page("p12", BLACK, "UI components, dark surface")
    chrome(p, 12, "04 UI Components", "Surfaces + nav", True)
    # nav bar
    ny, nh = 290, 92
    p.rect(M, ny, 1728, nh, fill=BLACK, stroke=WHITE, sw=2)
    place_logo(p, M + 32, ny + (nh - 190 / LOGO_W * LOGO_H) / 2, 190, "full-dark")
    items = ["ITEM ONE", "ITEM TWO", "ITEM THREE"]
    xx = 560
    for i, it in enumerate(items):
        wv = p.text(xx, ny + nh / 2 + 6, it, 16, B if i == 0 else R, WHITE, tracking=0.12)
        if i == 0:
            p.rect(xx, ny + nh / 2 + 18, wv, 4, fill=TEAL)
        xx += wv + 48
    button(p, M + 1728 - 32 - 190, ny + (nh - 56) / 2, 190, 56, "secondary", "default", True)
    # buttons on dark
    by = 420
    label(p, M, by - 6, "Buttons on black", WHITE, 14)
    for i, kind in enumerate(("primary", "secondary", "tertiary")):
        for j, st in enumerate(("default", "hover", "pressed", "disabled")):
            button(p, M + j * 222 + i * 0, by + 18 + i * 76, 190, 52, kind, st, True)
    # cards
    cx0, cy0, cw, ch, gap = 1040, 434, 250, 232, 14
    label(p, cx0, by - 6, "Cards", WHITE, 14)
    cardspec = [(WHITE, BLACK, None), (TEAL, BLACK, None), (BLACK, WHITE, WHITE)]
    for i, (f_, t_, s_) in enumerate(cardspec):
        x = cx0 + i * (cw + gap) + (0 if i < 3 else 0)
        p.rect(x, cy0 + 4, cw, ch, fill=f_, stroke=s_, sw=2 if s_ else 0)
        label(p, x + 22, cy0 + 50, "Card title", t_, 16)
        p.para(x + 22, cy0 + 86, "Body text set in Arvo Regular.", 17, R, t_, cw - 44, 25)
        p.rect(x + 22, cy0 + ch - 54, 120, 34, fill=t_, rx=4)
        p.text(x + 82, cy0 + ch - 31, "LINK", 14, B, f_, anchor="middle", tracking=0.12)
    # tags, tabs, avatar
    ry = 700
    label(p, M, ry, "Tags", WHITE, 14)
    tx = M
    for fill_, tc, st in ((WHITE, BLACK, None), (TEAL, BLACK, None), (BLACK, WHITE, WHITE)):
        tw_ = R.width("TAG", 14, 0.14) + 40
        p.rect(tx, ry + 20, tw_, 38, fill=fill_, stroke=st, sw=2 if st else 0, rx=19)
        p.text(tx + tw_ / 2, ry + 45, "TAG", 14, B, tc, anchor="middle", tracking=0.14)
        tx += tw_ + 16
    label(p, M, ry + 130, "Tabs", WHITE, 14)
    tx = M
    for i, it in enumerate(("TAB ONE", "TAB TWO", "TAB THREE")):
        wv = p.text(tx, ry + 176, it, 16, B if i == 0 else R, WHITE, tracking=0.12)
        if i == 0:
            p.rect(tx, ry + 190, wv, 5, fill=TEAL)
        tx += wv + 40
    cx1 = 700
    label(p, cx1, ry, "Fields", WHITE, 14)
    field(p, cx1, ry + 36, 300, "focus", True, name="Label", value="Value")
    label(p, 1040, ry, "Controls", WHITE, 14)
    checkbox(p, 1040, ry + 40, True, True)
    p.text(1080, ry + 60, "Checkbox", 18, R, WHITE)
    radio(p, 1040, ry + 90, True, True)
    p.text(1080, ry + 110, "Radio", 18, R, WHITE)
    toggle(p, 1040, ry + 138, True, True)
    p.text(1110, ry + 160, "Toggle", 18, R, WHITE)
    label(p, 1400, ry, "Avatar", WHITE, 14)
    p.circle(1456, ry + 100, 56, fill=TEAL)
    place_glyph(p, 1456, ry + 100, 56 * 2 * 0.6905, WHITE)
    return p


def _asset(name, vb, content_fn, page_key, bg=None, w=2000):
    """Write a standalone transparent SVG. vb = (x, y, w, h) in content coordinates."""
    pg = Page(page_key)
    body = content_fn(pg)
    x, y, vw, vh = vb
    h = round(w * vh / vw)
    back = f'<rect x="{n(x)}" y="{n(y)}" width="{n(vw)}" height="{n(vh)}" fill="{bg}"/>' if bg else ""
    defs = f"<defs>{''.join(pg.defs)}</defs>" if pg.defs else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{n(x)} {n(y)} {n(vw)} {n(vh)}" '
        f'role="img" aria-label="{esc(name)}"><title>{esc(name)}</title>{defs}{back}{body}</svg>'
    )
    path = os.path.join(DIST, "logos", name.replace(" ", "-").lower() + ".svg")
    with open(path, "w") as f:
        f.write(svg)
    return path


def export_logos():
    os.makedirs(os.path.join(DIST, "logos"), exist_ok=True)
    wb = (LOGO_X0, LOGO_Y0, LOGO_W, LOGO_H)
    for nm, var in (("wordmark full color on dark", "full-dark"), ("wordmark full color on light", "full-light"),
                    ("wordmark white", "mono-white"), ("wordmark black", "mono-black")):
        _asset(nm, wb, lambda pg, v=var: logo_content(pg, **VARIANTS[v]), "w")
    gb = (GLYPH_BOX[0], GLYPH_BOX[1], GLYPH_BOX[2] - GLYPH_BOX[0], GLYPH_BOX[3] - GLYPH_BOX[1])
    for nm, fill in (("icon gradient on dark", ("grad", WHITE)), ("icon gradient on light", ("grad", BLACK)),
                     ("icon white", WHITE), ("icon black", BLACK), ("icon teal", TEAL)):
        _asset(nm, gb, lambda pg, f=fill: glyph_group(pg, f), "i")
    # profile mark: 1500 square, glyph at 69.05% of the width, centred
    def prof(pg, circle=False):
        k = 0.6905 * 1500 / (GLYPH_BOX[2] - GLYPH_BOX[0])
        gcx, gcy = (GLYPH_BOX[0] + GLYPH_BOX[2]) / 2, (GLYPH_BOX[1] + GLYPH_BOX[3]) / 2
        shape = f'<circle cx="750" cy="750" r="750" fill="{TEAL}"/>' if circle else f'<rect width="1500" height="1500" fill="{TEAL}"/>'
        return shape + f'<g transform="translate({n(750 - gcx * k)} {n(750 - gcy * k)}) scale({k:.6f})">{glyph_group(pg, WHITE)}</g>'
    _asset("profile mark square", (0, 0, 1500, 1500), lambda pg: prof(pg, False), "ps", w=1500)
    _asset("profile mark circle", (0, 0, 1500, 1500), lambda pg: prof(pg, True), "pc", w=1500)
    gem = (GEM_CX - GEM_W / 2, GEM_CY - GEM_R[0], GEM_W, 2 * GEM_R[0])
    _asset("gem full color", gem, lambda pg: gem_group(pg, "full"), "g")
    _asset("gem white", gem, lambda pg: gem_group(pg, "mono", WHITE), "gw")
    _asset("gem black", gem, lambda pg: gem_group(pg, "mono", BLACK), "gb")


PAGES = [
    ("01-cover", page_cover), ("02-contents", page_contents), ("03-logo-suite", page_suite),
    ("04-wordmark", page_anatomy), ("05-color-versions", page_versions), ("06-misuse", page_misuse),
    ("07-palette", page_palette), ("08-contrast-gradient", page_contrast), ("09-typeface", page_type),
    ("10-type-scale", page_scale), ("11-ui-light", page_ui_light), ("12-ui-dark", page_ui_dark),
]


def build():
    os.makedirs(os.path.join(DIST, "pages"), exist_ok=True)
    pages = [(name, fn()) for name, fn in PAGES]
    gap = 48
    total_h = len(pages) * H + (len(pages) + 1) * gap
    parts = []
    for i, (name, pg) in enumerate(pages):
        with open(os.path.join(DIST, "pages", f"{name}.svg"), "w") as f:
            f.write(pg.svg())
        y = gap + i * (H + gap)
        defs = f"<defs>{''.join(pg.defs)}</defs>" if pg.defs else ""
        parts.append(
            f'<g id="{name}" transform="translate({gap} {y})" role="img" aria-label="{esc(pg.title)}">{defs}'
            f'<clipPath id="{pg.key}-clip"><rect width="{W}" height="{H}"/></clipPath>'
            f'<g clip-path="url(#{pg.key}-clip)">{pg.body()}</g></g>'
        )
    mw = W + 2 * gap
    master = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{mw}" height="{total_h}" viewBox="0 0 {mw} {total_h}" '
        f'role="img" aria-label="GEMINII Brand Kit"><title>GEMINII Brand Kit</title>'
        f'<rect width="{mw}" height="{total_h}" fill="{TEAL}"/>{"".join(parts)}</svg>'
    )
    with open(os.path.join(DIST, "GEMINII_Brandkit.svg"), "w") as f:
        f.write(master)
    export_logos()
    return pages


if __name__ == "__main__":
    pgs = build()
    print(f"built {len(pgs)} pages -> {DIST}")
