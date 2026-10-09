#!/usr/bin/env python3
"""GEMINII brand kit package: verification suite.

    python3 tests/verify_package.py                    # all groups except extended; exits non-zero on any failure
    python3 tests/verify_package.py --extended         # also compile with Tailwind v3 and v4 (needs node and network)
    python3 tests/verify_package.py --only files,css   # chosen groups
    python3 tests/verify_package.py --list             # group names

Groups: files, assets, palette, tokens, css, docs, kit, browser, geometry, a11y, behavior, zip, extended.
Independent oracles: the WCAG formula, the kit type scale and the kit button colors are written out here,
not imported from the generator, so the generator cannot agree with itself by accident.
"""
import argparse
import glob
import hashlib
import http.server
import json
import math
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARTER = os.path.join(ROOT, "web", "starter")
AXE = os.path.join(ROOT, "tests", "vendor", "axe.min.js")

BLACK, TEAL, WHITE = "#000000", "#00c7c5", "#ffffff"
GEM_NEUTRALS = {"#e0e1dd", "#b3b2b2", "#494949", "#373737"}
RESULTS = []
GROUPS = ["files", "assets", "palette", "tokens", "css", "docs", "kit", "browser", "geometry", "a11y", "behavior", "zip", "extended"]


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


def skip(name, why):
    print(f"SKIP {name}  [{why}]", flush=True)


def read(*parts, binary=False):
    with open(os.path.join(ROOT, *parts), "rb" if binary else "r", **({} if binary else {"encoding": "utf-8"})) as f:
        return f.read()


def walk_files():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if d not in ("__pycache__", "node_modules", ".pytest_cache"))
        for f in sorted(fn):
            if f.endswith(".pyc"):
                continue
            out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return out


# ------------------------------------------------------------------ oracles
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = lum(rgb(a)), lum(rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


KIT_SCALE = {  # name: (px, line px) at 1280 and wider: kit page 10
    "display": (120, 120), "h1": (72, 80), "h2": (48, 56), "h3": (32, 40), "body-lg": (24, 36), "body": (18, 28), "label": (14, 20),
}
MIN_SCALE = {"display": 48, "h1": 36, "h2": 28, "h3": 24, "body-lg": 20, "body": 18, "label": 14}
KIT_BUTTONS = {  # kit page 11 (light) and 12 (dark): (bg, text, border) default and pressed
    "light": {"primary": ((BLACK, WHITE, BLACK), (TEAL, BLACK, BLACK)),
              "secondary": ((TEAL, BLACK, BLACK), (BLACK, TEAL, BLACK)),
              "tertiary": ((WHITE, BLACK, BLACK), (BLACK, WHITE, BLACK))},
    "dark": {"primary": ((WHITE, BLACK, WHITE), (TEAL, BLACK, TEAL)),
             "secondary": ((TEAL, BLACK, TEAL), (BLACK, TEAL, TEAL)),
             "tertiary": ((BLACK, WHITE, WHITE), (WHITE, BLACK, WHITE))},
}


# ================================================================== files
def group_files():
    expected = [
        "README.md", "BRAND.md", "AI_BRIEF.md", "brand.json", "MANIFEST.sha256",
        "docs/01-assets.md", "docs/02-tokens.md", "docs/03-components.md", "docs/04-website-guide.md", "docs/05-accessibility.md",
        "docs/06-open-items.md", "docs/07-testing-and-build.md",
        "guidelines/GEMINII_Brandkit.pdf", "guidelines/GEMINII_Brandkit.svg",
        "logos/sprite.svg", "icons/sprite.svg",
        "favicons/favicon.ico", "favicons/favicon.svg", "favicons/apple-touch-icon.png", "favicons/icon-192.png",
        "favicons/icon-512.png", "favicons/icon-maskable-512.png", "favicons/site.webmanifest",
        "social/og-image.png", "social/linkedin-banner-1584x396.png", "social/x-header-1500x500.png",
        "social/youtube-banner-2560x1440.png", "social/profile-1080.png",
        "fonts/Arvo-Regular.woff2", "fonts/Arvo-Bold.woff2", "fonts/Arvo-Regular.ttf", "fonts/Arvo-Bold.ttf", "fonts/OFL.txt",
        "tokens/tokens.css", "tokens/tokens.json", "tokens/tokens.scss", "tokens/tailwind.preset.cjs", "tokens/tailwind-theme.css",
        "css/fonts.css", "css/base.css", "css/components.css", "css/brand.css", "css/brand.min.css",
        "js/theme-init.js", "js/brand.js",
        "web/starter/index.html", "web/starter/styleguide.html", "web/starter/robots.txt", "web/starter/README.md",
        "web/starter/favicon.ico", "web/starter/site.webmanifest", "web/starter/assets/css/brand.min.css",
        "web/starter/assets/css/styleguide.css", "web/starter/assets/js/brand.js", "web/starter/assets/fonts/Arvo-Bold.woff2",
        "tools/build_package.py", "tools/build_site.py", "tools/tokens.py", "tools/icons.py", "tools/requirements.txt",
        "tools/kit/kitlib.py", "tools/kit/build.py", "tools/kit/verify_kit.py", "tests/verify_package.py", "tests/vendor/axe.min.js",
    ]
    expected += [f"guidelines/pages/{i:02d}-{n}.svg" for i, n in enumerate(
        ["cover", "contents", "logo-suite", "wordmark", "color-versions", "misuse", "palette", "contrast-gradient", "typeface",
         "type-scale", "ui-light", "ui-dark"], 1)]
    for n in ("wordmark-full-color-on-dark", "wordmark-full-color-on-light", "wordmark-white", "wordmark-black", "wordmark-currentcolor",
              "icon-gradient-on-dark", "icon-gradient-on-light", "icon-white", "icon-black", "icon-teal", "icon-currentcolor",
              "profile-mark-square", "profile-mark-circle", "gem-full-color", "gem-white", "gem-black", "gem-currentcolor"):
        expected.append(f"logos/svg/{n}.svg")
    missing = [f for f in expected if not os.path.isfile(os.path.join(ROOT, f))]
    check("files: every expected file exists", not missing, f"{len(expected)} files" if not missing else str(missing[:8]))

    # manifest
    man = {}
    for line in read("MANIFEST.sha256").splitlines():
        h, rel = line.split("  ", 1)
        man[rel] = h
    actual = [f for f in walk_files() if f != "MANIFEST.sha256" and not f.startswith("tests/.report")]
    bad = [f for f in actual if f not in man or hashlib.sha256(read(f, binary=True)).hexdigest() != man[f]]
    gone = [f for f in man if f not in actual]
    check("files: MANIFEST.sha256 matches every file (no stray, missing or edited files)", not bad and not gone,
          f"{len(actual)} files" if not (bad or gone) else str((bad + gone)[:6]))

    # starter parity
    pairs = []
    for sub, src in (("css/brand.css", "css/brand.css"), ("css/brand.min.css", "css/brand.min.css"), ("js/brand.js", "js/brand.js"),
                     ("js/theme-init.js", "js/theme-init.js"), ("fonts/Arvo-Regular.woff2", "fonts/Arvo-Regular.woff2"),
                     ("fonts/Arvo-Bold.woff2", "fonts/Arvo-Bold.woff2"), ("icons/sprite.svg", "icons/sprite.svg"),
                     ("logos/sprite.svg", "logos/sprite.svg"), ("social/og-image.png", "social/og-image.png")):
        pairs.append((f"web/starter/assets/{sub}", src))
    for f in os.listdir(os.path.join(ROOT, "logos", "svg")):
        pairs.append((f"web/starter/assets/logos/svg/{f}", f"logos/svg/{f}"))
    for f in os.listdir(os.path.join(ROOT, "favicons")):
        pairs.append((f"web/starter/{f}", f"favicons/{f}"))
    diff = [a for a, b in pairs if not os.path.isfile(os.path.join(ROOT, a)) or read(a, binary=True) != read(b, binary=True)]
    check("files: starter assets are byte-identical to the canonical files", not diff, f"{len(pairs)} files" if not diff else str(diff[:5]))

    bundle = "\n".join(read(p_) for p_ in ("tokens/tokens.css", "css/fonts.css", "css/base.css", "css/components.css"))
    check("files: css/brand.css is the exact concatenation of tokens, fonts, base, components", read("css/brand.css") == bundle)


# ================================================================== assets
def group_assets():
    from PIL import Image
    from fontTools.ttLib import TTFont
    svgs = sorted(glob.glob(os.path.join(ROOT, "logos", "**", "*.svg"), recursive=True) + glob.glob(os.path.join(ROOT, "icons", "**", "*.svg"), recursive=True)
                  + glob.glob(os.path.join(ROOT, "guidelines", "**", "*.svg"), recursive=True) + glob.glob(os.path.join(ROOT, "favicons", "*.svg")))
    bad, forbidden = [], []
    for f in svgs:
        try:
            tree = ET.fromstring(open(f, encoding="utf-8").read())
        except ET.ParseError as e:
            bad.append((os.path.basename(f), str(e)))
            continue
        for el in tree.iter():
            tag = el.tag.split("}")[-1]
            if tag in ("text", "tspan", "image", "foreignObject", "script", "style", "filter"):
                forbidden.append((os.path.basename(f), tag))
            for k, v in el.attrib.items():
                if k.split("}")[-1].startswith("on") or (k.endswith("href") and not v.startswith("#")):
                    forbidden.append((os.path.basename(f), k))
    check("assets: all SVGs are well-formed", not bad, f"{len(svgs)} files" if not bad else str(bad[:3]))
    check("assets: SVGs have no text, raster, script, style, filter or external reference", not forbidden, str(forbidden[:4]))

    # PNG sizes
    probs = []
    for f in glob.glob(os.path.join(ROOT, "logos", "png", "*.png")):
        m = re.search(r"-(\d+)w\.png$", f)
        im = Image.open(f)
        name = os.path.basename(f)
        if im.width != int(m.group(1)):
            probs.append(name + " width")
        elif "profile-mark-square" in f:
            # platform avatars are opaque: no alpha channel, or alpha 255 everywhere
            if im.mode == "RGBA" and im.getchannel("A").getextrema()[0] != 255:
                probs.append(name + " not opaque")
            elif im.mode not in ("RGB", "RGBA"):
                probs.append(name + " mode " + im.mode)
        elif im.mode != "RGBA":
            probs.append(name + " not RGBA")
        elif ("profile-mark-circle" in f or "wordmark" in f) and im.getpixel((0, 0))[3] != 0:
            probs.append(name + " corner not transparent")
    check("assets: logo PNG widths match their names; all are RGBA with transparency except the opaque square avatar", not probs and len(glob.glob(os.path.join(ROOT, "logos", "png", "*.png"))) == 42, str(probs[:4]))
    want = {"favicons/apple-touch-icon.png": (180, 180), "favicons/icon-192.png": (192, 192), "favicons/icon-512.png": (512, 512),
            "favicons/icon-maskable-512.png": (512, 512), "social/og-image.png": (1200, 630), "social/linkedin-banner-1584x396.png": (1584, 396),
            "social/x-header-1500x500.png": (1500, 500), "social/youtube-banner-2560x1440.png": (2560, 1440), "social/profile-1080.png": (1080, 1080)}
    wrong = []
    for f, sz in want.items():
        im = Image.open(os.path.join(ROOT, f))
        if im.size != sz:
            wrong.append((f, im.size))
        a = im.convert("RGBA").getchannel("A")
        if a.getextrema()[0] != 255:
            wrong.append((f, "not opaque"))
    check("assets: app icons, banners and share image have the right pixel size and are opaque", not wrong, str(wrong[:3]))
    ico = Image.open(os.path.join(ROOT, "favicons", "favicon.ico"))
    check("assets: favicon.ico holds 16, 32 and 48 px", sorted(ico.info.get("sizes", [])) == [(16, 16), (32, 32), (48, 48)], str(ico.info.get("sizes")))

    # maskable safe zone
    im = Image.open(os.path.join(ROOT, "favicons", "icon-maskable-512.png")).convert("RGB")
    px = im.load()
    far = 0
    for y in range(512):
        for x in range(512):
            r, g, b = px[x, y]
            if abs(r - 0) + abs(g - 199) + abs(b - 197) > 60:
                far = max(far, math.hypot(x - 255.5, y - 255.5))
    check("assets: maskable icon glyph sits inside the 80% safe circle", far <= 0.4 * 512 + 2, f"farthest {far:.0f} px of {0.4 * 512:.0f}")

    man = json.loads(read("favicons/site.webmanifest"))
    ok = man["theme_color"] == BLACK and man["background_color"] == BLACK and any(i.get("purpose") == "maskable" for i in man["icons"])
    for i in man["icons"]:
        w, h = map(int, i["sizes"].split("x"))
        ok = ok and Image.open(os.path.join(ROOT, "favicons", i["src"])).size == (w, h)
    check("assets: web manifest is valid, icons exist at their stated size, one is maskable", ok)

    # fonts
    probs = []
    for style, wt in (("Regular", 400), ("Bold", 700)):
        for ext in ("woff2", "ttf"):
            raw = read(f"fonts/Arvo-{style}.{ext}", binary=True)
            if ext == "woff2" and raw[:4] != b"wOF2":
                probs.append(f"{style} woff2 magic")
            f = TTFont(os.path.join(ROOT, "fonts", f"Arvo-{style}.{ext}"))
            fam = f["name"].getDebugName(1)
            if fam != "Arvo" and not (fam or "").startswith("Arvo"):
                probs.append((style, ext, fam))
            if f["OS/2"].usWeightClass != wt:
                probs.append((style, ext, "weight", f["OS/2"].usWeightClass))
            cm = f.getBestCmap()
            if any(ord(c) not in cm for c in map(chr, range(32, 127))):
                probs.append((style, ext, "ASCII coverage"))
    check("assets: Arvo woff2 and ttf are valid, correct family and weight, full ASCII", not probs, str(probs[:3]))
    check("assets: OFL license ships with the fonts", "SIL OPEN FONT LICENSE" in read("fonts/OFL.txt").upper())

    pdf = read("guidelines/GEMINII_Brandkit.pdf", binary=True)
    from pypdf import PdfReader
    r = PdfReader(os.path.join(ROOT, "guidelines", "GEMINII_Brandkit.pdf"))
    check("assets: guidelines PDF has 12 bookmarked pages", len(r.pages) == 12 and len(r.outline) == 12, f"{len(r.pages)} pages, {len(r.outline)} bookmarks")


# ================================================================== palette
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


def on_ramp(color, far):
    """True when color = lerp(teal, far, u) for some u in [0,1] (2 levels of rounding allowed)."""
    t, f, c = rgb(TEAL), rgb(far), rgb(color)
    d = [f[i] - t[i] for i in range(3)]
    den = sum(x * x for x in d)
    u = sum((c[i] - t[i]) * d[i] for i in range(3)) / den
    if not -0.01 <= u <= 1.01:
        return False
    return all(abs(t[i] + u * d[i] - c[i]) <= 2.5 for i in range(3))


def group_palette():
    offenders = []
    files = (glob.glob(os.path.join(ROOT, "logos", "**", "*.svg"), recursive=True) + glob.glob(os.path.join(ROOT, "icons", "**", "*.svg"), recursive=True)
             + glob.glob(os.path.join(ROOT, "guidelines", "**", "*.svg"), recursive=True) + glob.glob(os.path.join(ROOT, "favicons", "*.svg")))
    for f in files:
        tree = ET.fromstring(open(f, encoding="utf-8").read())
        parents = {c: p_ for p_ in tree.iter() for c in p_}
        for el in tree.iter():
            tag = el.tag.split("}")[-1]
            for k, v in el.attrib.items():
                if k not in ("fill", "stroke", "stop-color", "color", "style"):
                    continue  # data-t and aria-label carry text (hex labels), not paint
                for h in HEX.findall(v):
                    h = h.lower()
                    if h in (BLACK, TEAL, WHITE) or h in GEM_NEUTRALS:
                        continue
                    if tag == "rect" and k == "fill" and (on_ramp(h, WHITE) or on_ramp(h, BLACK)):
                        continue  # swatches sampled from the gradient ramp (kit page 3)
                    grad = parents.get(el)
                    gt = grad.tag.split("}")[-1] if grad is not None else ""
                    r, g, b = rgb(h)
                    if tag == "stop" and gt == "radialGradient" and r == g == b:
                        continue
                    if tag == "stop" and gt == "linearGradient" and (on_ramp(h, WHITE) or on_ramp(h, BLACK)):
                        continue
                    offenders.append((os.path.relpath(f, ROOT), h))
    check("palette: SVGs use only black, teal, white, the gem neutrals, gradient ramps and the gem glow", not offenders, f"{len(files)} files" if not offenders else str(offenders[:5]))

    bad = []
    for f in ("css/base.css", "css/components.css", "css/fonts.css"):
        for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", read(f)):
            if h.lower() not in ("#fff", "#000", "#0000", "#ffffff", "#000000"):
                bad.append((f, h))
    check("palette: component CSS has no literal color other than black, white and transparent", not bad, str(bad[:4]))
    tok = read("tokens/tokens.css")
    bad = [h for h in HEX.findall(tok) if h.lower() not in (BLACK, TEAL, WHITE) and not (on_ramp(h, WHITE) or on_ramp(h, BLACK))]
    check("palette: tokens.css holds only the three colors and gradient interpolations", not bad, str(bad[:4]))
    html_bad = []
    for f in ("index.html", "styleguide.html"):
        t = read("web", "starter", f)
        for tag_src in re.findall(r"<[^>]+>", t):  # hex values printed as visible text (spec tables) are fine; paint in markup is not
            for h in HEX.findall(tag_src):
                if h.lower() != BLACK:
                    html_bad.append((f, h))
        if re.search(r"\sstyle\s*=", t) or "<style" in t:
            html_bad.append((f, "inline style"))
    check("palette: starter pages have no color literals and no inline styles", not html_bad, str(html_bad[:4]))


# ================================================================== tokens
def css_vars(text, first_block_only=True):
    m = re.search(r":root\s*\{(.*?)\n\}", text, re.S)
    block = m.group(1) if first_block_only else text
    return dict(re.findall(r"(--[a-z0-9-]+):\s*(.*?);", block, re.S))


def px_of(v):
    v = v.strip()
    if v.endswith("rem"):
        return float(v[:-3]) * 16
    if v.endswith("px"):
        return float(v[:-2])
    return float(v)


def group_tokens():
    css = css_vars(read("tokens/tokens.css"))
    tj = json.loads(read("tokens/tokens.json"))
    check("tokens: three colors equal the kit palette in css and json",
          (css["--gm-black"], css["--gm-teal"], css["--gm-white"]) == (BLACK, TEAL, WHITE)
          and (tj["color"]["black"]["$value"], tj["color"]["teal"]["$value"], tj["color"]["white"]["$value"]) == (BLACK, TEAL, WHITE))
    errs = []
    for name, (px, lh) in KIT_SCALE.items():
        t = tj["typography"][name]["$value"]
        if float(t["fontSize"][:-2]) != px or round(float(t["lineHeight"]) * px) != lh:
            errs.append((name, t["fontSize"], t["lineHeight"]))
        size = css[f"--gm-text-{name}-size"]
        mx = float(re.findall(r"([\d.]+)rem\)?$", size)[-1]) * 16 if "clamp" in size else px_of(size)
        mn = float(re.search(r"clamp\(([\d.]+)rem", size).group(1)) * 16 if "clamp" in size else px_of(size)
        if round(mx, 2) != px or round(mn, 2) != MIN_SCALE[name]:
            errs.append((name, "css range", mn, mx))
    check("tokens: type scale equals kit page 10 at 1280 px and the documented minimums at 360 px", not errs, str(errs[:3]))

    errs = []
    for k, v in tj["space"].items():
        if px_of(css[f"--gm-space-{k}"]) != px_of(v["$value"]):
            errs.append(("space", k))
    for k, v in tj["radius"].items():
        if px_of(css[f"--gm-radius-{k}"]) != px_of(v["$value"]):
            errs.append(("radius", k))
    for k, v in tj["border"].items():
        if px_of(css[f"--gm-border-{k}"]) != px_of(v["$value"]):
            errs.append(("border", k))
    for k, v in tj["breakpoint"].items():
        if px_of(css[f"--gm-bp-{k}"]) != px_of(v["$value"]):
            errs.append(("bp", k))
    check("tokens: tokens.json and tokens.css agree on spacing, radius, border, breakpoints", not errs, str(errs[:4]))

    scss = dict(re.findall(r"\$([a-z0-9-]+):\s*(.*?);", read("tokens/tokens.scss")))
    miss = [k for k, v in css.items() if not k.startswith("--gm-gradient") and scss.get(k[2:]) != v]
    check("tokens: tokens.scss mirrors every css variable exactly", not miss, str(miss[:4]))

    if shutil.which("node"):
        js = subprocess.run(["node", "-e", "console.log(JSON.stringify(require(process.argv[1])))", os.path.join(ROOT, "tokens", "tailwind.preset.cjs")],
                            capture_output=True, text=True)
        ok = js.returncode == 0
        detail = js.stderr[:200]
        if ok:
            tw = json.loads(js.stdout)["theme"]
            ok = (tw["colors"]["teal"] == TEAL and tw["colors"]["black"] == BLACK and tw["colors"]["white"] == WHITE
                  and set(tw["colors"]) == {"transparent", "current", "black", "teal", "white", "bg", "fg"}
                  and tw["fontSize"]["display"][0] == css["--gm-text-display-size"]
                  and tw["spacing"]["4"] == css["--gm-space-4"] and tw["screens"]["md"] == css["--gm-bp-md"]
                  and tw["boxShadow"] == {"none": "none"})
            detail = "palette restricted to 3 colors + theme aliases"
        check("tokens: Tailwind v3 preset loads and matches the css tokens", ok, detail)
    else:
        skip("tokens: Tailwind v3 preset", "node not found")
    tw4 = read("tokens/tailwind-theme.css")
    ok = (f"--color-teal: {TEAL};" in tw4 and "--color-*: initial;" in tw4 and f"--text-display: {css['--gm-text-display-size']};" in tw4
          and f"--breakpoint-md: {css['--gm-bp-md']};" in tw4)
    check("tokens: Tailwind v4 theme matches the css tokens", ok)

    # contrast
    docs = read("docs/05-accessibility.md") + read("BRAND.md")
    bj = json.loads(read("brand.json"))
    errs = []
    for pr in bj["contrast"]:
        r = ratio(pr["fg"], pr["bg"])
        if abs(r - pr["ratio"]) > 0.006:
            errs.append(("brand.json", pr))
        txt = f"{r:.2f}:1".replace(".00:1", ":1")
        if txt not in docs:
            errs.append(("docs", txt))
        want = "AAA" if r >= 7 else "AA" if r >= 4.5 else "FAIL"
        if pr["wcag"] != want and not (want == "AA" and pr["wcag"] in ("AA",)):
            errs.append(("level", pr["fg"], pr["bg"], want, pr["wcag"]))
    check("tokens: documented contrast ratios and levels equal an independent WCAG calculation", not errs, str(errs[:3]))

    # every button state passes text contrast, and matches the kit pages
    css_all = read("tokens/tokens.css")
    blocks = {"light": re.search(r":root,\n\[data-theme=\"light\"\],\n\.gm-surface-light \{(.*?)\n\}", css_all, re.S).group(1),
              "dark": re.search(r"\[data-theme=\"dark\"\],\n\.gm-surface-dark \{(.*?)\n\}", css_all, re.S).group(1)}
    errs, low = [], []
    for theme, blk in blocks.items():
        v = dict(re.findall(r"(--[a-z0-9-]+):\s*(.*?);", blk))
        for kind, (base, pressed) in KIT_BUTTONS[theme].items():
            got_base = (v[f"--gm-btn-{kind}-bg"], v[f"--gm-btn-{kind}-fg"], v[f"--gm-btn-{kind}-border"])
            got_pr = (v[f"--gm-btn-{kind}-pressed-bg"], v[f"--gm-btn-{kind}-pressed-fg"], v[f"--gm-btn-{kind}-pressed-border"])
            if got_base != base or got_pr != pressed:
                errs.append((theme, kind))
            for bg, fg, _ in (base, pressed):
                if ratio(bg, fg) < 4.5:
                    low.append((theme, kind, bg, fg))
    check("tokens: button colors equal kit pages 11 and 12 for every kind and state", not errs, str(errs[:3]))
    check("tokens: every button state has at least 4.5:1 text contrast", not low, str(low[:3]))


# ================================================================== css
def split_top(s, sep=","):
    out, depth, cur = [], 0, ""
    for c in s:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def group_css():
    files = {f: read(f) for f in ("css/base.css", "css/components.css", "tokens/tokens.css")}
    for f, t in files.items():
        t_ = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        check(f"css: {f} has balanced braces", t_.count("{") == t_.count("}"))
    # shadows: no blur
    blur = []
    for f, t in files.items():
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        for m in re.finditer(r"(box-shadow|--gm-ring-shadow|--gm-inset-shadow)\s*:\s*(.*?);", t, re.S):
            for sh in split_top(m.group(2)):
                toks = [x for x in split_top(re.sub(r"\s+", " ", sh), " ") if x and x != "inset"]
                lengths = [x for x in toks if re.fullmatch(r"-?[\d.]+(px|rem|em)?", x) or x.startswith("calc(") or x.startswith("var(--gm-ring") or x.startswith("var(--gm-border") or x.startswith("var(--gm-button-bar")]
                if len(lengths) >= 3 and lengths[2] not in ("0", "0px"):
                    blur.append((f, sh))
    check("css: every shadow has zero blur (flat system)", not blur, str(blur[:3]))
    allc = "\n".join(re.sub(r"/\*.*?\*/", "", t, flags=re.S) for t in files.values())
    check("css: no filter, backdrop-filter or text-shadow", not re.search(r"(?<![a-z-])(filter|backdrop-filter|text-shadow)\s*:", allc))
    ops = re.findall(r"(?<![a-z-])opacity\s*:\s*([^;]+);", allc)
    check("css: opacity is used only to hide native inputs (0) and reset placeholders (1)", all(o.strip() in ("0", "1") for o in ops), str(ops))
    rad = re.findall(r"border-radius\s*:\s*([^;]+);", allc)
    okr = all(r_.strip() in ("0", "50%", "2px", "var(--gm-radius-none)", "var(--gm-radius-sm)", "var(--gm-radius-md)", "var(--gm-radius-pill)") for r_ in rad)
    check("css: border-radius values are tokens, a circle, or the 2 px link ring", okr, str([r_ for r_ in rad if r_.strip() not in ("0", "50%", "2px") and not r_.strip().startswith("var(--gm-radius")]))
    # defined vars
    defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", allc))
    used = set(re.findall(r"var\((--[a-z0-9-]+)", allc))
    undefined = sorted(used - defined)
    check("css: every var(--x) used in the css is defined somewhere", not undefined, str(undefined[:6]))
    cls = set(re.findall(r"\.(gm-[a-z0-9_-]+)", allc))
    check("css: component classes are defined", len(cls) > 60, f"{len(cls)} gm- classes")


# ================================================================== docs
def group_docs():
    mds = ["README.md", "BRAND.md", "AI_BRIEF.md"] + [f"docs/{f}" for f in sorted(os.listdir(os.path.join(ROOT, "docs")))] + ["web/starter/README.md"]
    left = [f for f in mds if "{{" in read(f)]
    check("docs: no template placeholder left unfilled", not left, str(left))
    em = [f for f in mds if "—" in read(f) or "–" in read(f)]
    check("docs: no em or en dashes", not em, str(em))
    broken = []
    for f in mds:
        base = os.path.dirname(os.path.join(ROOT, f))
        for target in re.findall(r"\]\(([^)]+)\)", read(f)):
            if target.startswith(("http", "#", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, target.split("#")[0]))):
                broken.append((f, target))
    check("docs: relative markdown links resolve", not broken, str(broken[:4]))
    # paths named in backticks that look like package files
    missing = []
    for f in mds:
        for tick in re.findall(r"`([A-Za-z0-9_./-]+\.(?:md|css|js|json|svg|png|woff2|ttf|ico|html|py|cjs|scss|pdf|webmanifest|txt|sha256))`", read(f)):
            if "<" in tick or tick.startswith(("http", ".")) or "*" in tick:
                continue
            cands = [os.path.join(ROOT, tick), os.path.join(ROOT, "web", "starter", tick), os.path.join(ROOT, "tools", tick),
                     os.path.join(ROOT, "tests", tick), os.path.join(ROOT, "tools", "kit", tick), os.path.join(ROOT, "logos", "svg", tick),
                     os.path.join(ROOT, "logos", "png", tick), os.path.join(ROOT, "css", tick), os.path.join(ROOT, "js", tick),
                     os.path.join(ROOT, "fonts", tick), os.path.join(ROOT, "tokens", tick), os.path.join(ROOT, "favicons", tick),
                     os.path.join(ROOT, "web", "starter", "assets", tick), os.path.join(ROOT, "icons", tick), os.path.join(ROOT, "social", tick),
                     os.path.join(ROOT, "docs", tick), os.path.join(ROOT, "guidelines", tick)]
            if not any(os.path.exists(c) for c in cands):
                missing.append((f, tick))
    check("docs: every file named in the docs exists in the package", not missing, str(sorted(set(missing))[:8]))
    css = read("css/base.css") + read("css/components.css") + read("tokens/tokens.css") + read("web/starter/assets/css/styleguide.css")
    defined_cls = set(re.findall(r"\.(gm-[a-z0-9_-]+)", css))
    allowed = {"gm-theme", "gm-menu", "gm-"}
    bad = []
    for f in mds:
        t = re.sub(r"data-gm-[a-z-]+|--gm-[a-z0-9-]+|\$gm-[a-z0-9-]+|gm-btn-<kind>[a-z-]*", "", read(f))
        for c in set(re.findall(r"\bgm-[a-z0-9_-]+", t)):
            c = c.rstrip("-")
            if c not in defined_cls and c not in allowed and not any(d.startswith(c) for d in defined_cls):
                bad.append((f, c))
    check("docs: every gm- class named in the docs exists in the css", not bad, str(sorted(set(bad))[:8]))
    defined_vars = set(re.findall(r"(--gm-[a-z0-9-]+)\s*:", css)) | set(re.findall(r"(--gm-[a-z0-9-]+)\s*:", read("css/components.css")))
    badv = []
    for f in mds:
        for v in set(re.findall(r"--gm-[a-z0-9-]+", read(f))):
            if "<" in v:
                continue
            if v not in defined_vars and not any(d.startswith(v) for d in defined_vars):
                badv.append((f, v))
    check("docs: every --gm- variable named in the docs is defined", not badv, str(sorted(set(badv))[:8]))
    # numbers generated into docs are current
    fonts_kb = f"{(os.path.getsize(os.path.join(ROOT, 'fonts', 'Arvo-Regular.woff2')) + os.path.getsize(os.path.join(ROOT, 'fonts', 'Arvo-Bold.woff2'))) / 1024:.1f}"
    check("docs: measured sizes in the website guide equal the files", f"{fonts_kb} KB" in read("docs/04-website-guide.md"))
    bj = json.loads(read("brand.json"))
    check("docs: brand.json lists the same three colors", [bj["colors"][k]["hex"] for k in ("black", "teal", "white")] == [BLACK, TEAL, WHITE])


# ================================================================== kit
def group_kit():
    tmp = tempfile.mkdtemp(prefix="gm-verify-kit-")
    env = dict(os.environ, GEMINII_KIT_DIST=tmp)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "kit", "build.py")], env=env, capture_output=True, text=True)
    check("kit: the page generator rebuilds from source", r.returncode == 0, r.stdout.strip()[-60:] or r.stderr[-120:])
    same = []
    for f in sorted(glob.glob(os.path.join(tmp, "pages", "*.svg"))):
        if open(f, "rb").read() != read("guidelines", "pages", os.path.basename(f), binary=True):
            same.append(os.path.basename(f))
    for f in sorted(glob.glob(os.path.join(tmp, "logos", "*.svg"))):
        if open(f, "rb").read() != read("logos", "svg", os.path.basename(f), binary=True):
            same.append(os.path.basename(f))
    if open(os.path.join(tmp, "GEMINII_Brandkit.svg"), "rb").read() != read("guidelines/GEMINII_Brandkit.svg", binary=True):
        same.append("master")
    check("kit: packaged pages and logos are byte-identical to a fresh build", not same, str(same[:4]))
    v = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "kit", "verify_kit.py")], env=env, capture_output=True, text=True)
    tail = v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-200:]
    check("kit: the 36 kit checks (fidelity, geometry, layout, legibility, second-engine render) pass", v.returncode == 0 and "36/36" in v.stdout, tail)
    shutil.rmtree(tmp, ignore_errors=True)


# ================================================================== browser plumbing
class Handler(http.server.SimpleHTTPRequestHandler):
    csp = None
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".webmanifest": "application/manifest+json", ".woff2": "font/woff2", ".svg": "image/svg+xml", "": "application/octet-stream"}

    def __init__(self, *a, **k):
        super().__init__(*a, directory=STARTER, **k)

    def end_headers(self):
        if self.server.csp:
            self.send_header("Content-Security-Policy", self.server.csp)
        super().end_headers()

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    csp = None


def start_server(csp=None):
    srv = Server(("127.0.0.1", 0), Handler)
    srv.csp = csp
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


PAGES = ["index.html", "styleguide.html"]

JS_TEXT_CONTRAST = r"""
() => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r:p[0], g:p[1], b:p[2], a:p.length > 3 ? p[3] : 1}; };
  const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.backgroundImage !== 'none') return null; const c = parse(cs.backgroundColor); if (c && c.a > 0) return c; } return {r:255,g:255,b:255,a:1}; };
  const out = [], seen = new Set(); let n = 0;
  const test = (el, label) => {
    if (el.closest('[data-demo-fail],[aria-hidden="true"],script,style,[hidden],:disabled,[aria-disabled="true"],.is-disabled,option')) return;
    if (!el.getClientRects().length) return;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') return;
    const fg = parse(cs.color), bg = bgOf(el); if (!fg || !bg) return;
    const L1 = lum(fg), L2 = lum(bg), r = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700, large = fs >= 24 || (bold && fs >= 18.66);
    n++;
    if (r < (large ? 3 : 4.5)) out.push({text: label.slice(0, 30), fg: cs.color, bg: `rgb(${bg.r},${bg.g},${bg.b})`, ratio: +r.toFixed(2), size: fs, el: el.className || el.tagName});
  };
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const t = w.currentNode; if (t.nodeValue.trim()) test(t.parentElement, t.nodeValue.trim()); }
  document.querySelectorAll('input:not([type=checkbox]):not([type=radio]),textarea,select').forEach(el => test(el, el.placeholder || el.value || el.tagName));
  return {n, fails: out};
}
"""

JS_FOCUS = r"""
() => {
  const el = document.activeElement; if (!el || el === document.body) return null;
  const drawn = el.matches('.gm-check > input, .gm-radio > input, .gm-switch > input') ? el.nextElementSibling : el;
  const cs = getComputedStyle(drawn);
  return {idx: [...document.querySelectorAll('*')].indexOf(el), tag: el.tagName.toLowerCase(), cls: (el.className || '').toString().slice(0, 40), id: el.id || '', text: (el.textContent || '').trim().slice(0, 20),
    outline: cs.outlineStyle, width: parseFloat(cs.outlineWidth), shadow: cs.boxShadow, rect: drawn.getBoundingClientRect().toJSON()};
}
"""

JS_TABBABLE = r"""
() => {
  const groups = new Set();
  const inClosedDetails = e => { for (let p = e.parentElement; p; p = p.parentElement) { if (p.tagName === 'DETAILS' && !p.open && e !== p.querySelector(':scope > summary')) return true; } return false; };
  return [...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]):not([type=hidden]),select:not([disabled]),textarea:not([disabled]),summary,[tabindex]')]
    .filter(e => e.tabIndex >= 0 && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden' && !inClosedDetails(e))
    .filter(e => { if (e.type !== 'radio' || !e.name) return true; if (groups.has(e.name)) return false; groups.add(e.name); return true; }).length;  // one Tab stop per radio group
}
"""


class Browser:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch()

    def close(self):
        self.b.close()
        self.pw.stop()

    def load(self, base, page, width=1280, scheme="light", js=True, height=900, reduced=False, forced=False, init=None):
        kw = dict(viewport={"width": width, "height": height}, color_scheme=scheme, java_script_enabled=js)
        if reduced:
            kw["reduced_motion"] = "reduce"
        if forced:
            kw["forced_colors"] = "active"
        ctx = self.b.new_context(**kw)
        pg = ctx.new_page()
        logs, failed, reqs = [], [], []
        pg.on("console", lambda m: logs.append((m.type, m.text)) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        pg.on("requestfailed", lambda r: failed.append((r.url, r.failure)))
        pg.on("response", lambda r: failed.append((r.url, r.status)) if r.status >= 400 else None)
        pg.on("request", lambda r: reqs.append(r.url))
        if init:
            pg.add_init_script(init)
        pg.goto(f"{base}/{page}")
        pg.wait_for_load_state("networkidle")
        if js:
            pg.evaluate("document.fonts.ready.then(() => true)")
        return ctx, pg, logs, failed, reqs


# ================================================================== browser
def group_browser(br, base):
    from fontTools.ttLib import TTFont
    cmap = set(TTFont(os.path.join(ROOT, "fonts", "Arvo-Regular.ttf")).getBestCmap()) | set(TTFont(os.path.join(ROOT, "fonts", "Arvo-Bold.ttf")).getBestCmap())
    css = read("css/base.css") + read("css/components.css") + read("tokens/tokens.css") + read("web/starter/assets/css/styleguide.css")
    known = set(re.findall(r"\.([a-z][a-z0-9_-]+)", css)) | {"is-hover", "is-pressed", "is-focus", "is-disabled", "is-open", "is-current", "js"}
    problems = {k: [] for k in ("console", "network", "external", "scroll", "fonts", "h1", "headings", "alt", "ids", "glyphs", "classes", "refs", "inline", "meta", "theme", "landmarks")}
    combos = 0
    for page in PAGES:
        for width in (360, 768, 1280, 1920):
            for scheme in ("light", "dark"):
                combos += 1
                ctx, pg, logs, failed, reqs = br.load(base, page, width, scheme)
                tag = f"{page}@{width}/{scheme}"
                if logs:
                    problems["console"].append((tag, logs[:2]))
                if failed:
                    problems["network"].append((tag, failed[:2]))
                ext = [u for u in reqs if not u.startswith(base) and not u.startswith("data:")]
                if ext:
                    problems["external"].append((tag, ext[:2]))
                d = pg.evaluate("""() => ({sw: document.documentElement.scrollWidth, iw: window.innerWidth,
                    f400: document.fonts.check('400 16px Arvo'), f700: document.fonts.check('700 16px Arvo'),
                    loaded: [...document.fonts].filter(f => f.family.replace(/"/g,'') === 'Arvo').map(f => f.weight + ':' + f.status),
                    h1: document.querySelectorAll('h1').length,
                    heads: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => h.getClientRects().length).map(h => +h.tagName[1]),
                    noalt: [...document.images].filter(i => !i.hasAttribute('alt') || !i.hasAttribute('width') || !i.hasAttribute('height')).map(i => i.src.split('/').pop()),
                    dupe: (() => { const s = {}, d = []; document.querySelectorAll('[id]').forEach(e => { if (s[e.id]) d.push(e.id); s[e.id] = 1; }); return d; })(),
                    text: [...new Set((document.body.innerText + document.title).split(''))].map(c => c.codePointAt(0)),
                    classes: [...new Set([...document.querySelectorAll('[class]')].flatMap(e => [...e.classList]))],
                    badref: [...document.querySelectorAll('[aria-controls],[aria-labelledby],[aria-describedby],label[for]')].flatMap(e => ['aria-controls','aria-labelledby','aria-describedby','for'].filter(a => e.hasAttribute(a)).flatMap(a => e.getAttribute(a).split(/\\s+/).filter(i => !document.getElementById(i)).map(i => a + '=' + i))),
                    inline: document.querySelectorAll('[style],style').length,
                    scripts: [...document.scripts].filter(s => !s.src && s.type !== 'application/ld+json').length,
                    lang: document.documentElement.lang, title: document.title, vp: !!document.querySelector('meta[name=viewport]'),
                    bg: getComputedStyle(document.body).backgroundColor,
                    landmarks: ['header','nav','main','footer'].map(t => document.querySelectorAll(t).length)
                })""")
                if d["sw"] > d["iw"]:
                    problems["scroll"].append((tag, d["sw"], d["iw"]))
                if not (d["f400"] and d["f700"]) or not d["loaded"] or any(not s.endswith("loaded") for s in d["loaded"]):
                    problems["fonts"].append((tag, d["loaded"]))
                if d["h1"] != 1:
                    problems["h1"].append((tag, d["h1"]))
                hs = d["heads"]
                if any(b - a > 1 for a, b in zip(hs, hs[1:])) or (hs and hs[0] != 1):
                    problems["headings"].append((tag, hs[:12]))
                if d["noalt"]:
                    problems["alt"].append((tag, d["noalt"][:3]))
                if d["dupe"]:
                    problems["ids"].append((tag, d["dupe"][:3]))
                miss = [chr(c) for c in d["text"] if c not in cmap and chr(c) not in "\n\r\t ​"]
                if miss:
                    problems["glyphs"].append((tag, miss[:6]))
                unk = [c for c in d["classes"] if c not in known]
                if unk:
                    problems["classes"].append((tag, unk[:6]))
                if d["badref"]:
                    problems["refs"].append((tag, d["badref"][:4]))
                if d["inline"] or d["scripts"]:
                    problems["inline"].append((tag, d["inline"], d["scripts"]))
                if not d["lang"] or not d["title"] or not d["vp"]:
                    problems["meta"].append((tag, d["lang"], d["title"], d["vp"]))
                if d["bg"] != ("rgb(0, 0, 0)" if scheme == "dark" else "rgb(255, 255, 255)"):
                    problems["theme"].append((tag, d["bg"]))
                if page == "index.html" and (min(d["landmarks"]) < 1 or d["landmarks"][2] != 1):
                    problems["landmarks"].append((tag, d["landmarks"]))
                ctx.close()
    labels = {
        "console": "no console errors or warnings", "network": "no failed or 4xx requests", "external": "no third-party requests",
        "scroll": "no horizontal scroll", "fonts": "Arvo 400 and 700 load from the woff2 files", "h1": "exactly one h1",
        "headings": "heading levels never skip", "alt": "every image has alt, width and height", "ids": "no duplicate ids",
        "glyphs": "every character on the page exists in Arvo", "classes": "every class used is defined in the css",
        "refs": "aria and label references resolve", "inline": "no inline styles or scripts", "meta": "lang, title and viewport present",
        "theme": "page background follows the system color scheme", "landmarks": "header, nav, main, footer present",
    }
    for k, label in labels.items():
        check(f"browser: {label} ({combos} loads: 2 pages x 4 widths x 2 schemes)", not problems[k], str(problems[k][:2]))

    # strict CSP
    m = re.search(r"Content-Security-Policy: (.+)", read("docs/04-website-guide.md"))
    policy = m.group(1).strip()
    srv, cbase = start_server(csp=policy)
    viol = []
    for page in PAGES:
        ctx, pg, logs, failed, reqs = br.load(cbase, page, 1280, "light",
                                              init="window.__v=[];document.addEventListener('securitypolicyviolation',e=>window.__v.push(e.violatedDirective+' '+e.blockedURI));")
        v = pg.evaluate("window.__v")
        f400 = pg.evaluate("document.fonts.check('700 16px Arvo')")
        pg.click("[data-gm-theme-toggle]")
        themed = pg.evaluate("document.documentElement.getAttribute('data-theme')")
        if v or logs or failed or not f400 or themed not in ("dark", "light"):
            viol.append((page, v, logs[:2], failed[:2], f400, themed))
        ctx.close()
    srv.shutdown()
    check("browser: starter and style guide run under the documented strict CSP with no violation", not viol, str(viol[:2]))


# ================================================================== geometry
def group_geometry(br, base):
    ctx, pg, *_ = br.load(base, "styleguide.html", 1280, "light")
    probe = """(sel) => { const e = document.querySelector(sel); if (!e) return null; const cs = getComputedStyle(e), r = e.getBoundingClientRect();
        return {w: r.width, h: r.height, bw: parseFloat(cs.borderTopWidth), rad: cs.borderTopLeftRadius, fs: parseFloat(cs.fontSize), fw: cs.fontWeight,
                ls: cs.letterSpacing, tt: cs.textTransform, pl: parseFloat(cs.paddingLeft), pt: parseFloat(cs.paddingTop), bs: cs.borderTopStyle}; }"""
    P = lambda s: pg.evaluate(probe, s)
    b = P(".sg-matrix .gm-btn--primary:not(.is-hover):not(.is-pressed):not(.is-focus):not(:disabled)")
    check("geometry: button is 56 px high, 2 px border, 4 px radius, Bold 16 px uppercase, 0.12em tracking",
          b and round(b["h"]) == 56 and b["bw"] == 2 and b["rad"] == "4px" and b["fs"] == 16 and b["fw"] == "700" and b["tt"] == "uppercase" and abs(float(b["ls"][:-2]) - 1.92) < 0.01, str(b))
    sm = P(".gm-surface-dark .gm-btn--sm")
    check("geometry: small button is 52 px high", sm and round(sm["h"]) == 52, str(sm and sm["h"]))
    dis = pg.evaluate(probe.replace("document.querySelector(sel)", "document.querySelector('.sg-matrix .gm-btn:disabled')"), "")
    check("geometry: disabled button is dashed and Regular", dis and dis["bs"] == "dashed" and dis["fw"] == "400", str(dis))
    f = P("#sg-default")
    check("geometry: text field is 56 px high, 2 px border, 4 px radius, 18 px side padding, 18 px text",
          f and round(f["h"]) == 56 and f["bw"] == 2 and f["rad"] == "4px" and f["pl"] == 18 and f["fs"] == 18, str(f))
    ff = P("#sg-filled")
    check("geometry: a filled field is Bold, an empty one Regular", ff and ff["fw"] == "700" and f["fw"] == "400", f"{ff and ff['fw']} / {f['fw']}")
    err = pg.evaluate("getComputedStyle(document.querySelector('#sg-error')).boxShadow")
    check("geometry: error field edge reads 4 px (2 px border + 2 px inset)", "inset" in err and "2px" in err, err[:60])
    cb, rd, sw = P(".gm-check__box"), P(".gm-radio__dot"), P(".gm-switch__track")
    check("geometry: checkbox and radio are 26 px, switch is 56 x 32", cb["w"] == 26 and cb["h"] == 26 and rd["w"] == 26 and rd["h"] == 26 and rd["rad"] == "50%" and sw["w"] == 56 and sw["h"] == 32, f"{cb['w']} {rd['w']} {sw['w']}x{sw['h']}")
    tg = P(".gm-tag")
    check("geometry: tag is 38 px high, pill, 20 px padding, Bold 14 px", tg and round(tg["h"]) == 38 and tg["pl"] == 22 - 2 + 0 and tg["fs"] == 14 and tg["fw"] == "700", str(tg))
    cd = P(".gm-card")
    check("geometry: card has 2 px edge, square corners, 24 px padding", cd and cd["bw"] == 2 and cd["rad"] == "0px" and cd["pl"] == 24, str(cd))
    rl = P(".gm-rule")
    check("geometry: accent bar is 72 x 6", rl and rl["w"] == 72 and rl["h"] == 6, str(rl and (rl["w"], rl["h"])))
    nav = pg.evaluate("document.querySelector('.gm-nav__inner').getBoundingClientRect().height")
    check("geometry: header is 92 px high from 960 px", round(nav) == 92, str(nav))
    av = pg.evaluate("[...document.querySelectorAll('.gm-avatar')].map(a => Math.round(a.getBoundingClientRect().width))")
    check("geometry: avatar sizes are 32, 48, 64, 112", av == [32, 48, 64, 112], str(av))
    ctx.close()

    # type scale at 3 widths
    JS = """(cls) => { const e = document.createElement('p'); e.className = cls; e.textContent = 'x'; document.body.appendChild(e);
        const cs = getComputedStyle(e); const r = {fs: parseFloat(cs.fontSize), lh: parseFloat(cs.lineHeight), fw: cs.fontWeight, ls: cs.letterSpacing, tt: cs.textTransform}; e.remove(); return r; }"""
    cls = {"display": "gm-display", "h1": "gm-h1", "h2": "gm-h2", "h3": "gm-h3", "body-lg": "gm-body-lg", "body": "gm-body", "label": "gm-label-text"}
    errs, mono = [], {}
    for width in (360, 640, 960, 1280, 1920):
        ctx, pg, *_ = br.load(base, "index.html", width, "light")
        for name, c in cls.items():
            r = pg.evaluate(JS, c)
            px, lh = KIT_SCALE[name]
            mn = MIN_SCALE[name]
            if width >= 1280:
                want_fs, want_lh = px, lh
            elif width == 360:
                want_fs, want_lh = mn, round(mn * lh / px, 2)
            else:
                want_fs, want_lh = None, None
            if want_fs is not None and (abs(r["fs"] - want_fs) > 0.05 or abs(r["lh"] - want_lh) > 0.1):
                errs.append((name, width, r["fs"], r["lh"], want_fs, want_lh))
            mono.setdefault(name, []).append(r["fs"])
            if name == "label" and abs(float(r["ls"][:-2]) - 1.96) > 0.01:
                errs.append(("label tracking", r["ls"]))
            if name in ("display", "h1", "h2", "label") and r["tt"] != "uppercase" or name in ("h3", "body", "body-lg") and r["tt"] != "none":
                errs.append((name, "case", r["tt"]))
        ctx.close()
    check("geometry: type scale equals the kit at 1280 px and wider, the minimums at 360 px, correct case and tracking", not errs, str(errs[:3]))
    check("geometry: fluid sizes never shrink as the viewport grows", all(v == sorted(v) for v in mono.values()), str({k: v for k, v in mono.items() if v != sorted(v)}))

    ctx, pg, *_ = br.load(base, "index.html", 1920, "light")
    left = pg.evaluate("document.querySelector('.gm-hero .gm-container > *').getBoundingClientRect().left")
    wid = pg.evaluate("document.querySelector('#section-one .gm-container').clientWidth - 2 * parseFloat(getComputedStyle(document.querySelector('#section-one .gm-container')).paddingLeft)")
    check("geometry: at 1920 px the content column is 1728 px wide with 96 px margins, as on the kit canvas", round(left) == 96 and round(wid) == 1728, f"left {left}, width {wid}")
    ctx.close()


# ================================================================== a11y
def tab_walk(pg):
    pg.evaluate("window.scrollTo(0,0); document.activeElement && document.activeElement.blur()")
    stops, fails, first = [], [], None
    expected = pg.evaluate(JS_TABBABLE)
    for i in range(expected + 6):
        pg.keyboard.press("Tab")
        info = pg.evaluate(JS_FOCUS)
        if info is None:
            break
        key = info["idx"]
        if first is None:
            first = key
        elif key == first:
            break
        stops.append(key)
        if info["outline"] == "none" or info["width"] < 3 or "rgb" not in info["shadow"]:
            fails.append((info["tag"], info["cls"], info["text"], info["outline"], info["width"], info["shadow"][:30]))
    return expected, stops, fails


def group_a11y(br, base):
    axe_js = open(AXE, encoding="utf-8").read()
    tags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
    AX = """async (tags) => { const r = await axe.run({exclude: [['[data-demo-fail]']]}, {runOnly: {type: 'tag', values: tags}});
        return r.violations.map(v => ({id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' '))})); }"""
    viol, contrast_fail, n_text = [], [], 0
    for page in PAGES:
        for width in (360, 1280):
            for scheme in ("light", "dark"):
                ctx, pg, *_ = br.load(base, page, width, scheme)
                pg.add_script_tag(content=axe_js)
                v = pg.evaluate(AX, tags)
                if v:
                    viol.append((f"{page}@{width}/{scheme}", v[:3]))
                c = pg.evaluate(JS_TEXT_CONTRAST)
                n_text += c["n"]
                if c["fails"]:
                    contrast_fail.append((f"{page}@{width}/{scheme}", c["fails"][:3]))
                ctx.close()
    check("a11y: axe-core finds no violation (WCAG 2.2 A and AA, best practice) on both pages, 2 widths, 2 schemes", not viol, str(viol[:2]))
    check("a11y: every rendered text run meets WCAG AA against the background behind it", not contrast_fail, f"{n_text} runs checked" if not contrast_fail else str(contrast_fail[:2]))

    for page in PAGES:
        ctx, pg, *_ = br.load(base, page, 1280, "light")
        expected, stops, fails = tab_walk(pg)
        check(f"a11y: {page}: keyboard reaches every interactive element, each shows the double focus ring", expected == len(stops) and not fails and len(set(stops)) == len(stops),
              f"{len(stops)} of {expected} stops" if not fails else str(fails[:2]))
        ctx.close()
    ctx, pg, *_ = br.load(base, "index.html", 360, "light")
    expected, stops, fails = tab_walk(pg)
    check("a11y: index.html at 360 px (menu collapsed): every reachable element shows the ring", expected == len(stops) and not fails, f"{len(stops)} of {expected}")
    ctx.close()

    # target size
    ctx, pg, *_ = br.load(base, "styleguide.html", 1280, "light")
    small = pg.evaluate("""() => [...document.querySelectorAll('.gm-btn,.gm-nav__link,.gm-tab,.gm-input,.gm-textarea,.gm-select > select,.gm-check__box,.gm-radio__dot,.gm-switch__track,.gm-nav__toggle,.gm-card__link')]
        .filter(e => e.getClientRects().length).map(e => ({c: e.className, w: e.getBoundingClientRect().width, h: e.getBoundingClientRect().height})).filter(r => r.w < 24 || r.h < 24)""")
    check("a11y: no control is smaller than 24 x 24 px", not small, str(small[:3]))
    rows = pg.evaluate("""() => [...document.querySelectorAll('.gm-check,.gm-radio,.gm-switch')].map(e => e.getBoundingClientRect().height).filter(h => h < 44)""")
    check("a11y: checkbox, radio and switch rows are at least 44 px high", not rows, str(rows[:3]))
    ctx.close()

    # reduced motion, forced colors
    ctx, pg, *_ = br.load(base, "index.html", 1280, "light", reduced=True)
    d = pg.evaluate("[...document.querySelectorAll('.gm-btn,a')].map(e => parseFloat(getComputedStyle(e).transitionDuration.split(',')[0]))")
    check("a11y: prefers-reduced-motion removes transitions", d and max(d) <= 0.0001, f"max {max(d)}s")
    ctx.close()
    ctx, pg, *_ = br.load(base, "index.html", 1280, "light", forced=True)
    pg.keyboard.press("Tab"); pg.keyboard.press("Tab")
    o = pg.evaluate("(() => { const cs = getComputedStyle(document.activeElement); return [cs.outlineStyle, parseFloat(cs.outlineWidth)]; })()")
    check("a11y: in forced-colors mode the focus outline is still drawn", o[0] != "none" and o[1] >= 3, str(o))
    ctx.close()


# ================================================================== behavior
def group_behavior(br, base):
    # theme toggle, persistence, no flash
    ctx, pg, *_ = br.load(base, "index.html", 1280, "light", init="window.__t=[];document.addEventListener('DOMContentLoaded',()=>window.__t.push(document.documentElement.getAttribute('data-theme')))")
    bg0 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    pg.click("[data-gm-theme-toggle]")
    st = pg.evaluate("[document.documentElement.getAttribute('data-theme'), localStorage.getItem('gm-theme'), getComputedStyle(document.body).backgroundColor, document.querySelector('[data-gm-theme-toggle]').getAttribute('aria-pressed')]")
    pg.reload(); pg.wait_for_load_state("networkidle")
    t = pg.evaluate("window.__t")
    logos = pg.evaluate("[...document.querySelectorAll('.gm-nav__brand img')].filter(i => getComputedStyle(i).display !== 'none').map(i => i.className)")
    check("behavior: theme toggle switches to dark, saves the choice, and applies it before first paint after reload",
          bg0 == "rgb(255, 255, 255)" and st == ["dark", "dark", "rgb(0, 0, 0)", "true"] and t == ["dark"], f"{st} {t}")
    check("behavior: the header shows only the logo variant for the current theme (dark theme: the on-dark logo)", len(logos) == 1 and "gm-logo--on-dark" in logos[0], str(logos))
    pg.click("[data-gm-theme-toggle]")
    st2 = pg.evaluate("[document.documentElement.getAttribute('data-theme'), getComputedStyle(document.body).backgroundColor]")
    check("behavior: toggling again returns to light", st2 == ["light", "rgb(255, 255, 255)"], str(st2))
    ctx.close()
    ctx, pg, *_ = br.load(base, "index.html", 1280, "dark")
    bg = pg.evaluate("[document.documentElement.hasAttribute('data-theme'), getComputedStyle(document.body).backgroundColor]")
    check("behavior: with no saved choice the page follows the system dark setting", bg == [False, "rgb(0, 0, 0)"], str(bg))
    ctx.close()

    # mobile menu
    ctx, pg, *_ = br.load(base, "index.html", 360, "light")
    vis = lambda: pg.evaluate("[getComputedStyle(document.querySelector('.gm-nav__toggle')).display, getComputedStyle(document.querySelector('#gm-menu')).display, document.querySelector('.gm-nav__toggle').getAttribute('aria-expanded')]")
    v0 = vis()
    pg.click(".gm-nav__toggle")
    v1 = vis()
    pg.keyboard.press("Escape")
    v2 = vis()
    foc = pg.evaluate("document.activeElement.className")
    check("behavior: mobile menu is collapsed, opens on the toggle, closes on Escape and returns focus",
          v0 == ["flex", "none", "false"] and v1[1] == "flex" and v1[2] == "true" and v2 == ["flex", "none", "false"] and "gm-nav__toggle" in foc, f"{v0} {v1} {v2}")
    ctx.close()
    ctx, pg, *_ = br.load(base, "index.html", 1280, "light")
    d = pg.evaluate("[getComputedStyle(document.querySelector('.gm-nav__toggle')).display, getComputedStyle(document.querySelector('#gm-menu')).display]")
    check("behavior: at 960 px and wider the menu is inline and the toggle is hidden", d[0] == "none" and d[1] == "flex", str(d))
    ctx.close()
    ctx, pg, *_ = br.load(base, "index.html", 360, "light", js=False)
    d = pg.evaluate("[getComputedStyle(document.querySelector('.gm-nav__toggle')).display, getComputedStyle(document.querySelector('#gm-menu')).display]")
    check("behavior: without JavaScript the menu stays open and the toggle is hidden", d == ["none", "flex"], str(d))
    ctx.close()

    # tabs
    ctx, pg, *_ = br.load(base, "styleguide.html", 1280, "light")
    st = lambda: pg.evaluate("[...document.querySelectorAll('[data-gm-tabs] [role=tab]')].map(t => t.getAttribute('aria-selected') + (document.getElementById(t.getAttribute('aria-controls')).hidden ? 'h' : 'v')).join()")
    s0 = st()
    pg.click("#t2")
    s1 = st()
    pg.keyboard.press("ArrowRight")
    s2 = st(); f2 = pg.evaluate("document.activeElement.id")
    pg.keyboard.press("Home")
    s3 = st()
    pg.keyboard.press("End")
    s4 = st()
    pg.keyboard.press("ArrowRight")
    s5 = st()
    check("behavior: tabs follow the ARIA model (click, arrows, Home, End, wrap)",
          s0 == "truev,falseh,falseh" and s1 == "falseh,truev,falseh" and s2 == "falseh,falseh,truev" and f2 == "t3" and s3 == "truev,falseh,falseh" and s4 == "falseh,falseh,truev" and s5 == "truev,falseh,falseh",
          f"{s0} | {s1} | {s2} | {s3} | {s4} | {s5}")

    # fields and controls
    pg.fill("#sg-default", "abc")
    pg.evaluate("document.activeElement.blur()")  # focus is Bold by itself; measure the resting states
    fw = pg.evaluate("getComputedStyle(document.querySelector('#sg-default')).fontWeight")
    pg.fill("#sg-default", "")
    pg.evaluate("document.activeElement.blur()")
    fw0 = pg.evaluate("getComputedStyle(document.querySelector('#sg-default')).fontWeight")
    check("behavior: a filled field rests Bold, an emptied one returns to Regular", fw == "700" and fw0 == "400", f"{fw} {fw0}")
    first = "label.gm-check:nth-of-type(1)"
    bg_before = pg.evaluate("getComputedStyle(document.querySelector('.sg-controls .gm-check__box')).backgroundColor")
    pg.click(".sg-controls .gm-check")
    chk = pg.evaluate("[document.querySelector('.sg-controls .gm-check input').checked, getComputedStyle(document.querySelector('.sg-controls .gm-check__box')).backgroundColor]")
    check("behavior: clicking a checkbox label checks it and fills the box", bg_before == "rgb(255, 255, 255)" and chk == [True, "rgb(0, 0, 0)"], f"{bg_before} {chk}")
    pg.click(".gm-switch >> nth=0")
    tr = pg.evaluate("[getComputedStyle(document.querySelector('.gm-switch input')).opacity, getComputedStyle(document.querySelector('.gm-switch__track'), '::after').transform, getComputedStyle(document.querySelector('.gm-switch__track')).backgroundColor]")
    pg.wait_for_timeout(300)
    tr = pg.evaluate("[getComputedStyle(document.querySelector('.gm-switch__track'), '::after').transform, getComputedStyle(document.querySelector('.gm-switch__track')).backgroundColor]")
    check("behavior: switch turns teal and the knob travels 26 px", tr == ["matrix(1, 0, 0, 1, 26, 0)", "rgb(0, 199, 197)"], str(tr))
    ctx.close()


# ================================================================== zip
def group_zip():
    z = os.path.join(os.path.dirname(ROOT), "GEMINII_Brandkit.zip")
    if not os.path.isfile(z):
        skip("zip: archive matches the folder", "no GEMINII_Brandkit.zip next to the folder; run build_package.py --zip")
        return
    base = os.path.basename(ROOT)
    with zipfile.ZipFile(z) as zf:
        bad = zf.testzip()
        names = {n[len(base) + 1:]: n for n in zf.namelist() if not n.endswith("/")}
        files = set(walk_files())
        diff = [f for f in files if f not in names or hashlib.sha256(zf.read(names[f])).hexdigest() != hashlib.sha256(read(f, binary=True)).hexdigest()]
        extra = [n for n in names if n not in files]
    check("zip: archive is intact and identical to the folder, file for file", bad is None and not diff and not extra, f"{len(files)} files" if not (diff or extra) else str((diff + extra)[:4]))


# ================================================================== extended
def group_extended():
    if not shutil.which("npx"):
        skip("extended", "node/npx not found")
        return
    tmp = tempfile.mkdtemp(prefix="gm-tw-")
    html = '<div class="bg-teal text-black p-4 md:p-8 rounded border text-h1 bg-slate-500 shadow-lg font-bold">x</div>'
    open(os.path.join(tmp, "index.html"), "w").write(html)
    open(os.path.join(tmp, "in.css"), "w").write("@tailwind base; @tailwind components; @tailwind utilities;")
    shutil.copytree(os.path.join(ROOT, "tokens"), os.path.join(tmp, "tokens"))
    open(os.path.join(tmp, "tailwind.config.cjs"), "w").write("module.exports={presets:[require('./tokens/tailwind.preset.cjs')],content:['./index.html']}")
    r = subprocess.run(["npx", "--yes", "tailwindcss@3.4.17", "-c", "tailwind.config.cjs", "-i", "in.css", "-o", "out.css"], cwd=tmp, capture_output=True, text=True)
    out = open(os.path.join(tmp, "out.css")).read() if os.path.exists(os.path.join(tmp, "out.css")) else ""
    check("extended: Tailwind v3 compiles with the preset; brand classes exist, off-palette and shadow classes do not",
          r.returncode == 0 and "rgb(0 199 197" in out and ".bg-slate-500" not in out and ".shadow-lg" not in out and "border-radius: 4px" in out and "font-size: clamp(" in out,
          (r.stderr or "")[-120:] or "ok")
    tmp4 = tempfile.mkdtemp(prefix="gm-tw4-")
    shutil.copytree(os.path.join(ROOT, "tokens"), os.path.join(tmp4, "tokens"))
    open(os.path.join(tmp4, "index.html"), "w").write(html)
    open(os.path.join(tmp4, "in.css"), "w").write('@import "tailwindcss"; @import "./tokens/tailwind-theme.css"; @source "./index.html";')
    open(os.path.join(tmp4, "package.json"), "w").write("{}")
    subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--silent", "tailwindcss@4.1.4", "@tailwindcss/cli@4.1.4"], cwd=tmp4, capture_output=True, text=True)
    r = subprocess.run(["npx", "--no-install", "@tailwindcss/cli", "-i", "in.css", "-o", "out.css"], cwd=tmp4, capture_output=True, text=True)
    out = open(os.path.join(tmp4, "out.css")).read() if os.path.exists(os.path.join(tmp4, "out.css")) else ""
    check("extended: Tailwind v4 compiles with the theme; teal exists, slate does not",
          r.returncode == 0 and "#00c7c5" in out and ".bg-teal" in out and ".bg-slate-500" not in out, (r.stderr or "")[-160:] or "ok")
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(tmp4, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--extended", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("\n".join(GROUPS))
        return 0
    groups = a.only.split(",") if a.only else [g for g in GROUPS if g != "extended" or a.extended]
    need_browser = any(g in groups for g in ("browser", "geometry", "a11y", "behavior"))
    group_fns = {"files": group_files, "assets": group_assets, "palette": group_palette, "tokens": group_tokens, "css": group_css,
                 "docs": group_docs, "kit": group_kit, "zip": group_zip, "extended": group_extended}
    for g in groups:
        if g in group_fns:
            print(f"--- {g}", flush=True)
            group_fns[g]()
    if need_browser:
        srv, base = start_server()
        br = Browser()
        try:
            for g, fn in (("browser", group_browser), ("geometry", group_geometry), ("a11y", group_a11y), ("behavior", group_behavior)):
                if g in groups:
                    print(f"--- {g}", flush=True)
                    fn(br, base)
        finally:
            br.close()
            srv.shutdown()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    for n, _, d in failed:
        print("FAILED:", n, d)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
