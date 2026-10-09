"""GEMINII design tokens: single source of truth.

Everything in tokens/ (JSON, CSS, SCSS, Tailwind) is generated from the data in this file.
Colors, type scale, radii, borders and component geometry come from the brand kit pages.
Entries marked WEB are additions made for the website layer; the kit does not define them.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kit"))
import kitlib as K  # noqa: E402

BLACK, TEAL, WHITE = K.BLACK, K.TEAL, K.WHITE
COLORS = {"black": BLACK, "teal": TEAL, "white": WHITE}

# ------------------------------------------------------------------ typography
FAMILY = ['"Arvo"', '"Rockwell"', '"Roboto Slab"', "Georgia", "serif"]            # WEB: fallback stack
MONO = ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"]        # WEB: code only, the kit defines no mono face
WEIGHTS = {"regular": 400, "bold": 700}
VP_MIN, VP_MAX = 360, 1280                                                       # WEB: fluid range (px)
# name, max px, line-height px (at max), weight, uppercase, tracking em, min px on small screens
TYPE = [
    ("display", 120, 120, 700, True, 0.0, 48),
    ("h1", 72, 80, 700, True, 0.0, 36),
    ("h2", 48, 56, 700, True, 0.0, 28),
    ("h3", 32, 40, 700, False, 0.0, 24),
    ("body-lg", 24, 36, 400, False, 0.0, 20),
    ("body", 18, 28, 400, False, 0.0, 18),
    ("label", 14, 20, 700, True, 0.14, 14),
]
TRACKING = {"label": 0.14, "button": 0.12, "nav": 0.12, "tag": 0.14, "chrome": 0.14}


def rem(px):
    v = px / 16
    return f"{v:g}rem"


def fluid(mx, mn):
    """CSS length that is mn px at VP_MIN and mx px at VP_MAX, clamped, in rem."""
    if mx == mn:
        return rem(mx)
    slope = (mx - mn) / (VP_MAX - VP_MIN)
    base = mn - slope * VP_MIN
    return f"clamp({rem(mn)}, calc({rem(base)} + {slope * 100:.4f}vw), {rem(mx)})"


def type_tokens():
    out = {}
    for name, mx, lh, w, up, tr, mn in TYPE:
        out[name] = {
            "size": fluid(mx, mn), "size_max_px": mx, "size_min_px": mn,
            "line_height": round(lh / mx, 4), "line_height_px": lh,
            "weight": w, "uppercase": up, "tracking": tr,
        }
    return out


# ------------------------------------------------------------------ scales
SPACE = {1: 4, 2: 8, 3: 12, 4: 16, 5: 20, 6: 24, 8: 32, 10: 40, 12: 48, 16: 64, 24: 96, 32: 128}   # WEB: 4 px grid
RADIUS = {"none": 0, "sm": 3, "md": 4, "pill": 9999}                                  # sm checkbox, md button + field (kit)
BORDER = {"hairline": 1, "base": 2, "heavy": 3, "strong": 4, "accent": 6}            # kit stroke widths
BREAKPOINT = {"sm": 640, "md": 960, "lg": 1280, "xl": 1920}                          # WEB
LAYOUT = {"content_max": 1728, "measure": "68ch", "gutter": 24, "margin_sm": 16, "margin_md": 32, "margin_lg": 48,
          "columns": 12}                                                              # content_max: kit 1920 canvas minus 2 x 96
DURATION = {"fast": 120, "base": 200}                                                 # WEB
EASING = "cubic-bezier(0.2, 0, 0, 1)"                                                 # WEB
Z = {"base": 0, "sticky": 100, "overlay": 200, "modal": 300, "toast": 400}            # WEB

# ------------------------------------------------------------------ component geometry (kit pages 11 and 12)
COMPONENT = {
    "button_height": 56, "button_height_sm": 52, "button_pad_x": 32, "button_bar": 6,
    "field_height": 56, "field_pad_x": 18,
    "control_size": 26, "switch_w": 56, "switch_h": 32, "switch_knob": 18,
    "tag_height": 38, "tag_pad_x": 20,
    "nav_height": 92, "nav_height_mobile": 72,
    "rule_w": 72, "rule_h": 6,
    "ring_gap": 3, "ring_ink": 2, "ring_teal": 3, "ring_teal_offset": 7.5,
    "avatar_sizes": [32, 48, 64, 112],
}

# ------------------------------------------------------------------ themes
BTN = {
    "light": {
        "primary": ((BLACK, WHITE, BLACK), (TEAL, BLACK, BLACK), TEAL),
        "secondary": ((TEAL, BLACK, BLACK), (BLACK, TEAL, BLACK), BLACK),
        "tertiary": ((WHITE, BLACK, BLACK), (BLACK, WHITE, BLACK), TEAL),
    },
    "dark": {
        "primary": ((WHITE, BLACK, WHITE), (TEAL, BLACK, TEAL), TEAL),
        "secondary": ((TEAL, BLACK, TEAL), (BLACK, TEAL, TEAL), BLACK),
        "tertiary": ((BLACK, WHITE, WHITE), (WHITE, BLACK, WHITE), TEAL),
    },
}
BTN["teal"] = BTN["light"]

THEMES = {
    "light": {"bg": WHITE, "fg": BLACK, "ring_gap": WHITE, "knob_off": BLACK, "switch_on_edge": BLACK, "accent_line": TEAL, "focus_outer": TEAL,
              "edge": {"white": BLACK, "teal": BLACK, "black": BLACK}, "gradient": "on-light"},
    "dark": {"bg": BLACK, "fg": WHITE, "ring_gap": BLACK, "knob_off": WHITE, "switch_on_edge": TEAL, "accent_line": TEAL, "focus_outer": TEAL,
             "edge": {"white": WHITE, "teal": TEAL, "black": WHITE}, "gradient": "on-dark"},
    "teal": {"bg": TEAL, "fg": BLACK, "ring_gap": TEAL, "knob_off": BLACK, "switch_on_edge": BLACK, "accent_line": BLACK, "focus_outer": BLACK,
             "edge": {"white": BLACK, "teal": BLACK, "black": BLACK}, "gradient": "on-light"},
}


def gradient_stops(far, steps=48):
    """Signature gradient: left to right, from teal to `far`, sampled from the original ramp."""
    return [(round(100 * k / steps, 3), K.ramp_color(k / steps, far)) for k in range(steps + 1)]


def gradient_css(far):
    return "linear-gradient(to right, " + ", ".join(f"{c} {p:g}%" for p, c in gradient_stops(far)) + ")"


# ------------------------------------------------------------------ derived
def rgb(h):
    return K.hex_to_rgb(h)


def color_table():
    rows = []
    for name, role in (("black", "Primary"), ("teal", "Secondary"), ("white", "Tertiary")):
        h = COLORS[name]
        rows.append({"name": name, "role": role, "hex": h.upper(), "rgb": rgb(h), "hsl": K.to_hsl(h), "cmyk": K.to_cmyk(h)})
    return rows


def pair_table():
    out = []
    for fg, bg in ((BLACK, WHITE), (WHITE, BLACK), (BLACK, TEAL), (TEAL, BLACK), (WHITE, TEAL), (TEAL, WHITE)):
        r = K.contrast(fg, bg)
        out.append({"fg": fg, "bg": bg, "ratio": r, "level": K.wcag_level(r)})
    return out


def theme_vars(theme, edge=True):
    t = THEMES[theme]
    v = {
        "color-scheme": "dark" if theme == "dark" else "light",
        "--gm-bg": t["bg"], "--gm-fg": t["fg"], "--gm-accent": TEAL, "--gm-on-accent": BLACK,
        "--gm-accent-line": t["accent_line"], "--gm-focus-outer": t["focus_outer"],
        "--gm-ring-gap": t["ring_gap"], "--gm-knob-off": t["knob_off"], "--gm-switch-on-edge": t["switch_on_edge"],
        "--gm-gradient": f"var(--gm-gradient-{t['gradient']})",
        "--gm-logo-on-dark-display": "inline-block" if theme == "dark" else "none",
        "--gm-logo-on-light-display": "inline-block" if theme == "light" else "none",
        "--gm-logo-on-teal-display": "inline-block" if theme == "teal" else "none",
    }
    if edge:
        for k, c in t["edge"].items():
            v[f"--gm-edge-{k}"] = c
    for kind, (base, pressed, bar) in BTN[theme].items():
        for suffix, trio in (("", base), ("-pressed", pressed)):
            v[f"--gm-btn-{kind}{suffix}-bg"] = trio[0]
            v[f"--gm-btn-{kind}{suffix}-fg"] = trio[1]
            v[f"--gm-btn-{kind}{suffix}-border"] = trio[2]
        v[f"--gm-btn-{kind}-bar"] = bar
    return v


def decl_block(vars_, indent="  "):
    return "\n".join(f"{indent}{k}: {val};" for k, val in vars_.items())


# ------------------------------------------------------------------ emitters
def primitives_vars():
    v = {"--gm-black": BLACK, "--gm-teal": TEAL, "--gm-white": WHITE,
         "--gm-gradient-on-dark": gradient_css(WHITE), "--gm-gradient-on-light": gradient_css(BLACK),
         "--gm-font-family": ", ".join(FAMILY),
         "--gm-font-mono": ", ".join(MONO),
         "--gm-weight-regular": WEIGHTS["regular"], "--gm-weight-bold": WEIGHTS["bold"]}
    for name, d in type_tokens().items():
        v[f"--gm-text-{name}-size"] = d["size"]
        v[f"--gm-text-{name}-line"] = d["line_height"]
        v[f"--gm-text-{name}-weight"] = d["weight"]
        v[f"--gm-text-{name}-tracking"] = f"{d['tracking']:g}em"
    for k, val in TRACKING.items():
        v[f"--gm-tracking-{k}"] = f"{val:g}em"
    for k, px in SPACE.items():
        v[f"--gm-space-{k}"] = rem(px)
    for k, px in RADIUS.items():
        v[f"--gm-radius-{k}"] = f"{px}px"
    for k, px in BORDER.items():
        v[f"--gm-border-{k}"] = f"{px}px"
    for k, px in BREAKPOINT.items():
        v[f"--gm-bp-{k}"] = f"{px}px"
    v["--gm-content-max"] = f"{LAYOUT['content_max']}px"
    v["--gm-measure"] = LAYOUT["measure"]
    v["--gm-gutter"] = f"{LAYOUT['gutter']}px"
    v["--gm-margin"] = f"{LAYOUT['margin_sm']}px"
    for k, ms in DURATION.items():
        v[f"--gm-duration-{k}"] = f"{ms}ms"
    v["--gm-ease"] = EASING
    for k, z in Z.items():
        v[f"--gm-z-{k}"] = z
    c = COMPONENT
    v.update({
        "--gm-button-height": f"{c['button_height']}px", "--gm-button-height-sm": f"{c['button_height_sm']}px",
        "--gm-button-pad-x": f"{c['button_pad_x']}px", "--gm-button-bar": f"{c['button_bar']}px",
        "--gm-field-height": f"{c['field_height']}px", "--gm-field-pad-x": f"{c['field_pad_x']}px",
        "--gm-control-size": f"{c['control_size']}px",
        "--gm-switch-w": f"{c['switch_w']}px", "--gm-switch-h": f"{c['switch_h']}px", "--gm-switch-knob": f"{c['switch_knob']}px",
        "--gm-tag-height": f"{c['tag_height']}px", "--gm-tag-pad-x": f"{c['tag_pad_x']}px",
        "--gm-nav-height": f"{c['nav_height_mobile']}px",
        "--gm-rule-w": f"{c['rule_w']}px", "--gm-rule-h": f"{c['rule_h']}px",
        "--gm-ring-gap-w": f"{c['ring_gap']}px", "--gm-ring-ink-w": f"{c['ring_ink']}px",
        "--gm-ring-teal-w": f"{c['ring_teal']}px", "--gm-ring-teal-offset": f"{c['ring_teal_offset']}px",
    })
    return v


def tokens_css():
    prim = primitives_vars()
    light, dark, teal = theme_vars("light"), theme_vars("dark"), theme_vars("teal")
    light_v, dark_v, teal_v = theme_vars("light", False), theme_vars("dark", False), theme_vars("teal", False)
    out = ["/* GEMINII design tokens. Generated by tools/build_package.py from tools/tokens.py. Do not edit by hand. */",
           ":root {", decl_block(prim), "}", "",
           f"@media (min-width: {BREAKPOINT['sm']}px) {{\n  :root {{ --gm-margin: {LAYOUT['margin_md']}px; }}\n}}",
           f"@media (min-width: {BREAKPOINT['md']}px) {{\n  :root {{ --gm-margin: {LAYOUT['margin_lg']}px; --gm-nav-height: {COMPONENT['nav_height']}px; }}\n}}", "",
           "/* Page and section themes. No data-theme attribute on <html> follows the system setting. */",
           ':root,\n[data-theme="light"],\n.gm-surface-light {', decl_block(light), "}", "",
           '[data-theme="dark"],\n.gm-surface-dark {', decl_block(dark), "}", "",
           "@media (prefers-color-scheme: dark) {", ":root:not([data-theme]) {", decl_block(dark, "    "), "  }", "}", "",
           ".gm-surface-teal {", decl_block(teal), "}", "",
           "/* Card and tag variants re-scope the theme but keep the edge colors of the surface they sit on. */",
           ".gm-card--white,\n.gm-tag--white {", decl_block(light_v), "}", "",
           ".gm-card--black,\n.gm-tag--black {", decl_block(dark_v), "}", "",
           ".gm-card--teal,\n.gm-tag--teal {", decl_block(teal_v), "}", ""]
    return "\n".join(out)


def tokens_scss():
    prim = primitives_vars()
    lines = ["// GEMINII design tokens. Generated by tools/build_package.py from tools/tokens.py. Do not edit by hand."]
    for k, val in prim.items():
        if k.startswith("--gm-gradient"):
            continue
        lines.append(f"${k[2:]}: {val};")
    lines.append("")
    lines.append("$gm-gradient-on-dark: " + gradient_css(WHITE) + ";")
    lines.append("$gm-gradient-on-light: " + gradient_css(BLACK) + ";")
    return "\n".join(lines) + "\n"


def dtcg():
    def tok(t, v, d=None):
        o = {"$type": t, "$value": v}
        if d:
            o["$description"] = d
        return o

    tt = type_tokens()
    j = {
        "$description": "GEMINII design tokens (W3C Design Tokens Community Group format). Generated. Do not edit by hand.",
        "color": {
            "black": tok("color", BLACK, "Primary"),
            "teal": tok("color", TEAL, "Secondary"),
            "white": tok("color", WHITE, "Tertiary"),
        },
        "gradient": {
            "on-dark": tok("gradient", [{"color": c, "position": p / 100} for p, c in gradient_stops(WHITE)], "Teal to white, left to right"),
            "on-light": tok("gradient", [{"color": c, "position": p / 100} for p, c in gradient_stops(BLACK)], "Teal to black, left to right"),
        },
        "font": {
            "family": {"base": tok("fontFamily", [f.strip('"') for f in FAMILY])},
            "weight": {k: tok("fontWeight", v) for k, v in WEIGHTS.items()},
        },
        "typography": {
            name: {"$type": "typography", "$value": {
                "fontFamily": "{font.family.base}", "fontWeight": d["weight"], "fontSize": f"{d['size_max_px']}px",
                "lineHeight": d["line_height"], "letterSpacing": f"{d['tracking']:g}em",
            }, "$extensions": {"gm.brand": {"uppercase": d["uppercase"], "minSizePx": d["size_min_px"], "fluid": d["size"]}}}
            for name, d in tt.items()
        },
        "tracking": {k: tok("dimension", f"{v:g}em") for k, v in TRACKING.items()},
        "space": {str(k): tok("dimension", f"{px}px") for k, px in SPACE.items()},
        "radius": {k: tok("dimension", f"{px}px") for k, px in RADIUS.items()},
        "border": {k: tok("dimension", f"{px}px") for k, px in BORDER.items()},
        "breakpoint": {k: tok("dimension", f"{px}px") for k, px in BREAKPOINT.items()},
        "layout": {
            "contentMax": tok("dimension", f"{LAYOUT['content_max']}px"), "measure": tok("dimension", LAYOUT["measure"]),
            "gutter": tok("dimension", f"{LAYOUT['gutter']}px"), "columns": tok("number", LAYOUT["columns"]),
        },
        "duration": {k: tok("duration", f"{ms}ms") for k, ms in DURATION.items()},
        "easing": {"base": tok("cubicBezier", [0.2, 0, 0, 1])},
        "zIndex": {k: tok("number", z) for k, z in Z.items()},
        "component": {k: tok("dimension" if not isinstance(v, list) else "other", f"{v}px" if not isinstance(v, list) else v)
                      for k, v in COMPONENT.items()},
        "theme": {},
    }
    for th in THEMES:
        j["theme"][th] = {k.replace("--gm-", ""): tok("color", v) if str(v).startswith("#") else tok("other", v)
                          for k, v in theme_vars(th).items() if k.startswith("--gm-") and not k.startswith("--gm-gradient")}
    return j


def tailwind_preset():
    tt = type_tokens()
    fs = {}
    for name, d in tt.items():
        key = name
        opts = {"lineHeight": str(d["line_height"]), "fontWeight": str(d["weight"])}
        if d["tracking"]:
            opts["letterSpacing"] = f"{d['tracking']:g}em"
        fs[key] = [d["size"], opts]
    cfg = {
        "colors": {"transparent": "transparent", "current": "currentColor", **COLORS,
                   "bg": "var(--gm-bg)", "fg": "var(--gm-fg)"},
        "fontFamily": {"sans": [f.strip('"') for f in FAMILY], "arvo": [f.strip('"') for f in FAMILY]},
        "fontWeight": {k: str(v) for k, v in WEIGHTS.items()},
        "fontSize": fs,
        "spacing": {"0": "0px", "px": "1px", **{str(k): rem(px) for k, px in SPACE.items()}},
        "borderRadius": {"none": "0px", "sm": f"{RADIUS['sm']}px", "DEFAULT": f"{RADIUS['md']}px", "md": f"{RADIUS['md']}px", "full": "9999px"},
        "borderWidth": {"DEFAULT": f"{BORDER['base']}px", "0": "0px", **{k: f"{px}px" for k, px in BORDER.items()}},
        "screens": {k: f"{px}px" for k, px in BREAKPOINT.items()},
        "boxShadow": {"none": "none"},
        "maxWidth": {"content": f"{LAYOUT['content_max']}px", "measure": LAYOUT["measure"], "none": "none", "full": "100%"},
        "backgroundImage": {"signature-on-dark": "var(--gm-gradient-on-dark)", "signature-on-light": "var(--gm-gradient-on-light)"},
        "transitionDuration": {"DEFAULT": f"{DURATION['base']}ms", **{k: f"{ms}ms" for k, ms in DURATION.items()}},
        "transitionTimingFunction": {"DEFAULT": EASING},
        "zIndex": {k: str(z) for k, z in Z.items()},
    }
    js = ("/* GEMINII Tailwind v3 preset. Generated by tools/build_package.py. Do not edit by hand.\n"
          " * Usage: module.exports = { presets: [require('./tokens/tailwind.preset.cjs')], content: [...] }\n"
          " * Replaces Tailwind's default palette with the three brand colors. Import css/brand.css for themes and components. */\n"
          "module.exports = {\n  theme: " + json.dumps(cfg, indent=2).replace("\n", "\n  ") + ",\n  corePlugins: { container: false },\n};\n")
    return js


def tailwind_v4_theme():
    tt = type_tokens()
    L = ["/* GEMINII Tailwind v4 theme. Generated by tools/build_package.py. Do not edit by hand.",
         " * Usage: @import \"tailwindcss\"; @import \"./tokens/tailwind-theme.css\"; @import \"./css/brand.css\"; */",
         "@theme {",
         "  --color-*: initial;",
         f"  --color-black: {BLACK};", f"  --color-teal: {TEAL};", f"  --color-white: {WHITE};",
         "  --color-bg: var(--gm-bg);", "  --color-fg: var(--gm-fg);",
         "  --font-*: initial;", f"  --font-sans: {', '.join(FAMILY)};",
         "  --radius-*: initial;"]
    for k, px in RADIUS.items():
        L.append(f"  --radius-{k}: {px}px;")
    L.append("  --breakpoint-*: initial;")
    for k, px in BREAKPOINT.items():
        L.append(f"  --breakpoint-{k}: {px}px;")
    L.append("  --text-*: initial;")
    for name, d in tt.items():
        L.append(f"  --text-{name}: {d['size']};")
        L.append(f"  --text-{name}--line-height: {d['line_height']};")
        L.append(f"  --text-{name}--font-weight: {d['weight']};")
        if d["tracking"]:
            L.append(f"  --text-{name}--letter-spacing: {d['tracking']:g}em;")
    L.append("  --shadow-*: initial;")
    L.append("  --spacing: 0.25rem;")
    L.append(f"  --ease-brand: {EASING};")
    L.append("}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    print(tokens_css()[:1500])
