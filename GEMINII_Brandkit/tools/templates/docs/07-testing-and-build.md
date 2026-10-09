# Build and tests

## Requirements

Python 3.10+, and `pip install -r tools/requirements.txt` (fonttools, brotli, uharfbuzz, playwright, cairosvg, pypdf, pillow, numpy). Playwright needs a Chromium build: set `PLAYWRIGHT_BROWSERS_PATH` if it is not on the default path. Node is only needed for the extended tests.

## Build

```
python3 tools/build_package.py          # everything
python3 tools/build_package.py --zip    # and ../GEMINII_Brandkit.zip
python3 tools/build_package.py --only tokens,site     # some steps
```

Steps: `kit` (kit pages and logo SVGs from `tools/kit/`), `png`, `favicons`, `social`, `fonts`, `tokens` (token files, CSS bundle, icons), `pdf`, `site` (starter, style guide), `docs`, `meta` (`brand.json`, `MANIFEST.sha256`).

Hand-written and never overwritten: `css/base.css`, `css/components.css`, `css/fonts.css`, `js/`, `tools/templates/`, `tools/tokens.py`, `tools/icons.py`. Everything else is generated.

## Test

```
python3 tests/verify_package.py            # exits non-zero on any failure
python3 tests/verify_package.py --extended # also compiles with Tailwind v3 and v4 (needs node and network)
```

| Group | Checks |
| --- | --- |
| files | Every expected file exists, no stray files, manifest hashes match, zip matches the folder |
| assets | SVGs parse, have no `<text>`, raster or script; PNG sizes and transparency; ICO sizes; manifest icons exist; fonts are woff2 with the right family and weight; license present |
| palette | Only the three colors, the gem neutrals and the gradient interpolations appear in any SVG or CSS |
| tokens | JSON, CSS, SCSS and both Tailwind files agree; type scale equals the kit at 1280 px; contrast ratios in the docs equal the computed ones |
| css | No shadows with blur, no literal colors outside tokens in the component CSS, every `var(--gm-*)` is defined, minified CSS computes identical styles to the readable file |
| docs | Markdown links resolve, every `gm-` class named in the docs exists in the CSS, every token name named exists |
| browser | Starter and style guide at 360, 768, 1280 and 1920 px, light and dark: no console error, no failed request, no sideways scroll, fonts loaded, one `h1`, alt text, no inline style, strict CSP clean |
| geometry | Rendered sizes of buttons, fields, controls, tags, nav and type match the kit numbers |
| accessibility | axe-core, per-element contrast, focus ring on every tab stop, target sizes, reduced motion |
| behavior | Theme toggle and persistence, system theme, mobile menu, Escape, tabs keyboard model |

`tests/vendor/axe.min.js` is axe-core (MPL 2.0), kept so the tests run offline.

The brand kit page generator keeps its own checks: `python3 tools/kit/verify_kit.py` (36 checks on the 12 SVG pages and logo fidelity).

## Change a token

1. Edit `tools/tokens.py`.
2. `python3 tools/build_package.py`.
3. `python3 tests/verify_package.py`.
4. Commit everything, including generated files. `MANIFEST.sha256` shows what changed.

## Versions

{{VERSION}}: first full release. Brand kit pages, assets, tokens, CSS, starter, style guide, docs, tests.
