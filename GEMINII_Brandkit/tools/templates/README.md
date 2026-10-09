# GEMINII Brand Kit {{VERSION}}

Logos, favicons, social images, fonts, design tokens, CSS components, a static starter site, a live style guide and the rules in Markdown. Black, teal `#00C7C5`, white. Arvo.

## Start here

| If you are | Open |
| --- | --- |
| Building the website | `web/starter/` (copy it), then `docs/04-website-guide.md` |
| Using Tailwind | `tokens/tailwind.preset.cjs` (v3) or `tokens/tailwind-theme.css` (v4) |
| Designing | `guidelines/GEMINII_Brandkit.pdf`, `logos/svg/`, `fonts/*.ttf` |
| Briefing an AI tool or a contractor | `AI_BRIEF.md`, `BRAND.md` |
| Looking up a value | `docs/02-tokens.md`, `tokens/tokens.json` |
| Checking what is not decided yet | `docs/06-open-items.md` |

## Folder map

{{TREE}}

## Quick start: the starter site

```
cd web/starter
python3 -m http.server 8000
```

Open `http://localhost:8000` for the page skeleton and `http://localhost:8000/styleguide.html` for every token and component, live, light and dark. Use a server, not `file://`: some browsers block fonts loaded from files.

## Quick start: your own project

1. Copy `css/brand.min.css`, `fonts/Arvo-*.woff2`, `js/theme-init.js`, `js/brand.js`, `icons/sprite.svg` and the logos you use. Keep `css/` and `fonts/` as siblings, or edit the two `url()` paths in `css/fonts.css`.
2. Paste the head block from `docs/04-website-guide.md`.
3. Add a class to a section to choose its surface: `gm-surface-light`, `gm-surface-dark`, `gm-surface-teal`.
4. Build with the `gm-` classes in `docs/03-components.md`, or with Tailwind and the preset.

## Rebuild and test

```
pip install -r tools/requirements.txt
python3 tools/build_package.py        # regenerates every generated file
python3 tests/verify_package.py       # exits non-zero on any failure
```

`tools/tokens.py` is the single source for every token file. Edit it, rebuild, never edit generated files. Generated files carry a header saying so. `MANIFEST.sha256` lists every file with its hash.

## Licenses

Arvo: SIL Open Font License 1.1, in `fonts/OFL.txt`. Everything else is GEMINII brand material; usage rights are the owner's to set.
