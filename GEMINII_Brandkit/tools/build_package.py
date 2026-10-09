#!/usr/bin/env python3
"""Build the GEMINII brand kit package.

    python3 tools/build_package.py            # regenerates every generated file in the package
    python3 tools/build_package.py --zip      # ... and writes ../GEMINII_Brandkit.zip

Generated: guidelines/, logos/, icons/, favicons/, social/, fonts/*.woff2, tokens/, css/tokens.css, css/brand*.css,
web/starter/, docs tables, brand.json, MANIFEST.sha256.
Hand-written (never overwritten): css/base.css, css/components.css, css/fonts.css, js/, tools/templates/.
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "kit"))

import icons as ICONS  # noqa: E402
import tokens as T  # noqa: E402

TMP = tempfile.mkdtemp(prefix="gm-kit-")
os.environ["GEMINII_KIT_DIST"] = TMP
import build as KITBUILD  # noqa: E402  (kit page generator)
import kitlib as K  # noqa: E402

BLACK, TEAL, WHITE = K.BLACK, K.TEAL, K.WHITE


def p(*parts):
    return os.path.join(ROOT, *parts)


def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def clean(*dirs):
    for d in dirs:
        full = p(d)
        if os.path.isdir(full):
            shutil.rmtree(full)
        os.makedirs(full, exist_ok=True)


# ============================================================================ 1. kit pages + logo SVGs
LOGO_SVGS = [
    "wordmark-full-color-on-dark", "wordmark-full-color-on-light", "wordmark-white", "wordmark-black",
    "icon-gradient-on-dark", "icon-gradient-on-light", "icon-white", "icon-black", "icon-teal",
    "profile-mark-square", "profile-mark-circle", "gem-full-color", "gem-white", "gem-black",
]


def step_kit():
    clean("guidelines", "logos")
    os.makedirs(p("logos", "svg"), exist_ok=True)
    KITBUILD.build()
    shutil.copytree(os.path.join(TMP, "pages"), p("guidelines", "pages"))
    shutil.copy(os.path.join(TMP, "GEMINII_Brandkit.svg"), p("guidelines", "GEMINII_Brandkit.svg"))
    for n in LOGO_SVGS:
        shutil.copy(os.path.join(TMP, "logos", n + ".svg"), p("logos", "svg", n + ".svg"))

    # currentColor variants for inline use and theming (single-color artwork only)
    for src, dst in (("wordmark-white", "wordmark-currentcolor"), ("icon-white", "icon-currentcolor"), ("gem-white", "gem-currentcolor")):
        s = read(p("logos", "svg", src + ".svg"))
        s = s.replace("#ffffff", "currentColor")
        s = re.sub(r'\swidth="\d+"\sheight="\d+"', "", s, count=1)
        s = s.replace(f'aria-label="{src.replace("-", " ")}"', f'aria-label="GEMINII {dst.split("-")[0]}"')
        s = re.sub(r"<title>[^<]*</title>", f"<title>GEMINII {dst.split('-')[0]}</title>", s)
        write(p("logos", "svg", dst + ".svg"), s)

    # sprite: <svg class="logo"><use href="logos/sprite.svg#wordmark"/></svg>
    syms = []
    for src, sid in (("wordmark-currentcolor", "wordmark"), ("icon-currentcolor", "icon"), ("gem-currentcolor", "gem")):
        s = read(p("logos", "svg", src + ".svg"))
        vb = re.search(r'viewBox="([^"]+)"', s).group(1)
        inner = re.sub(r"^<svg[^>]*>|</svg>$", "", s.strip())
        inner = re.sub(r"<title>[^<]*</title>", "", inner)
        syms.append(f'<symbol id="{sid}" viewBox="{vb}">{inner}</symbol>')
    write(p("logos", "sprite.svg"), '<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' + "".join(syms) + "</svg>\n")


# ============================================================================ 2. rasterization
def viewbox_ratio(svg_text):
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg_text).group(1).split()]
    return vb[3] / vb[2]


class Raster:
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(args=["--allow-file-access-from-files"])
        return self

    def __exit__(self, *a):
        self.browser.close()
        self.pw.stop()

    def svg_to_png(self, svg_path, out_path, width, height=None, bg=None):
        s = read(svg_path)
        height = height or max(1, round(width * viewbox_ratio(s)))
        page = self.browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        css = f"background:{bg}" if bg else "background:transparent"
        html = (f'<!doctype html><meta charset=utf-8><style>html,body{{margin:0;{css}}}img{{display:block;width:{width}px;height:{height}px}}</style>'
                f'<img src="file://{svg_path}">')
        tmp = os.path.join(TMP, "r.html")
        write(tmp, html)
        page.goto("file://" + tmp)
        page.wait_for_function("document.images[0].complete && document.images[0].naturalWidth > 0")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        page.screenshot(path=out_path, omit_background=bg is None, clip={"x": 0, "y": 0, "width": width, "height": height})
        page.close()

    def html_to_png(self, html, out_path, width, height):
        page = self.browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        tmp = os.path.join(TMP, "h.html")
        write(tmp, html)
        page.goto("file://" + tmp)
        page.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        page.screenshot(path=out_path, clip={"x": 0, "y": 0, "width": width, "height": height})
        page.close()


PNG_WIDTHS = {"wordmark": (480, 960, 1920), "icon": (128, 512, 1024), "profile": (128, 512, 1024), "gem": (128, 512, 1024)}


def step_png(r):
    for n in LOGO_SVGS:
        kind = n.split("-")[0]
        for w in PNG_WIDTHS[kind]:
            r.svg_to_png(p("logos", "svg", n + ".svg"), p("logos", "png", f"{n}-{w}w.png"), w)


# ============================================================================ 3. favicons + app icons
def maskable_svg():
    """Profile mark with the glyph shrunk so its corners sit inside the 80% maskable safe circle."""
    gb = K.GLYPH_BOX
    half_diag = (((gb[2] - gb[0]) / 2) ** 2 + ((gb[3] - gb[1]) / 2) ** 2) ** 0.5
    k = 0.4 * 1500 / half_diag
    gcx, gcy = (gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2
    pg = K.Page("m")
    glyph = K.glyph_group(pg, WHITE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500">'
            f'<rect width="1500" height="1500" fill="{TEAL}"/>'
            f'<g transform="translate({K.n(750 - gcx * k)} {K.n(750 - gcy * k)}) scale({k:.6f})">{glyph}</g></svg>')


def step_favicons(r):
    from PIL import Image
    clean("favicons")
    sq = p("logos", "svg", "profile-mark-square.svg")
    shutil.copy(sq, p("favicons", "favicon.svg"))
    write(os.path.join(TMP, "maskable.svg"), maskable_svg())
    sizes = {"favicon-16.png": 16, "favicon-32.png": 32, "favicon-48.png": 48, "apple-touch-icon.png": 180,
             "icon-192.png": 192, "icon-512.png": 512}
    for name, s in sizes.items():
        r.svg_to_png(sq, p("favicons", name), s, s, bg=TEAL)
    r.svg_to_png(os.path.join(TMP, "maskable.svg"), p("favicons", "icon-maskable-512.png"), 512, 512, bg=TEAL)
    imgs = [Image.open(p("favicons", f"favicon-{s}.png")).convert("RGBA") for s in (16, 32, 48)]
    imgs[2].save(p("favicons", "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
    for s in (16, 32, 48):
        os.remove(p("favicons", f"favicon-{s}.png"))
    manifest = {
        "name": "GEMINII", "short_name": "GEMINII", "start_url": "./", "display": "standalone",
        "background_color": BLACK, "theme_color": BLACK,
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    write(p("favicons", "site.webmanifest"), json.dumps(manifest, indent=2) + "\n")


# ============================================================================ 4. social images
SOCIAL = [  # file, width, height, wordmark width
    ("og-image.png", 1200, 630, 640),
    ("linkedin-banner-1584x396.png", 1584, 396, 560),
    ("x-header-1500x500.png", 1500, 500, 600),
    ("youtube-banner-2560x1440.png", 2560, 1440, 900),
]


def step_social(r):
    clean("social")
    wm = p("logos", "svg", "wordmark-full-color-on-dark.svg")
    for name, w, h, lw in SOCIAL:
        html = (f'<!doctype html><meta charset=utf-8><style>html,body{{margin:0;background:{BLACK}}}'
                f'body{{width:{w}px;height:{h}px;display:grid;place-items:center}}img{{width:{lw}px;height:auto;display:block}}</style>'
                f'<img src="file://{wm}">')
        r.html_to_png(html, p("social", name), w, h)
    r.svg_to_png(p("logos", "svg", "profile-mark-square.svg"), p("social", "profile-1080.png"), 1080, 1080, bg=TEAL)


# ============================================================================ 5. fonts
def step_fonts():
    from fontTools.ttLib import TTFont
    clean("fonts")
    for style in ("Regular", "Bold"):
        src = os.path.join(HERE, "kit", "fonts", f"Arvo-{style}.ttf")
        shutil.copy(src, p("fonts", f"Arvo-{style}.ttf"))
        f = TTFont(src)
        f.flavor = "woff2"
        f.save(p("fonts", f"Arvo-{style}.woff2"))
    shutil.copy(os.path.join(HERE, "kit", "fonts", "OFL-LICENSE.txt"), p("fonts", "OFL.txt"))


# ============================================================================ 6. tokens + css bundle + icons
def minify_css(css):
    """Small, string-safe CSS minifier (no restructuring). Equivalence is tested in a browser."""
    out, i, n = [], 0, len(css)
    while i < n:
        c = css[i]
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "\"'":
            j = i + 1
            while j < n and css[j] != c:
                j += 2 if css[j] == "\\" else 1
            out.append(css[i:j + 1])
            i = j + 1
            continue
        out.append(c)
        i += 1
    s = "".join(out)
    # protect strings while collapsing whitespace
    parts = re.split(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', s)
    for k in range(0, len(parts), 2):
        t = re.sub(r"\s+", " ", parts[k])
        t = re.sub(r"\s*([{};,>~])\s*", r"\1", t)
        t = re.sub(r";}", "}", t)
        parts[k] = t
    return "".join(parts).strip() + "\n"


def step_tokens():
    clean("tokens", "icons")
    write(p("tokens", "tokens.json"), json.dumps(T.dtcg(), indent=2) + "\n")
    write(p("tokens", "tokens.scss"), T.tokens_scss())
    write(p("tokens", "tailwind.preset.cjs"), T.tailwind_preset())
    write(p("tokens", "tailwind-theme.css"), T.tailwind_v4_theme())
    write(p("tokens", "tokens.css"), T.tokens_css())
    bundle = "\n".join(read(p("tokens", f) if f == "tokens.css" else p("css", f)) for f in ("tokens.css", "fonts.css", "base.css", "components.css"))
    write(p("css", "brand.css"), bundle)
    write(p("css", "brand.min.css"), minify_css(bundle))
    os.makedirs(p("icons", "svg"), exist_ok=True)
    for n in ICONS.NAMES:
        write(p("icons", "svg", n + ".svg"), ICONS.single(n))
    write(p("icons", "sprite.svg"), ICONS.sprite())


# ============================================================================ 7. guidelines PDF
PAGE_TITLES = ["Cover", "Contents", "Logo suite", "Wordmark", "Color versions", "Misuse", "Palette",
               "Contrast and gradient", "Typeface", "Type scale", "UI components, light", "UI components, dark"]


def step_pdf():
    import cairosvg
    from pypdf import PdfWriter, PdfReader
    pages = sorted(f for f in os.listdir(p("guidelines", "pages")) if f.endswith(".svg"))
    w = PdfWriter()
    for i, f in enumerate(pages):
        buf = io.BytesIO()
        cairosvg.svg2pdf(url=p("guidelines", "pages", f), write_to=buf)
        buf.seek(0)
        w.append(PdfReader(buf))
        w.add_outline_item(PAGE_TITLES[i], i)
    w.add_metadata({"/Title": "GEMINII Brand Kit", "/Author": "GEMINII", "/Subject": "Brand kit, version 1.0, 2026"})
    with open(p("guidelines", "GEMINII_Brandkit.pdf"), "wb") as fh:
        w.write(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--only", help="comma list of steps")
    a = ap.parse_args()
    steps = (a.only or "kit,png,favicons,social,fonts,tokens,pdf,site,docs,meta").split(",")
    import build_site  # noqa: E402
    with Raster() as r:
        if "kit" in steps: step_kit(); print("kit")
        if "png" in steps: step_png(r); print("png")
        if "favicons" in steps: step_favicons(r); print("favicons")
        if "social" in steps: step_social(r); print("social")
    if "fonts" in steps: step_fonts(); print("fonts")
    if "tokens" in steps: step_tokens(); print("tokens")
    if "pdf" in steps: step_pdf(); print("pdf")
    if "site" in steps: build_site.build_starter(); print("site")
    if "docs" in steps: build_site.build_docs(); print("docs")
    if "meta" in steps: build_site.build_meta(); print("meta")
    if a.zip:
        build_site.make_zip(); print("zip")
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
