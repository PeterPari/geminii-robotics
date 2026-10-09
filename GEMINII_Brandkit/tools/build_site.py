"""Website starter, style guide, docs, metadata and zip for the GEMINII brand kit package."""
import hashlib
import html
import json
import os
import re
import shutil
import zipfile

import icons as ICONS
import tokens as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, "templates")
STARTER = os.path.join(ROOT, "web", "starter")


def p(*a):
    return os.path.join(ROOT, *a)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def esc(s):
    return html.escape(s, quote=False)


# ============================================================================ starter copy
def copy_assets(dest):
    """Assets shared by index.html and styleguide.html, at the paths the pages reference."""
    a = os.path.join(dest, "assets")
    for sub in ("css", "js", "fonts", "logos", "icons", "social"):
        shutil.rmtree(os.path.join(a, sub), ignore_errors=True)
    os.makedirs(os.path.join(a, "css"))
    for f in ("brand.css", "brand.min.css"):
        shutil.copy(p("css", f), os.path.join(a, "css", f))
    shutil.copytree(p("js"), os.path.join(a, "js"))
    os.makedirs(os.path.join(a, "fonts"))
    for f in ("Arvo-Regular.woff2", "Arvo-Bold.woff2", "OFL.txt"):
        shutil.copy(p("fonts", f), os.path.join(a, "fonts", f))
    os.makedirs(os.path.join(a, "logos"))
    shutil.copytree(p("logos", "svg"), os.path.join(a, "logos", "svg"))
    shutil.copy(p("logos", "sprite.svg"), os.path.join(a, "logos", "sprite.svg"))
    os.makedirs(os.path.join(a, "logos", "png"))
    for f in ("profile-mark-square-512w.png",):
        shutil.copy(p("logos", "png", f), os.path.join(a, "logos", "png", f))
    os.makedirs(os.path.join(a, "icons"))
    shutil.copy(p("icons", "sprite.svg"), os.path.join(a, "icons", "sprite.svg"))
    os.makedirs(os.path.join(a, "social"))
    shutil.copy(p("social", "og-image.png"), os.path.join(a, "social", "og-image.png"))
    for f in os.listdir(p("favicons")):
        shutil.copy(p("favicons", f), os.path.join(dest, f))


def build_starter():
    os.makedirs(STARTER, exist_ok=True)
    copy_assets(STARTER)
    shutil.copy(os.path.join(TPL, "index.html"), os.path.join(STARTER, "index.html"))
    write(os.path.join(STARTER, "robots.txt"), "User-agent: *\nAllow: /\n")
    shutil.copy(os.path.join(TPL, "styleguide.css"), os.path.join(STARTER, "assets", "css", "styleguide.css"))
    # spacing bars for the style guide
    with open(os.path.join(STARTER, "assets", "css", "styleguide.css"), "a", encoding="utf-8") as f:
        f.write("\n/* ---- spacing bars (generated) */\n")
        for k in T.SPACE:
            f.write(f".sg-space-{k} {{ width: var(--gm-space-{k}); }}\n")
    write(os.path.join(STARTER, "styleguide.html"), styleguide_html())
    write(os.path.join(STARTER, "README.md"), STARTER_README)


STARTER_README = """# GEMINII starter site

Static, no build step, no dependencies. Serve the folder with any static host.

```
python3 -m http.server 8000      # then open http://localhost:8000
```

Open it through a server, not as a file: some browsers block fonts loaded from `file://`.

| File | What |
| --- | --- |
| `index.html` | Page skeleton: head metadata, header, hero, cards, call to action, form, footer. Placeholders are in `[brackets]`. |
| `styleguide.html` | Every token and component, live, in light and dark. Set to `noindex`. Delete before launch if it should not be public. |
| `assets/css/brand.min.css` | Tokens, fonts, base, components in one file. `brand.css` is the readable version. |
| `assets/js/` | `theme-init.js` (load in `<head>`), `brand.js` (theme toggle, mobile menu, tabs). |
| `assets/fonts/` | Arvo Regular and Bold, woff2. |
| `assets/logos/`, `assets/icons/`, `assets/social/` | Logo SVGs, icon sprite, Open Graph image. |
| `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, `icon-*.png`, `site.webmanifest` | Site icons. Keep them in the site root. |

Before launch: replace every `[placeholder]`, replace `https://example.com` in `index.html` with the production origin, and add a `sitemap.xml`.
Full documentation is in the package `docs/` folder.
"""


# ============================================================================ style guide
def snippet(code):
    code = code.strip("\n")
    lines = code.split("\n")
    pad = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    code = "\n".join(l[pad:] for l in lines)
    return (f'<details class="sg-note"><summary>Markup</summary>'
            f'<pre tabindex="0"><code>{esc(code)}</code></pre></details>')


def icon(name, cls="sg-icon"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="assets/icons/sprite.svg#{name}"></use></svg>'


def section(sid, num, total, eyebrow, title, body, surface=""):
    return f"""
    <section class="gm-section {surface}" id="{sid}" aria-labelledby="{sid}-title">
      <div class="gm-container">
        <header class="gm-section-header">
          <div class="gm-section-header__meta">
            <span class="gm-eyebrow">{esc(eyebrow)}</span>
            <span class="gm-counter">{num:02d} / {total:02d}</span>
          </div>
          <span class="gm-rule" aria-hidden="true"></span>
          <h2 id="{sid}-title">{esc(title)}</h2>
        </header>
        {body}
      </div>
    </section>"""


def btn_matrix(prefix):
    states = [("Default", ""), ("Hover", " is-hover"), ("Pressed", " is-pressed"), ("Focus", " is-focus"), ("Disabled", "")]
    head = "".join(f'<th scope="col">{s}</th>' for s, _ in states)
    rows = []
    for kind in ("primary", "secondary", "tertiary"):
        cells = []
        for s, cls in states:
            dis = " disabled" if s == "Disabled" else ""
            cells.append(f'<td><button class="gm-btn gm-btn--{kind}{cls}" type="button"{dis}>Button</button></td>')
        rows.append(f'<tr><th scope="row">{kind.capitalize()}</th>{"".join(cells)}</tr>')
    return (f'<div class="sg-scroll" tabindex="0" role="region" aria-label="{prefix} button states">'
            f'<table class="sg-matrix"><thead><tr><td></td>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def fields_demo(p_):
    err = icon("error", "gm-field__icon")
    return f"""
    <div class="sg-fields">
      <div class="gm-field"><label class="gm-label" for="{p_}-default">Default</label>
        <input class="gm-input" id="{p_}-default" type="text" placeholder="Placeholder"></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-focus">Focus</label>
        <input class="gm-input is-focus" id="{p_}-focus" type="text" placeholder="Placeholder" value="Value"></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-filled">Filled</label>
        <input class="gm-input" id="{p_}-filled" type="text" placeholder="Placeholder" value="Value"></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-disabled">Disabled</label>
        <input class="gm-input" id="{p_}-disabled" type="text" placeholder="Placeholder" disabled></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-error">Error</label>
        <div class="gm-field__control">
          <input class="gm-input" id="{p_}-error" type="text" placeholder="Placeholder" value="Value" aria-invalid="true" aria-describedby="{p_}-error-msg">
          {err}
        </div>
        <p class="gm-field__message" id="{p_}-error-msg">Error message text.</p></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-select">Select</label>
        <div class="gm-select"><select id="{p_}-select"><option>Option one</option><option>Option two</option></select></div></div>
      <div class="gm-field"><label class="gm-label" for="{p_}-textarea">Textarea</label>
        <textarea class="gm-textarea" id="{p_}-textarea" placeholder="Placeholder"></textarea></div>
    </div>"""


def controls_demo(p_):
    return f"""
    <div class="sg-fields">
      <div class="sg-controls">
        <label class="gm-check"><input type="checkbox"><span class="gm-check__box"></span>Checkbox</label>
        <label class="gm-check"><input type="checkbox" checked><span class="gm-check__box"></span>Checkbox checked</label>
        <label class="gm-check"><input type="checkbox" disabled><span class="gm-check__box"></span>Checkbox disabled</label>
        <label class="gm-check"><input type="checkbox" tabindex="-1"><span class="gm-check__box is-focus"></span>Checkbox focus</label>
      </div>
      <div class="sg-controls" role="radiogroup" aria-label="Radio demo {p_}">
        <label class="gm-radio"><input type="radio" name="{p_}-r"><span class="gm-radio__dot"></span>Radio</label>
        <label class="gm-radio"><input type="radio" name="{p_}-r" checked><span class="gm-radio__dot"></span>Radio selected</label>
        <label class="gm-radio"><input type="radio" name="{p_}-rd" disabled><span class="gm-radio__dot"></span>Radio disabled</label>
      </div>
      <div class="sg-controls">
        <label class="gm-switch"><input type="checkbox" role="switch"><span class="gm-switch__track"></span>Switch off</label>
        <label class="gm-switch"><input type="checkbox" role="switch" checked><span class="gm-switch__track"></span>Switch on</label>
        <label class="gm-switch"><input type="checkbox" role="switch" disabled><span class="gm-switch__track"></span>Switch disabled</label>
      </div>
    </div>"""


def surface_block(name, cls, logo, p_):
    return f"""
      <div class="sg-surface {cls}">
        <img src="assets/logos/svg/{logo}" alt="GEMINII" width="190" height="54">
        <h3 class="gm-label-text">{name} surface</h3>
        <p>Body text set in Arvo Regular. <a href="#surfaces">Inline link</a>.</p>
        <div class="gm-cluster">
          <button class="gm-btn gm-btn--primary gm-btn--sm" type="button">Primary</button>
          <button class="gm-btn gm-btn--secondary gm-btn--sm" type="button">Secondary</button>
          <button class="gm-btn gm-btn--tertiary gm-btn--sm" type="button">Tertiary</button>
        </div>
        <div class="gm-field"><label class="gm-label" for="{p_}-f">Label</label>
          <input class="gm-input" id="{p_}-f" type="text" placeholder="Placeholder"></div>
        <label class="gm-check"><input type="checkbox" checked><span class="gm-check__box"></span>Checkbox</label>
      </div>"""


def styleguide_html():
    total = 10
    # ---- 01 logo
    tiles = [
        ("Full color on black", "gm-surface-dark", "wordmark-full-color-on-dark.svg", ""),
        ("Full color on white", "gm-surface-light", "wordmark-full-color-on-light.svg", ""),
        ("One color white, on black only", "gm-surface-dark", "wordmark-white.svg", ""),
        ("One color black, on white", "gm-surface-light", "wordmark-black.svg", ""),
        ("One color black, on teal", "gm-surface-teal", "wordmark-black.svg", ""),
        ("Icon, gradient on black", "gm-surface-dark", "icon-gradient-on-dark.svg", "sg-small"),
        ("Icon, gradient on white", "gm-surface-light", "icon-gradient-on-light.svg", "sg-small"),
        ("Profile mark, square", "gm-surface-light", "profile-mark-square.svg", "sg-small"),
        ("Profile mark, circle", "gm-surface-light", "profile-mark-circle.svg", "sg-small"),
        ("Gem, full color", "gm-surface-dark", "gem-full-color.svg", "sg-small"),
    ]
    tile_html = "".join(
        f'<figure class="sg-tile {cls}"><span class="gm-label-text">{esc(cap)}</span>'
        f'<img class="{small}" src="assets/logos/svg/{f}" alt="GEMINII {esc(cap.lower())}" width="240" height="{68 if "wordmark" in f else 240}"></figure>'
        for cap, cls, f, small in tiles)
    s1 = f"""<div class="sg-tiles">{tile_html}</div>
        <p class="sg-note sg-sub">Clear space is 1X on every side, X = the flat-to-flat width of the gem (about 6.1% of the wordmark width). Minimum size: wordmark 160 px, icon 24 px. Below the minimum, use the icon.</p>"""

    # ---- 02 color
    rows = T.color_table()
    sw = []
    for r in rows:
        sw.append(f"""<div class="sg-swatch sg-swatch--{r['name']}"><h3 class="gm-label-text">{r['role']}: {r['name']}</h3>
          <dl><dt>HEX</dt><dd>{r['hex']}</dd><dt>RGB</dt><dd>{r['rgb'][0]} {r['rgb'][1]} {r['rgb'][2]}</dd>
          <dt>HSL</dt><dd>{r['hsl'][0]} {r['hsl'][1]}% {r['hsl'][2]}%</dd><dt>CMYK</dt><dd>{' '.join(str(x) for x in r['cmyk'])}</dd></dl></div>""")
    pair_rows = []
    for pr in T.pair_table():
        fn = {T.BLACK: "black", T.WHITE: "white", T.TEAL: "teal"}
        fg, bg = fn[pr["fg"]], fn[pr["bg"]]
        ratio = f"{pr['ratio']:.2f}:1".replace(".00:1", ":1")
        fail = pr["level"] == "FAIL"
        demo = f'<span class="sg-pair sg-pair--{fg}-{bg}" aria-hidden="true"{" data-demo-fail" if fail else ""}>Aa</span>'
        pair_rows.append(f'<tr><td>{demo}</td><td>{fg.capitalize()} on {bg}</td><td>{ratio}</td><td>{pr["level"]}'
                         f'{" (do not use for text)" if fail else ""}</td></tr>')
    s2 = f"""<div class="sg-swatches">{''.join(sw)}</div>
        <h3 class="sg-sub">Contrast pairings (WCAG 2.2)</h3>
        <div class="gm-table-wrap" tabindex="0" role="region" aria-label="Contrast pairings">
          <table class="gm-table"><thead><tr><th scope="col">Sample</th><th scope="col">Pair</th><th scope="col">Ratio</th><th scope="col">Level</th></tr></thead>
          <tbody>{''.join(pair_rows)}</tbody></table></div>
        <h3 class="sg-sub">Signature gradient</h3>
        <p class="sg-note">Left to right, teal solid for the first 19%, eased to the far color. Black text is the only text color that passes on the teal to white ramp. Do not set text on the teal to black ramp.</p>
        <div class="gm-stack gm-stack--lg"><div class="sg-grad sg-grad--dark" role="img" aria-label="Gradient, teal to white"></div>
        <div class="sg-grad sg-grad--light" role="img" aria-label="Gradient, teal to black"></div></div>"""

    # ---- 03 type
    cls = {"display": "gm-display", "h1": "gm-h1", "h2": "gm-h2", "h3": "gm-h3", "body-lg": "gm-body-lg", "body": "gm-body", "label": "gm-label-text"}
    sample = {"display": "GEMINII", "h1": "BRAND KIT", "h2": "SECTION TITLE", "h3": "Subsection title",
              "body-lg": "The quick brown fox jumps over the lazy dog.", "body": "The quick brown fox jumps over the lazy dog.",
              "label": "LABEL TEXT"}
    trs = []
    for name, mx, lh, w, up, tr, mn in T.TYPE:
        wname = "Bold" if w == 700 else "Regular"
        spec = f"{wname} {mx} / {lh}" + (f", +{round(tr*100)}% tracking" if tr else "") + (f", fluid from {mn} px" if mn != mx else "")
        tag = "p" if name.startswith("body") or name == "label" else "div"
        trs.append(f'<div class="sg-type-row"><div><span class="gm-label-text">{name}</span><br><small>{spec}</small></div>'
                   f'<{tag} class="{cls[name]}">{sample[name]}</{tag}></div>')
    s3 = f"""<div>{''.join(trs)}</div>
        <h3 class="sg-sub">Specimen</h3>
        <p class="sg-glyphs"><strong>ABCDEFGHIJKLMNOPQRSTUVWXYZ</strong><br>abcdefghijklmnopqrstuvwxyz<br><strong>0123456789 &amp;@#%!?.,:;()/-+=$</strong></p>
        <p class="sg-note">Arvo Regular 400 and Bold 700, SIL Open Font License 1.1. Bold uppercase is primary text, Regular sentence case is secondary text. Emphasis inside body copy is Bold: Arvo italic is not part of the kit.</p>"""

    # ---- 04 layout
    sp = "".join(f'<code>{k}</code><span>{T.rem(px)} / {px} px</span><span class="sg-bar sg-space-{k}"></span>' for k, px in T.SPACE.items())
    bp = "".join(f"<tr><td>{k}</td><td>{px} px</td></tr>" for k, px in T.BREAKPOINT.items())
    s4 = f"""<h3 class="gm-label-text">Spacing, 4 px grid</h3>
        <div class="sg-scale">{sp}</div>
        <h3 class="gm-label-text sg-sub">Radius</h3>
        <div class="sg-row"><span class="sg-radius sg-radius--none"></span><span class="sg-radius sg-radius--sm"></span><span class="sg-radius sg-radius--md"></span><span class="sg-radius sg-radius--pill"></span></div>
        <p class="sg-note">0 (cards), 3 (checkbox), 4 (buttons, fields, notices), pill (tags, switch), circle (avatar, radio).</p>
        <h3 class="gm-label-text sg-sub">Breakpoints</h3>
        <div class="gm-table-wrap" tabindex="0" role="region" aria-label="Breakpoints"><table class="gm-table"><thead><tr><th scope="col">Name</th><th scope="col">Min width</th></tr></thead><tbody>{bp}</tbody></table></div>
        <h3 class="gm-label-text sg-sub">12-column grid, 24 px gutter</h3>
        <div class="gm-grid" aria-hidden="true">{''.join('<div class="sg-colbox gm-span-1"></div>' for _ in range(12))}</div>"""

    # ---- 05 buttons
    s5 = f"""<h3 class="gm-label-text">On light</h3><div class="gm-surface-light sg-stage">{btn_matrix('Light')}</div>
        <h3 class="gm-label-text sg-sub">On dark</h3><div class="gm-surface-dark sg-stage">{btn_matrix('Dark')}</div>
        <h3 class="gm-label-text sg-sub">On teal</h3><div class="gm-surface-teal sg-stage">{btn_matrix('Teal')}</div>
        <p class="sg-note sg-sub">Hover lifts the label and shows a bar. Pressed inverts the colors. Focus is a double ring (ink, then teal). Disabled is a dashed outline in Regular.</p>
        {snippet('<button class="gm-btn gm-btn--primary" type="button">Button</button>' + chr(10) + '<a class="gm-btn gm-btn--secondary" href="/">Link styled as button</a>' + chr(10) + '<button class="gm-btn gm-btn--tertiary gm-btn--sm" type="button" disabled>Disabled</button>')}"""

    # ---- 06 forms
    s6 = f"""<h3 class="gm-label-text">Fields</h3>{fields_demo('sg')}
        {snippet('<div class="gm-field">' + chr(10) + '  <label class="gm-label" for="email">Label</label>' + chr(10) + '  <input class="gm-input" id="email" type="email" placeholder="Placeholder">' + chr(10) + '</div>' + chr(10) + chr(10) + '<!-- error: aria-invalid + icon + message -->' + chr(10) + '<div class="gm-field">' + chr(10) + '  <label class="gm-label" for="e2">Label</label>' + chr(10) + '  <div class="gm-field__control">' + chr(10) + '    <input class="gm-input" id="e2" type="text" placeholder="Placeholder" aria-invalid="true" aria-describedby="e2-msg">' + chr(10) + '    <svg class="gm-field__icon" aria-hidden="true"><use href="assets/icons/sprite.svg#error"></use></svg>' + chr(10) + '  </div>' + chr(10) + '  <p class="gm-field__message" id="e2-msg">Error message text.</p>' + chr(10) + '</div>')}
        <h3 class="gm-label-text sg-sub">Controls</h3>{controls_demo('sg')}
        {snippet('<label class="gm-check"><input type="checkbox"><span class="gm-check__box"></span>Label</label>' + chr(10) + '<label class="gm-radio"><input type="radio" name="g"><span class="gm-radio__dot"></span>Label</label>' + chr(10) + '<label class="gm-switch"><input type="checkbox" role="switch"><span class="gm-switch__track"></span>Label</label>')}"""

    # ---- 07 navigation
    s7 = f"""<h3 class="gm-label-text">Links</h3>
        <p><a href="#navigation">Inline link</a>, <a class="is-hover" href="#navigation">hover state</a>.</p>
        <h3 class="gm-label-text sg-sub">Header</h3>
        <div class="gm-surface-dark sg-stage">
          <header class="gm-nav gm-nav--boxed">
            <div class="gm-nav__inner" style="padding-inline: var(--gm-space-6)">
              <a class="gm-nav__brand" href="#navigation"><img src="assets/logos/svg/wordmark-full-color-on-dark.svg" alt="GEMINII" width="190" height="54"></a>
              <button class="gm-nav__toggle" type="button" data-gm-nav-toggle="sg-menu" aria-expanded="false" aria-controls="sg-menu">{icon('menu', '')}<span class="gm-visually-hidden">Menu</span></button>
              <nav class="gm-nav__menu" id="sg-menu" aria-label="Example">
                <ul class="gm-nav__list">
                  <li><a class="gm-nav__link" href="#navigation" aria-current="page">Item one</a></li>
                  <li><a class="gm-nav__link" href="#navigation">Item two</a></li>
                  <li><a class="gm-nav__link" href="#navigation">Item three</a></li>
                </ul>
                <div class="gm-nav__actions"><a class="gm-btn gm-btn--secondary gm-btn--sm" href="#navigation">Action</a></div>
              </nav>
            </div>
          </header>
        </div>
        <h3 class="gm-label-text sg-sub">Tabs</h3>
        <div data-gm-tabs>
          <div class="gm-tablist" role="tablist" aria-label="Example tabs">
            <button class="gm-tab" role="tab" id="t1" aria-selected="true" aria-controls="p1" type="button">Tab one</button>
            <button class="gm-tab" role="tab" id="t2" aria-selected="false" aria-controls="p2" tabindex="-1" type="button">Tab two</button>
            <button class="gm-tab" role="tab" id="t3" aria-selected="false" aria-controls="p3" tabindex="-1" type="button">Tab three</button>
          </div>
          <div class="gm-tabpanel" role="tabpanel" id="p1" aria-labelledby="t1" tabindex="0"><p>Panel one.</p></div>
          <div class="gm-tabpanel" role="tabpanel" id="p2" aria-labelledby="t2" tabindex="0" hidden><p>Panel two.</p></div>
          <div class="gm-tabpanel" role="tabpanel" id="p3" aria-labelledby="t3" tabindex="0" hidden><p>Panel three.</p></div>
        </div>"""
    s7 = s7.replace('<div class="gm-nav__inner" style="padding-inline: var(--gm-space-6)">', '<div class="gm-nav__inner gm-nav__inner--boxed">')

    # ---- 08 content
    tags = ('<span class="gm-tag">Tag</span> <span class="gm-tag gm-tag--white">Tag</span> '
            '<span class="gm-tag gm-tag--teal">Tag</span> <span class="gm-tag gm-tag--black">Tag</span>')
    av = "".join(f'<span class="gm-avatar {c}"><img src="assets/logos/svg/profile-mark-circle.svg" alt="GEMINII avatar" width="112" height="112"></span>'
                 for c in ("gm-avatar--sm", "", "gm-avatar--lg", "gm-avatar--xl"))
    notices = "".join(
        f'<div class="gm-notice{" gm-notice--error" if n == "error" else ""}" role="{"alert" if n == "error" else "status"}">{icon(n, "gm-notice__icon")}'
        f'<div><p class="gm-notice__title">{t}</p><p>Message text.</p></div></div>'
        for n, t in (("error", "Error"), ("warning", "Warning"), ("success", "Success"), ("info", "Information")))
    s8 = f"""<h3 class="gm-label-text">Cards</h3>
        <div class="gm-cards">
          <article class="gm-card gm-card--white"><h4 class="gm-card__title">Card title</h4><div class="gm-card__body"><p>Body text set in Arvo Regular.</p></div><a class="gm-card__link" href="#content">Link</a></article>
          <article class="gm-card gm-card--teal"><h4 class="gm-card__title">Card title</h4><div class="gm-card__body"><p>Body text set in Arvo Regular.</p></div><a class="gm-card__link" href="#content">Link</a></article>
          <article class="gm-card gm-card--black"><h4 class="gm-card__title">Card title</h4><div class="gm-card__body"><p>Body text set in Arvo Regular.</p></div><a class="gm-card__link" href="#content">Link</a></article>
        </div>
        <h3 class="gm-label-text sg-sub">Tags</h3><div class="sg-row">{tags}</div>
        <h3 class="gm-label-text sg-sub">Avatar</h3><div class="sg-row">{av}</div>
        <h3 class="gm-label-text sg-sub">Notices</h3><div class="gm-stack gm-stack--lg">{notices}</div>
        <p class="sg-note sg-sub">Status is carried by the icon and the heading, never by color.</p>
        <h3 class="gm-label-text sg-sub">Table</h3>
        <div class="gm-table-wrap" tabindex="0" role="region" aria-label="Example table"><table class="gm-table"><thead><tr><th scope="col">Column</th><th scope="col">Column</th><th scope="col">Column</th></tr></thead>
        <tbody><tr><td>Cell</td><td>Cell</td><td>Cell</td></tr><tr><td>Cell</td><td>Cell</td><td>Cell</td></tr></tbody></table></div>
        {snippet('<article class="gm-card gm-card--teal">' + chr(10) + '  <h3 class="gm-card__title">Card title</h3>' + chr(10) + '  <div class="gm-card__body"><p>Text</p></div>' + chr(10) + '  <a class="gm-card__link" href="#">Link</a>' + chr(10) + '</article>' + chr(10) + chr(10) + '<span class="gm-tag gm-tag--teal">Tag</span>')}"""

    # ---- 09 icons
    ic = "".join(f'<div class="sg-icon-cell">{icon(n)}<span>{n}</span></div>' for n in ICONS.NAMES)
    s9 = f"""<div class="sg-icons">{ic}</div>
        <p class="sg-note sg-sub">Line icons (2 px stroke) for actions, solid icons for status. Both inherit <code>currentColor</code>. The error icon is from the kit; the rest are web additions.</p>
        {snippet('<svg aria-hidden="true" focusable="false" width="24" height="24"><use href="assets/icons/sprite.svg#arrow-right"></use></svg>')}"""

    # ---- 10 surfaces
    s10 = f"""<div class="sg-surfaces">
        {surface_block('Light', 'gm-surface-light', 'wordmark-full-color-on-light.svg', 'sl')}
        {surface_block('Dark', 'gm-surface-dark', 'wordmark-full-color-on-dark.svg', 'sd')}
        {surface_block('Teal', 'gm-surface-teal', 'wordmark-black.svg', 'st')}
      </div>
      <p class="sg-note sg-sub">Add <code>gm-surface-light</code>, <code>gm-surface-dark</code> or <code>gm-surface-teal</code> to any section to re-scope the theme. Components inside follow it.</p>"""

    sections = [
        ("logo", "01 Logo", "Logos", s1), ("color", "02 Color", "Color", s2), ("type", "03 Typography", "Typography", s3),
        ("layout", "04 Layout", "Layout", s4), ("buttons", "05 Buttons", "Buttons", s5), ("forms", "06 Forms", "Forms", s6),
        ("navigation", "07 Navigation", "Navigation", s7), ("content", "08 Content", "Content", s8),
        ("icons", "09 Icons", "Icons", s9), ("surfaces", "10 Surfaces", "Surfaces", s10),
    ]
    body = "".join(section(sid, i + 1, total, eb, title, b) for i, (sid, eb, title, b) in enumerate(sections))
    toc = "".join(f'<li><a href="#{sid}">{esc(title)}</a></li>' for sid, _, title, _ in sections)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GEMINII Style Guide</title>
  <meta name="description" content="Tokens and components of the GEMINII brand kit.">
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#000000">
  <meta name="color-scheme" content="light dark">
  <link rel="icon" href="favicon.ico" sizes="48x48">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="preload" href="assets/fonts/Arvo-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/Arvo-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <script src="assets/js/theme-init.js"></script>
  <link rel="stylesheet" href="assets/css/brand.min.css">
  <link rel="stylesheet" href="assets/css/styleguide.css">
</head>
<body>
  <a class="gm-skip-link" href="#main">Skip to content</a>
  <header class="gm-nav">
    <div class="gm-container">
      <div class="gm-nav__inner">
        <a class="gm-nav__brand" href="./">
          <img class="gm-logo--on-dark" src="assets/logos/svg/wordmark-full-color-on-dark.svg" alt="GEMINII" width="190" height="54">
          <img class="gm-logo--on-light" src="assets/logos/svg/wordmark-full-color-on-light.svg" alt="GEMINII" width="190" height="54">
        </a>
        <div class="gm-nav__actions">
          <button class="gm-btn gm-btn--tertiary gm-btn--sm" type="button" data-gm-theme-toggle aria-pressed="false">Dark mode</button>
        </div>
      </div>
    </div>
  </header>
  <main id="main">
    <section class="gm-hero gm-surface-dark" aria-labelledby="sg-title">
      <div class="gm-container">
        <p class="gm-eyebrow">Brand kit 1.0, 2026</p>
        <h1 id="sg-title" class="gm-display">Style guide</h1>
        <p class="gm-body-lg gm-hero__lead">Every token and component, live. Toggle the theme in the header.</p>
        <nav aria-label="Sections"><ul class="sg-toc">{toc}</ul></nav>
      </div>
    </section>
    {body}
  </main>
  <footer class="gm-footer gm-surface-dark">
    <div class="gm-container"><p class="gm-footer__legal">GEMINII Brand Kit 1.0, 2026. Arvo is licensed under the SIL Open Font License 1.1.</p></div>
  </footer>
  <script src="assets/js/brand.js" defer></script>
</body>
</html>
"""


VERSION = "1.0"
SEMVER = "1.0.0"


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def kb(path, gz=False):
    import gzip
    data = open(path, "rb").read()
    if gz:
        data = gzip.compress(data, 9)
    return f"{len(data) / 1024:.1f}"


LOGO_DESC = {
    "wordmark-full-color-on-dark": ("Wordmark, full color", "On black. Primary."),
    "wordmark-full-color-on-light": ("Wordmark, full color", "On white."),
    "wordmark-white": ("Wordmark, one color white", "On black only."),
    "wordmark-black": ("Wordmark, one color black", "On white or teal."),
    "wordmark-currentcolor": ("Wordmark, one color, inherits text color", "Inline use, theming. On black, white or teal."),
    "icon-gradient-on-dark": ("Icon, gradient to white", "On black."),
    "icon-gradient-on-light": ("Icon, gradient to black", "On white."),
    "icon-white": ("Icon, one color white", "On black."),
    "icon-black": ("Icon, one color black", "On white or teal."),
    "icon-teal": ("Icon, teal", "On black. Teal on white fails contrast."),
    "icon-currentcolor": ("Icon, one color, inherits text color", "Inline use, theming."),
    "profile-mark-square": ("Profile mark, square", "Avatars, app icons, favicon source."),
    "profile-mark-circle": ("Profile mark, circle", "Round avatars, `gm-avatar`."),
    "gem-full-color": ("Gem, full artwork", "Small accents, 24 px and up."),
    "gem-white": ("Gem, one color white", "On black."),
    "gem-black": ("Gem, one color black", "On white or teal."),
    "gem-currentcolor": ("Gem, one color, inherits text color", "Inline use."),
}


def tree_block():
    def n(*parts, ext=None):
        d = p(*parts)
        return len([f for f in os.listdir(d) if (ext is None or f.endswith(ext)) and os.path.isfile(os.path.join(d, f))])
    lines = [
        ("README.md", "This file"),
        ("BRAND.md", "The brand rules in text"),
        ("AI_BRIEF.md", "Paste-ready brief for AI tools and contractors"),
        ("brand.json", "Machine-readable summary: colors, fonts, logos, rules"),
        ("MANIFEST.sha256", "Every file with its SHA-256"),
        ("docs/", "Implementation docs 01 to 07"),
        ("guidelines/", "The 12-page kit: PDF, stacked SVG, `pages/` one SVG per page"),
        ("logos/svg/", f"{n('logos', 'svg')} logo SVGs"),
        ("logos/png/", f"{n('logos', 'png')} PNGs, three sizes each (transparent, except the square avatar)"),
        ("logos/sprite.svg", "One-color wordmark, icon, gem as `<symbol>`s"),
        ("icons/", "UI icon sprite and one SVG per icon"),
        ("favicons/", "favicon.ico and .svg, Apple touch icon, Android icons, web manifest"),
        ("social/", "Open Graph image, LinkedIn, X and YouTube banners, 1080 px profile"),
        ("fonts/", "Arvo Regular and Bold: woff2 for the web, ttf for design tools, OFL license"),
        ("tokens/", "tokens.css, tokens.json, tokens.scss, Tailwind v3 preset and v4 theme"),
        ("css/", "fonts, base, components, and the bundles brand.css and brand.min.css"),
        ("js/", "theme-init.js (head), brand.js (theme toggle, menu, tabs)"),
        ("web/starter/", "Deployable static site: index.html, styleguide.html, all assets"),
        ("tools/", "Build scripts, token source, templates, the kit page generator"),
        ("tests/", "verify_package.py and the vendored axe-core"),
    ]
    w = max(len(a) for a, _ in lines)
    body = "\n".join(f"{('├── ' if i < len(lines) - 1 else '└── ')}{a.ljust(w)}  {b}" for i, (a, b) in enumerate(lines))
    return "```\nGEMINII_Brandkit/\n" + body.replace("`", "") + "\n```"


def doc_blocks():
    import build_package as BP  # noqa: F401  (constants only)
    from PIL import Image
    B = {}
    B["VERSION"] = VERSION
    B["X_PERCENT"] = f"{T.K.GEM_W / T.K.LOGO_W * 100:.1f}"
    B["TREE"] = tree_block()
    B["FAMILY"] = ", ".join(T.FAMILY)
    B["VP_MIN"], B["VP_MAX"] = T.VP_MIN, T.VP_MAX
    for k, key in (("LABEL", "label"), ("BUTTON", "button"), ("NAV", "nav"), ("TAG", "tag"), ("CHROME", "chrome")):
        B["TR_" + k] = f"{T.TRACKING[key]:g}"
    B["ICON_IDS"] = ", ".join(f"`{n}`" for n in ICONS.NAMES)

    rows = [(f"{r['role']}", f"`{r['name']}`", f"`{r['hex']}`", " ".join(map(str, r["rgb"])),
             f"{r['hsl'][0]} {r['hsl'][1]}% {r['hsl'][2]}%", " ".join(map(str, r["cmyk"]))) for r in T.color_table()]
    B["COLOR_TABLE"] = md_table(["Role", "Name", "HEX", "RGB", "HSL", "CMYK"], rows)

    nm = {T.BLACK: "black", T.WHITE: "white", T.TEAL: "teal"}
    prow = []
    for pr in T.pair_table():
        r = f"{pr['ratio']:.2f}:1".replace(".00:1", ":1")
        prow.append((f"{nm[pr['fg']]} on {nm[pr['bg']]}", r, pr["level"]))
    B["CONTRAST_TABLE"] = md_table(["Pair", "Ratio", "Level"], prow)

    trows = []
    for name, mx, lh, w, up, tr, mn in T.TYPE:
        trows.append((name, "Bold 700" if w == 700 else "Regular 400", f"{mx} / {lh}", mn, "uppercase" if up else "sentence case",
                      f"+{round(tr * 100)}%" if tr else "none"))
    B["TYPE_TABLE"] = md_table(["Style", "Weight", "Size / line (px)", "Min size (px)", "Case", "Tracking"], trows)
    tt = T.type_tokens()
    B["TYPE_TOKEN_TABLE"] = md_table(
        ["Token prefix", "Size (fluid)", "Line height", "Weight"],
        [(f"`--gm-text-{k}-`", f"`{d['size']}`", d["line_height"], d["weight"]) for k, d in tt.items()])

    B["SPACE_TABLE"] = md_table(["Token", "rem", "px"], [(f"`--gm-space-{k}`", T.rem(px), px) for k, px in T.SPACE.items()])
    desc = {"none": "Cards", "sm": "Checkbox", "md": "Buttons, fields, notices, chips in cards", "pill": "Tags, switch"}
    B["RADIUS_TABLE"] = md_table(["Token", "Value", "Used by"], [(f"`--gm-radius-{k}`", f"{px}px", desc[k]) for k, px in T.RADIUS.items()])
    bdesc = {"hairline": "Divider rules", "base": "Default: buttons, fields, cards, controls", "heavy": "Table header rule",
             "strong": "Error edge, hover underline", "accent": "Teal accent bar height"}
    B["BORDER_TABLE"] = md_table(["Token", "Value", "Used by"], [(f"`--gm-border-{k}`", f"{px}px", bdesc[k]) for k, px in T.BORDER.items()])
    B["BREAKPOINT_TABLE"] = md_table(["Token", "Min width"], [(f"`--gm-bp-{k}`", f"{px}px") for k, px in T.BREAKPOINT.items()])
    B["LAYOUT_TABLE"] = md_table(["Token", "Value", "Note"], [
        ("`--gm-content-max`", f"{T.LAYOUT['content_max']}px", "Kit canvas 1920 minus 2 x 96"),
        ("`--gm-margin`", "16px, 32px, 48px", "Container side padding; steps at 640 and 960 px"),
        ("`--gm-gutter`", f"{T.LAYOUT['gutter']}px", "Grid gap"),
        ("`--gm-measure`", T.LAYOUT["measure"], "Max line length for prose"),
        ("columns", T.LAYOUT["columns"], "`gm-grid`")])
    B["MOTION_TABLE"] = md_table(["Token", "Value"], [(f"`--gm-duration-{k}`", f"{ms}ms") for k, ms in T.DURATION.items()] + [("`--gm-ease`", f"`{T.EASING}`")])
    B["Z_TABLE"] = md_table(["Token", "Value"], [(f"`--gm-z-{k}`", z) for k, z in T.Z.items()])
    cdesc = {
        "button_height": "Button height", "button_height_sm": "Small button height", "button_pad_x": "Button side padding",
        "button_bar": "Hover bar thickness", "field_height": "Field height", "field_pad_x": "Field side padding",
        "control_size": "Checkbox and radio box", "switch_w": "Switch width", "switch_h": "Switch height", "switch_knob": "Switch knob",
        "tag_height": "Tag height", "tag_pad_x": "Tag side padding", "nav_height": "Header height from 960 px",
        "nav_height_mobile": "Header height below 960 px", "rule_w": "Accent bar width", "rule_h": "Accent bar height",
        "ring_gap": "Focus ring gap", "ring_ink": "Focus ink ring", "ring_teal": "Focus teal ring", "ring_teal_offset": "Teal ring offset from the edge",
        "avatar_sizes": "Avatar sizes",
    }
    crow = [(k.replace("_", "-"), desc_, (", ".join(f"{x}px" for x in v) if isinstance(v, list) else f"{v}px"))
            for k, v in T.COMPONENT.items() for desc_ in [cdesc[k]]]
    B["COMPONENT_TABLE"] = md_table(["Name", "What", "Value"], crow)

    th = {t: T.theme_vars(t) for t in T.THEMES}
    names = [k for k in th["light"] if k.startswith("--gm-") and "-btn-" not in k and "gradient" not in k]
    B["THEME_TABLE"] = md_table(["Variable", "Light", "Dark", "Teal"],
                               [(f"`{k}`", *[f"`{th[t][k]}`" for t in ("light", "dark", "teal")]) for k in names])
    brow = []
    for t in ("light", "dark"):
        for kind, (base, pressed, bar) in T.BTN[t].items():
            brow.append((t, kind, "/".join(base), "/".join(pressed), bar))
    B["BUTTON_TABLE"] = md_table(["Theme", "Kind", "Default bg / text / border", "Pressed bg / text / border", "Hover bar"],
                                [(a, b, f"`{c}`", f"`{d}`", f"`{e}`") for a, b, c, d, e in brow]) + "\n\nThe teal surface uses the light set."
    B["GRADIENT_STOPS"] = "`" + ", ".join(f"{c} {p:g}%" for p, c in T.gradient_stops(T.WHITE)[::4]) + "`, every fourth of 49 stops"

    lrows = []
    for fn in sorted(os.listdir(p("logos", "svg"))):
        base = fn[:-4]
        what, use = LOGO_DESC[base]
        lrows.append((f"`{fn}`", what, use))
    B["LOGO_FILE_TABLE"] = md_table(["File", "What", "Use"], lrows)
    prow = {}
    for fn in sorted(os.listdir(p("logos", "png"))):
        m = re.match(r"(.+)-(\d+)w\.png$", fn)
        im = Image.open(p("logos", "png", fn))
        prow.setdefault(m.group(1), []).append(f"{im.width} x {im.height}")
    B["PNG_TABLE"] = md_table(["File prefix", "Sizes (px)"], [(f"`{k}-<w>w.png`", ", ".join(v)) for k, v in prow.items()])
    fdesc = {
        "favicon.ico": "Legacy and default. 16, 32, 48 px in one file.", "favicon.svg": "Modern browsers. Profile mark, scales to any size.",
        "apple-touch-icon.png": "iOS home screen. Opaque, no rounding (iOS rounds it).", "icon-192.png": "Android and manifest.",
        "icon-512.png": "Manifest, splash.", "icon-maskable-512.png": "Manifest `purpose: maskable`. Glyph inside the 80% safe zone.",
        "site.webmanifest": "Name, colors, icons.",
    }
    frow = []
    for fn in sorted(os.listdir(p("favicons"))):
        if fn.endswith(".png"):
            im = Image.open(p("favicons", fn)); size = f"{im.width} x {im.height}"
        elif fn.endswith(".ico"):
            size = "16, 32, 48"
        else:
            size = "vector" if fn.endswith(".svg") else "text"
        frow.append((f"`{fn}`", size, fdesc[fn]))
    B["FAVICON_TABLE"] = md_table(["File", "Size (px)", "Use"], frow)
    sdesc = {"og-image.png": "Open Graph and X large card. Default share image.", "linkedin-banner-1584x396.png": "LinkedIn profile banner.",
             "x-header-1500x500.png": "X profile header.", "youtube-banner-2560x1440.png": "YouTube channel banner. Safe area is the center 1546 x 423.",
             "profile-1080.png": "Instagram and other square avatars. The platform crops the circle."}
    srow = []
    for fn in sorted(os.listdir(p("social"))):
        im = Image.open(p("social", fn))
        srow.append((f"`{fn}`", f"{im.width} x {im.height}", sdesc[fn]))
    B["SOCIAL_TABLE"] = md_table(["File", "Size (px)", "Use"], srow)
    fam = {n: ("line" if n in ICONS.LINE else "status") for n in ICONS.NAMES}
    B["ICON_TABLE"] = md_table(["Id", "Family", "Name"], [(f"`{n}`", fam[n], ICONS.LABELS[n]) for n in ICONS.NAMES])

    B["FONT_KB"] = f"{(os.path.getsize(p('fonts', 'Arvo-Regular.woff2')) + os.path.getsize(p('fonts', 'Arvo-Bold.woff2'))) / 1024:.1f}"
    B["CSS_MIN_KB"] = kb(p("css", "brand.min.css"))
    B["CSS_GZ_KB"] = kb(p("css", "brand.min.css"), gz=True)
    B["JS_KB"] = f"{(os.path.getsize(p('js', 'brand.js')) + os.path.getsize(p('js', 'theme-init.js'))) / 1024:.1f}"
    B["THEME_INIT_BYTES"] = str(os.path.getsize(p("js", "theme-init.js")))
    B["WORDMARK_KB"] = kb(p("logos", "svg", "wordmark-full-color-on-dark.svg"))
    B["SPRITE_KB"] = kb(p("icons", "sprite.svg"))
    return B


def fill(text, blocks):
    def rep(m):
        k = m.group(1)
        if k not in blocks:
            raise KeyError(f"doc placeholder {k} has no value")
        return str(blocks[k])
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", rep, text)


def build_docs():
    B = doc_blocks()
    for name in ("README.md", "BRAND.md", "AI_BRIEF.md"):
        write(p(name), fill(read(os.path.join(TPL, name)), B))
    os.makedirs(p("docs"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(TPL, "docs"))):
        write(p("docs", f), fill(read(os.path.join(TPL, "docs", f)), B))


def file_hashes():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if d not in ("__pycache__", "node_modules", ".pytest_cache"))
        for f in sorted(fn):
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, ROOT)
            if rel in ("MANIFEST.sha256",) or f.endswith(".pyc") or rel.startswith("tests/.report"):
                continue
            out.append((rel, hashlib.sha256(open(full, "rb").read()).hexdigest()))
    return out


def build_meta():
    from tokens import K
    brand = {
        "name": "GEMINII", "version": SEMVER, "year": 2026,
        "colors": {k: {"hex": v, "role": r} for (k, v), r in zip(T.COLORS.items(), ("primary", "secondary", "tertiary"))},
        "contrast": [{"fg": pr["fg"], "bg": pr["bg"], "ratio": round(pr["ratio"], 2), "wcag": pr["level"]} for pr in T.pair_table()],
        "typeface": {"family": "Arvo", "weights": T.WEIGHTS, "designer": "Anton Koovit", "license": "SIL OFL 1.1",
                     "files": ["fonts/Arvo-Regular.woff2", "fonts/Arvo-Bold.woff2"], "fallback": T.FAMILY},
        "typeScale": {k: {"maxPx": mx, "linePx": lh, "weight": w, "uppercase": up, "tracking": tr, "minPx": mn}
                      for k, mx, lh, w, up, tr, mn in T.TYPE},
        "logo": {
            "clearSpace": "1X, X = gem flat-to-flat width", "clearSpaceRatioOfWordmarkWidth": round(K.GEM_W / K.LOGO_W, 4),
            "aspectRatio": round(K.LOGO_W / K.LOGO_H, 4),
            "minWidth": {"wordmark": {"px": 160, "mm": 40}, "icon": {"px": 24, "mm": 8}},
            "files": {"svg": "logos/svg/", "png": "logos/png/", "sprite": "logos/sprite.svg"},
            "versions": {"fullColorOnBlack": "wordmark-full-color-on-dark.svg", "fullColorOnWhite": "wordmark-full-color-on-light.svg",
                         "oneColorWhiteOnBlack": "wordmark-white.svg", "oneColorBlackOnWhiteOrTeal": "wordmark-black.svg"},
        },
        "surfaces": ["light", "dark", "teal"],
        "radius": T.RADIUS, "borderPx": T.BORDER, "breakpointsPx": T.BREAKPOINT,
        "files": {"tokensCss": "tokens/tokens.css", "tokensJson": "tokens/tokens.json", "bundle": "css/brand.min.css",
                  "starter": "web/starter/", "styleGuide": "web/starter/styleguide.html", "brief": "AI_BRIEF.md"},
        "rules": [
            "Exactly three colors: black, teal, white. No tints or shades.",
            "Teal text works on black only. White on teal and teal on white fail contrast.",
            "Arvo Regular and Bold only. Bold uppercase is primary, Regular sentence case is secondary.",
            "Flat interface: no shadows, 2 px borders, 4 px radius on buttons and fields, square cards.",
            "Focus is a double ring. Disabled is dashed. Status is an icon plus a heading, never color alone.",
            "Logo: never stretch, rotate, outline, recolor, crop or move the gem. Keep 1X clear space.",
        ],
    }
    write(p("brand.json"), json.dumps(brand, indent=2) + "\n")
    write(p("MANIFEST.sha256"), "".join(f"{h}  {rel}\n" for rel, h in file_hashes()))


def make_zip():
    out = os.path.join(os.path.dirname(ROOT), "GEMINII_Brandkit.zip")
    if os.path.exists(out):
        os.remove(out)
    base = os.path.basename(ROOT)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, dn, fn in os.walk(ROOT):
            dn[:] = sorted(d for d in dn if d not in ("__pycache__", "node_modules", ".pytest_cache"))
            for f in sorted(fn):
                if f.endswith(".pyc"):
                    continue
                full = os.path.join(dp, f)
                z.write(full, os.path.join(base, os.path.relpath(full, ROOT)))
    return out
