#!/usr/bin/env python3
"""GEMINII brand kit: verification suite.

    GEMINII_KIT_DIST=<dir built by build.py> python3 tools/kit/verify_kit.py   # exits non-zero on any failure

Checks, in order:
  structure   well-formed XML, no <text>/<image>/<style>/<script>, no external refs, unique ids, resolved url(#id)
  palette     only palette + documented gem neutrals + gradient ramp colors appear
  math        contrast ratios, WCAG levels, HSL, CMYK
  geometry    glyph mirror symmetry, gem regularity and centring, section/page consistency
  fidelity    rebuilt wordmark, icon and profile mark against the original source SVGs
  layout      (Chromium) every outlined text run stays inside the safe area and never overlaps another
  legibility  (Chromium) text vs the background actually rendered behind it meets WCAG AA (demo samples exempt)
  portability (CairoSVG) every page renders the same in a second, independent engine
"""
import glob
import io
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))          # tools/kit
sys.path.insert(0, ROOT)
DIST = os.environ.get("GEMINII_KIT_DIST") or os.path.join(ROOT, "dist")

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import kitlib as K  # noqa: E402
import build as BUILD  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


ALL = sorted(glob.glob(os.path.join(DIST, "**", "*.svg"), recursive=True))
PAGES = sorted(glob.glob(os.path.join(DIST, "pages", "*.svg")))
MASTER = os.path.join(DIST, "GEMINII_Brandkit.svg")
NS = "{http://www.w3.org/2000/svg}"

# ------------------------------------------------------------------ structure
bad = []
for f in ALL:
    try:
        ET.fromstring(read(f))
    except ET.ParseError as e:
        bad.append((os.path.basename(f), str(e)))
check("structure: all SVGs are well-formed XML", not bad, f"{len(ALL)} files" if not bad else str(bad))

forbidden = {"text", "tspan", "image", "foreignObject", "style", "script", "a", "filter"}
hits = []
for f in ALL:
    root = ET.fromstring(read(f))
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        if tag in forbidden:
            hits.append((os.path.basename(f), tag))
        for att in el.attrib:
            if att.endswith("href") or att in ("font-family", "style"):
                hits.append((os.path.basename(f), att))
check("structure: no live text, raster, style, script, filter or external references", not hits, str(hits[:5]))

dupe, dangling = [], []
for f in ALL:
    s = read(f)
    ids = re.findall(r'\bid="([^"]+)"', s)
    if len(ids) != len(set(ids)):
        dupe.append(os.path.basename(f))
    refs = set(re.findall(r"url\(#([^)]+)\)", s))
    if refs - set(ids):
        dangling.append((os.path.basename(f), sorted(refs - set(ids))[:3]))
check("structure: ids unique in every file (including the master)", not dupe, str(dupe))
check("structure: every url(#id) resolves", not dangling, str(dangling))

for f in PAGES:
    root = ET.fromstring(read(f))
    if root.get("viewBox") != "0 0 1920 1080" or root.get("width") != "1920" or root.get("height") != "1080":
        check("structure: page size 1920x1080", False, os.path.basename(f))
        break
else:
    check("structure: page size 1920x1080", True, f"{len(PAGES)} pages")
check("structure: 12 pages + master + 14 logo assets",
      len(PAGES) == 12 and os.path.exists(MASTER) and len(glob.glob(os.path.join(DIST, "logos", "*.svg"))) == 14)
mroot = ET.fromstring(read(MASTER))
groups = [g.get("id") for g in mroot if g.tag == NS + "g"]
check("structure: master holds every page in order", groups == [os.path.basename(p)[:-4] for p in PAGES], str(groups[:2]) + "...")
check("structure: master under the 16 MB artifact limit", os.path.getsize(MASTER) < 16 * 1024 * 1024, f"{os.path.getsize(MASTER) / 1e6:.2f} MB")

# ------------------------------------------------------------------ palette
allowed = set(K.PALETTE) | set(K.GEM_NEUTRALS) | {"#7a7a7a", "#6a6a6a", "#595959", "#4b4b4b", "#414141", "#3c3c3c", "#3a3a3a"}
for far in (K.WHITE, K.BLACK):
    for k in range(49):
        allowed.add(K.lerp_hex(K.TEAL, far, K.ramp_u(k / 48)))
    for t in (0, 0.1875, 0.5, 0.75, 1.0):
        allowed.add(K.ramp_color(t, far))
offenders = {}
for f in ALL:
    for c in set(re.findall(r"#[0-9a-fA-F]{6}\b", read(f))):
        if c.lower() not in allowed:
            offenders.setdefault(os.path.basename(f), set()).add(c)
    if re.search(r"rgb\(|hsl\(|rgba\(", read(f)):
        offenders.setdefault(os.path.basename(f), set()).add("functional color")
check("palette: only black, teal, white (+ gem neutrals and gradient ramp) appear anywhere", not offenders, str(offenders)[:200])

# ------------------------------------------------------------------ math
c_bw, c_bt, c_wt = K.contrast(K.BLACK, K.WHITE), K.contrast(K.BLACK, K.TEAL), K.contrast(K.WHITE, K.TEAL)
check("math: black/white contrast is 21:1", abs(c_bw - 21) < 1e-9, f"{c_bw:.4f}")
check("math: black on teal is 9.98:1 (AAA)", abs(c_bt - 9.976) < 0.01 and K.wcag_level(c_bt) == "AAA", f"{c_bt:.4f}")
check("math: white on teal is 2.11:1 (FAIL)", abs(c_wt - 2.105) < 0.01 and K.wcag_level(c_wt) == "FAIL", f"{c_wt:.4f}")
check("math: WCAG level thresholds", [K.wcag_level(x) for x in (21, 7, 6.9, 4.5, 4.49, 3, 2.99)] == ["AAA", "AAA", "AA", "AA", "AA LARGE", "AA LARGE", "FAIL"])
check("math: teal HSL 179/100/39 and CMYK 100/0/1/22", K.to_hsl(K.TEAL) == (179, 100, 39) and K.to_cmyk(K.TEAL) == (100, 0, 1, 22), f"{K.to_hsl(K.TEAL)} {K.to_cmyk(K.TEAL)}")
check("math: black and white HSL/CMYK", K.to_hsl(K.BLACK) == (0, 0, 0) and K.to_cmyk(K.BLACK) == (0, 0, 0, 100) and K.to_hsl(K.WHITE) == (0, 0, 100) and K.to_cmyk(K.WHITE) == (0, 0, 0, 0))
check("math: hex/rgb round trip", all(K.rgb_to_hex(K.hex_to_rgb(c)) == c for c in K.PALETTE))
# the gradient model is lerp(teal, far, u): u runs 0..1 monotonic along the ramp
us = [K.ramp_u(k / 100) for k in range(101)]
check("math: gradient ramp monotonic, teal at the left end, white at the right end", all(b <= a + 1e-9 for a, b in zip(us, us[1:])) and us[0] > 0.999 and us[-1] < 1e-3 and K.ramp_color(0, K.WHITE) == K.TEAL and K.ramp_color(1, K.WHITE) == K.WHITE)

# ------------------------------------------------------------------ geometry
nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", K.GLYPH_ICON)]
# path uses single-coordinate L commands, so rebuild points with a tiny parser
pts, cur_x, cur_y = [], None, None
for cmd, args in re.findall(r"([MLC])([^MLCZ]*)", K.GLYPH_ICON):
    v = [float(x) for x in re.findall(r"-?\d+\.?\d*", args)]
    for i in range(0, len(v), 2):
        pts.append((v[i], v[i + 1]))
mirror_ok = all(any(abs((1500 - x) - x2) < 1e-6 and abs(y - y2) < 1e-6 for x2, y2 in pts) for x, y in pts)
check("geometry: glyph is mirror-symmetric about x=750", mirror_ok, f"{len(pts)} points")
check("geometry: gem width = sqrt(3) x circumradius", abs(K.GEM_W - math.sqrt(3) * K.GEM_R[0]) < 1e-9)
check("geometry: gem is centred on the stem of the teal I", abs(K.GEM_CX - K.I_CENTER) < 1e-9)
hx = re.findall(r"-?\d+\.?\d*", K.hexagon(0, 0, 10))
hp = [(float(hx[i]), float(hx[i + 1])) for i in range(0, 12, 2)]
check("geometry: hexagon vertices all lie on the circumscribed circle, pointy top", all(abs(math.hypot(x, y) - 10) < 0.02 for x, y in hp) and abs(hp[0][0]) < 0.02 and hp[0][1] < 0)
check("geometry: gem layers strictly nested", all(a > b for a, b in zip(K.GEM_R, K.GEM_R[1:])))
check("geometry: letters sit on one baseline at Arvo Bold 300 px", abs(K.S300 * 2048 - 300) < 1e-9 and K.LETTER_X["E"] > K.LETTER_X["G"] and K.LETTER_X["N"] > K.LETTER_X["I"] > K.LETTER_X["M"])
check("geometry: lockup aspect ratio 3.539", abs(K.LOGO_W / K.LOGO_H - 3.539) < 0.001, f"{K.LOGO_W / K.LOGO_H:.4f}")

# section/page consistency: each page's section label must match BUILD.SECTIONS
from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--allow-file-access-from-files"])
    ctx = br.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg = ctx.new_page()

    def load(path):
        pg.goto("file://" + path)
        pg.wait_for_load_state("load")

    def raster(path, w):
        """Render an SVG to an RGB numpy array at width w via an <img> wrapper."""
        html = os.path.join(os.path.dirname(path), "._v.html")
        with open(html, "w") as f:
            f.write(f'<html><body style="margin:0;background:#808080"><img id="i" src="file://{path}" style="display:block;width:{w}px"></body></html>')
        pg.set_viewport_size({"width": w, "height": w})
        pg.goto("file://" + html)
        pg.wait_for_function("document.getElementById('i').complete && document.getElementById('i').naturalWidth>0")
        png = pg.locator("#i").screenshot()
        os.remove(html)
        return np.array(Image.open(io.BytesIO(png)).convert("RGB"))

    # ---- section consistency + layout
    sect_ok, layout_bad, overlap_bad = True, [], []
    page_texts = {}
    for i, path in enumerate(PAGES, start=1):
        pg.set_viewport_size({"width": 1920, "height": 1080})
        load(path)
        items = pg.evaluate(
            """() => [...document.querySelectorAll('path[data-t]')].map(e => {
                 const r = e.getBoundingClientRect();
                 return {t: e.getAttribute('data-t'), x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, fill: e.getAttribute('fill')};
               })"""
        )
        page_texts[i] = items
        for it in items:
            m = re.match(r"^(0[1-4]) ([A-Z ]+)$", it["t"])
            if m and i > 2:
                sec = [s for s in BUILD.SECTIONS if s[0] == m.group(1)][0]
                if not (sec[2] <= i <= sec[3]) or sec[1].upper() != m.group(2):
                    sect_ok = False
        if i == 1:
            continue  # cover is free-form
        for it in items:
            if it["x0"] < 90 or it["x1"] > 1830 or it["y0"] < 90 or it["y1"] > 1012:
                layout_bad.append((i, it["t"], round(it["x0"]), round(it["y0"]), round(it["x1"]), round(it["y1"])))
        for a in range(len(items)):
            for b in range(a + 1, len(items)):
                A, Bb = items[a], items[b]
                ix = min(A["x1"], Bb["x1"]) - max(A["x0"], Bb["x0"])
                iy = min(A["y1"], Bb["y1"]) - max(A["y0"], Bb["y0"])
                if ix > 1 and iy > 1:
                    overlap_bad.append((i, A["t"], Bb["t"], round(ix), round(iy)))
    check("geometry: every page's section label matches the contents page", sect_ok)
    check("layout: all text inside the safe area (96 px margins)", not layout_bad, str(layout_bad[:4]))
    check("layout: no two text runs overlap", not overlap_bad, str(overlap_bad[:4]))
    check("layout: every page carries outlined text", all(len(v) > 0 for v in page_texts.values()), f"{sum(len(v) for v in page_texts.values())} runs")

    # ---- legibility against the rendered background
    low = []
    for i, path in enumerate(PAGES, start=1):
        pg.set_viewport_size({"width": 1920, "height": 1080})
        load(path)
        pg.evaluate("() => document.querySelectorAll('path[data-t]').forEach(e => e.setAttribute('display', 'none'))")
        png = pg.screenshot()
        img = np.array(Image.open(io.BytesIO(png)).convert("RGB"))
        for it in page_texts[i]:
            x0, y0, x1, y1 = [int(round(v)) for v in (it["x0"], it["y0"], it["x1"], it["y1"])]
            x0, y0 = max(x0, 0), max(y0, 0)
            x1, y1 = min(x1, 1920), min(y1, 1080)
            if x1 - x0 < 2 or y1 - y0 < 2:
                continue
            region = img[y0:y1, x0:x1].reshape(-1, 3)
            vals, counts = np.unique(region, axis=0, return_counts=True)
            bg = "#%02x%02x%02x" % tuple(vals[counts.argmax()])
            ratio = K.contrast(it["fill"], bg)
            if ratio < 4.5 and not (i == 8 and it["t"] == "Aa"):    # the "Aa" samples demonstrate pairings, including failing ones
                low.append((i, it["t"], it["fill"], bg, round(ratio, 2)))
    check("legibility: every text run meets WCAG AA against its rendered background (Aa demos exempt)", not low, str(low[:5]))
    check("legibility: the Aa demos on page 08 show exactly the six pairings",
          sorted((it["fill"]) for it in page_texts[8] if it["t"] == "Aa") == sorted([K.BLACK, K.WHITE, K.BLACK, K.TEAL, K.WHITE, K.TEAL]))

    # ---- fidelity against the original sources
    def diff_frac(a, b, thr=40):
        d = np.abs(a.astype(int) - b.astype(int)).max(axis=2)
        return float((d > thr).mean())

    ref = os.path.join(ROOT, "ref")
    tmp = os.path.join(DIST, "._fid")
    os.makedirs(tmp, exist_ok=True)
    p_ = K.Page("t")
    body = "".join(p_.out)
    p_.add(f"<g>{K.logo_content(p_)}</g>")
    open(os.path.join(tmp, "logo.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000" viewBox="0 0 1500 1500"><defs>{"".join(p_.defs)}</defs>'
        f'<rect x="-150" y="-150" width="1800" height="1800" fill="#000"/>{"".join(p_.out)}</svg>')
    f1 = diff_frac(raster(os.path.join(ref, "Full_Logo.svg"), 800), raster(os.path.join(tmp, "logo.svg"), 800))
    check("fidelity: rebuilt wordmark matches the original Full Logo (<0.1% pixels differ)", f1 < 0.001, f"{f1 * 100:.3f}%")

    p2 = K.Page("t2")
    g = K.glyph_group(p2, ("grad", K.WHITE))
    open(os.path.join(tmp, "icon.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="2000" viewBox="0 0 1500 1500"><defs>{"".join(p2.defs)}</defs>'
        f'<rect width="1500" height="1500" fill="#000"/>{g}</svg>')
    f2 = diff_frac(raster(os.path.join(ref, "Icon.svg"), 800), raster(os.path.join(tmp, "icon.svg"), 800))
    check("fidelity: rebuilt icon matches the original Icon (<0.4% pixels differ; symmetrization)", f2 < 0.004, f"{f2 * 100:.3f}%")

    f3 = diff_frac(raster(os.path.join(ref, "Instagram_PFP.svg"), 800), raster(os.path.join(DIST, "logos", "profile-mark-square.svg"), 800))
    check("fidelity: profile mark matches the original Instagram PFP (<0.4% pixels differ)", f3 < 0.004, f"{f3 * 100:.3f}%")

    # circular crop safety: glyph corners inside the inscribed circle of the profile mark
    k = 0.6905 * 1500 / (K.GLYPH_BOX[2] - K.GLYPH_BOX[0])
    corner = math.hypot((K.GLYPH_BOX[2] - K.GLYPH_BOX[0]) / 2 * k, (K.GLYPH_BOX[3] - K.GLYPH_BOX[1]) / 2 * k)
    check("fidelity: glyph stays inside the circular crop of the profile mark", corner < 750, f"corner radius {corner:.0f} of 750")

    for f in glob.glob(os.path.join(tmp, "*")):
        os.remove(f)
    os.rmdir(tmp)

    # ---- portability: CairoSVG vs Chromium
    import cairosvg
    worst = []
    for path in PAGES + sorted(glob.glob(os.path.join(DIST, "logos", "*.svg"))):
        w = 960 if "pages" in path else 400
        a = raster(path, w)
        png = cairosvg.svg2png(url=path, output_width=w, output_height=a.shape[0], background_color="#808080")
        b = np.array(Image.open(io.BytesIO(png)).convert("RGB"))
        worst.append((diff_frac(a, b, 96), os.path.basename(path)))
    worst.sort(reverse=True)
    check("portability: CairoSVG and Chromium agree on every page and logo (<1.5% pixels differ)", worst[0][0] < 0.015, f"worst {worst[0][1]} {worst[0][0] * 100:.2f}%")

    # ---- master renders and is not blank
    pg.set_viewport_size({"width": 1920, "height": 1080})
    m = raster(MASTER, 480)
    check("render: master renders with teal gutters and white/black pages", m.std() > 30 and (m == np.array([0, 199, 197])).all(axis=2).mean() > 0.01)
    br.close()

fails = [r for r in RESULTS if not r[1]]
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} checks passed")
sys.exit(1 if fails else 0)
