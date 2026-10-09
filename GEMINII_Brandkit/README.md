# GEMINII Brand Kit 1.0

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

```
GEMINII_Brandkit/
├── README.md         This file
├── BRAND.md          The brand rules in text
├── AI_BRIEF.md       Paste-ready brief for AI tools and contractors
├── brand.json        Machine-readable summary: colors, fonts, logos, rules
├── MANIFEST.sha256   Every file with its SHA-256
├── docs/             Implementation docs 01 to 07
├── guidelines/       The 12-page kit: PDF, stacked SVG, pages/ one SVG per page
├── logos/svg/        17 logo SVGs
├── logos/png/        42 PNGs, three sizes each (transparent, except the square avatar)
├── logos/sprite.svg  One-color wordmark, icon, gem as <symbol>s
├── icons/            UI icon sprite and one SVG per icon
├── favicons/         favicon.ico and .svg, Apple touch icon, Android icons, web manifest
├── social/           Open Graph image, LinkedIn, X and YouTube banners, 1080 px profile
├── fonts/            Arvo Regular and Bold: woff2 for the web, ttf for design tools, OFL license
├── tokens/           tokens.css, tokens.json, tokens.scss, Tailwind v3 preset and v4 theme
├── css/              fonts, base, components, and the bundles brand.css and brand.min.css
├── js/               theme-init.js (head), brand.js (theme toggle, menu, tabs)
├── web/starter/      Deployable static site: index.html, styleguide.html, all assets
├── tools/            Build scripts, token source, templates, the kit page generator
└── tests/            verify_package.py and the vendored axe-core
```

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
