# GEMINII rebrand, pass 1 (colors, logos, typeface): report

Scope: the redesigned "in construction" site (the Astro pages). The legacy page at `/old/` was not edited; at the owner's request it was then deleted (`src/pages/old/` and `public/old/`, 13 files, all unmodified from the baseline commit, so recoverable with `git checkout a6e601f -- src/pages/old public/old`). Nothing is staged or committed.

## Inputs and baseline

- The two input placeholders in the brief were not filled in. Site folder taken as the working directory `/Users/peterp/Projects/Geminii-Robotics` (git repo, commit "copy of ultro.browning.edu website"); brand kit taken as `GEMINII_Brandkit/` inside it. The kit was only read.
- Baseline: git commit `a6e601f021463bdaf409450100d31f9d0c31ea89`. The tracked tree was clean (0 changed files); the only untracked item was `GEMINII_Brandkit/`. Nothing was committed. Baseline data per page at 360 and 1280 px is in `rebrand/baseline/` (rendered text, heading outline, every href/src/srcset/action, form fields, head data, requests, overflow) and screenshots in `rebrand/screenshots/before/`. It was captured from a `git archive` of that commit, built with the site's own build command.
- Toolchain: `deno install` / `deno task build` (the site's own), Chrome 155 through Playwright.

## Counts

| Item | Count |
| --- | --- |
| Files changed | 14: 10 modified (`src/styles/global.css`, `src/components/NavigationBar.astro`, `Footer.astro`, `Welcome.astro`, `src/layouts/BaseLayout.astro`, `src/assets/background.svg`, `public/favicon.ico`, `favicon.svg`, `favicon-96x96.png`, `apple-touch-icon.png`) and 4 added (`public/assets/fonts/Arvo-Regular.woff2`, `Arvo-Bold.woff2`, `OFL.txt`, `public/assets/brand/icon-gradient-on-dark.svg`) |
| Color values replaced | 55: 31 in `global.css` (11 accent-scale values, 20 daisyUI theme values), 20 in `Welcome.astro`, 4 in `background.svg`. Plus 5 Tailwind palette variables overridden (`--color-gray-100..400`, `--color-slate-500`) and 24 rule blocks in the override section at the end of `global.css` (opacity-based colors, role-specific states) |
| Logos swapped | 2 source elements (header, footer) rendering 12 instances across the 6 pages; 4 fixed-path icon files overwritten (`favicon.ico`, `favicon.svg`, `favicon-96x96.png`, `apple-touch-icon.png`) |
| Fonts removed | 4 `@import`s (Metropolis 500 and 800, Space Mono, Atkinson Hyperlegible Next: 3 families), the 3 Tailwind font variables re-pointed to Arvo, 1 stray stack (Inter, in the unused `Welcome.astro`). Font files in the build: 14 (woff and woff2) down to 2 (Arvo Regular and Bold) |

## Pages

Pages (from `src/pages`): `/`, `/about/`, `/ex-nihilo/`, `/outreach/`, `/resources/`, `/robots/`, all rebranded and checked at 360 and 1280 px. (`/old/` existed in the baseline and is deleted; its baseline capture stays in `rebrand/baseline/` as a record.)
Endpoints (200, not rebranded): `/robots.txt`, `/sitemap-index.xml`, `/sitemap-0.xml`.

## How the palette was mapped (by role and surface)

| Original role | Result |
| --- | --- |
| Page surface (the browser's dark canvas, `#121212`) | `html` background set to black |
| Primary accent: Ultro red 500, 600, 700 (button fill, link text) | teal |
| Light tints: red 50 to 400, gray 100 and 200 (text on dark, light card) | white |
| Dark section tints: red 900 and 950 (section fades) | black |
| Red 800 (link hover) | white (hover on black reads as a change from teal) |
| Gray 300 and 400 (hover text on black) | teal |
| daisyUI `base-100` (cards, dropdown menu) | teal surface; text and links on it are black, links keep the underline and thicken on hover |
| `base-200` | black. `base-300` (timeline dividers) | white |
| `primary` | teal with black content. `secondary`, `accent` | white with black content. `neutral` | black with white content |
| Opacity-based colors (`bg-black/20,40,60`, `border-gray-200/30`, `border-b-black/60`, `hover/focus/active:bg-gray-200/30`, button glow) | solid palette colors; the glow became a black shadow |
| Button | teal fill, black text; hover hands the fill to the page surface with white text and a teal border; focus ring white |
| Nav menu button | hover and focus teal with black icon; pressed white |
| Dropdown menu items (on teal) | black text; hover and focus black fill with white text; pressed white fill |
| Keyboard focus ring | teal on black surfaces, black on teal surfaces |
| Photos, partner logos, sponsor logos, the Browning School mark | left unchanged |

Weights: below 600 is 400, 600 and above is 700 (Tailwind `--font-weight-*` variables, plus `.card-title` and `b, strong`). `font-style: normal` everywhere, `font-synthesis: none`. `code, kbd, samp, pre` use `--gm-font-mono` (none of them render on the site).

## Logo decisions

- Header and footer use `icon-gradient-on-dark.svg` (full-color icon, black surface) as an `<img>` with `alt`, `title` and `aria-label` set to "GEMINII". The wordmark was not used because both slots are narrower than 160 px: header slot 148 x 66 px at normal height, footer slot 56 x 56 px. (The home page's expanded header is 361 px wide at the top but shrinks to 148 px on scroll, and one element cannot switch.)
- `width` and `height` attributes fit the icon's aspect ratio (1.055) inside the old box: header 69.9 x 66.3 (old 148.11 x 66.3), footer 56 x 53.1 (old 56 x 56). One CSS rule, `#fullnav > a > img { width: auto }`, keeps the ratio where the layout sets the height.
- Fixed-path files are overwritten at the same path and size from `favicons/`; the 96 px PNG is the kit's `favicon.svg` rasterised by `make_assets.py` (the kit has no 96 px file).
- The kit file in `public/assets/brand/` is byte-identical to the kit. The site's own `@playform/compress` integration minifies SVGs in `dist/`, so the deployed copy differs in bytes but renders identically (pixel-compared in `verify.py`, check e).

## Gradients

| Where | Original | Result | Why |
| --- | --- | --- | --- |
| `src/pages/index.astro:28` (landing, `bg-gradient-to-b from-black to-ultro-red-950`) | black to dark red | black to black (flat black) | Dark-surface depth fade carrying white text. The kit gradients (teal to white or black) would put white text on teal. |
| `src/pages/index.astro:36` (about section, radial 900 to 950) | dark red to darker red | black to black | same |
| `src/pages/ex-nihilo.astro:44` (radial 900 to 950) | dark red to darker red | black to black | same |
| `src/components/Welcome.astro` button (unused component) | `#3245ff` to `#bc52ee` | solid teal, black text | text on a gradient must pass at the worst stop |
| `Welcome.astro` `pre` text gradient (unused) | `#d83333` to `#f041ff` | solid black text | same |
| `Welcome.astro` `code` fill and border gradients (unused) | pinks, red to magenta | solid white fill, black border | |
| `src/assets/background.svg` (unused decoration) | two gradients, blue/purple and red/magenta | both teal to white (the kit ramp endpoints; black text passes on it) | |

`var(--gm-gradient-on-dark)` and `var(--gm-gradient-on-light)` were not needed, so they were not added to the site.

## List only (not edited)

| Page | File | Size | Note |
| --- | --- | --- | --- |
| `/ex-nihilo/` | `src/assets/exnihilologo.png` | 1531 x 479, 34,591 B | Ex Nihilo logo with red baked into the pixels; not an Ultro logo, not a sponsor mark |
| `/ex-nihilo/` | `src/assets/exnihilohero.jpg` | 2048 x 1536, 442,497 B | photo (darkened by a CSS brightness filter, which is luminance only) |
| all rebranded pages (footer) | `src/assets/browning_footer.png` | 1000 x 311, 23,775 B | partner (school) mark, white on transparent |
| `/about/` | `src/assets/sponsors/EdgeChem.png` | 512 x 512, 169,910 B | sponsor logo, color baked in |
| `/about/` | `src/assets/sponsors/MaxBotix.png` | 1200 x 600, 14,362 B | sponsor logo |
| `/about/` | `src/assets/sponsors/SendCutSend.png` | 600 x 220, 17,124 B | sponsor logo |
| `/about/` | `src/assets/sponsors/ServoCity.png` | 2048 x 388, 75,716 B | sponsor logo |
| `/about/` | `src/assets/sponsors/goBILDA.png` | 820 x 351, 22,785 B | sponsor logo |
| (none; imported in `src/pages/index.astro:9`, never rendered) | `src/assets/robotics.webp` | 718 x 623, 225,522 B | meme image, color baked in |
| none | `src/assets/astro.svg` | 2,914 B | Astro's own logo, only in the unused `Welcome.astro` (third party) |

Raster files with the Ultro name or logo baked in (not edited): `src/assets/ultroblack.png` (1018 x 470, 64,659 B, unreferenced), `src/assets/ultrosmall.png` (424 x 424, 30,292 B, unreferenced).
Video, Lottie, 3D models and embeds with colors that cannot be overridden: none. (`src/components/Carousel.astro` is unused and would load 4 stock photos from `img.daisyui.com`.)

## Overflow fixes

Arvo Bold is wider than the face it replaced. One CSS rule in `src/styles/global.css` (`main > section > div > h1 { overflow-wrap: anywhere }`, line 236) stops the page headings spilling out of the viewport. Font sizes are unchanged. Effect: at 360 px the headings ABOUT US, OUTREACH, RESOURCES and ROBOTS break inside a word where needed (the baseline already scrolled sideways at 360 px on all four of those pages); at 1280 px OUTREACH and RESOURCES break inside the word because they are wider than the 576 px column. See open questions.

## Old logo files now unreferenced (left in place)

`src/assets/ultro_dark.svg` (was the header logo), `src/assets/ultro_small_dark.svg` (was the footer logo), `src/assets/ultroblack.png` and `src/assets/ultrosmall.png` (never referenced). The legacy page's `UltroLogo6.png` went with the page.

## Ignored instructions

None. The site source, comments, markup, metadata and config were searched for text addressed to an AI or asking for actions; nothing found.

## Open questions

1. `src/styles/global.css:92-93` `--color-info` / `--color-info-content` mapped to white and black. Info is no longer distinguishable by color. No component uses it today. Decide an icon or text treatment in the later pass.
2. `src/styles/global.css:94-95` `--color-success` / `--color-success-content`: same as above.
3. `src/styles/global.css:96-97` `--color-warning` / `--color-warning-content`: same.
4. `src/styles/global.css:98-99` `--color-error` / `--color-error-content`: same.
5. `src/pages/ex-nihilo.astro:9,27` `exnihilologo.png` keeps its red and its own mark. Decide whether Ex Nihilo gets a kit-compliant logo or stays a separate mark.
6. `src/styles/global.css:236` headings break inside a word (OUTREACH, RESOURCES at 1280 px; most headings at 360 px). Decide a smaller heading size or a wider column in a later pass; sizes were not allowed to change here.
7. `src/components/NavigationBar.astro:58`, `src/components/Footer.astro:12` the icon replaces the old wordmark-style logo because both slots are narrower than 160 px. Decide whether the header should show the wordmark (needs a second element or a wider slot).
8. `README.md:3,13,24` and `astro.config.ts:29`: they still describe and special-case the deleted legacy page (`/old`). Text and config were out of scope for this pass; clean up in the later pass.
9. `src/layouts/BaseLayout.astro:11-20` the head has no `theme-color`, web manifest, canonical or Open Graph tags, so no `og-image`, manifest icons or theme color were set. Adding them needs new elements and text; the kit's `social/` and `favicons/site.webmanifest` are ready for that pass.
10. `package.json:13-15` the three `@fontsource/*` packages are no longer imported. Left in `package.json` and `deno.lock` to keep the lockfile unchanged.
11. `astro.config.ts:26-30` the compress integration minifies SVGs in `dist/`, including the kit's logos (rendering is identical). Decide whether to exclude `dist/assets/brand/` like `dist/old/`.
12. `README.md:36-37` states the images under `public/**` are CC BY-SA 4.0. The GEMINII logos and Arvo (SIL OFL, `public/assets/fonts/OFL.txt`) now live there. Confirm the licensing statement.
13. `GEMINII_Brandkit/` sits inside the site root: Tailwind scans it for class names (the built CSS contains utilities taken from the kit's documentation) and `tsconfig.json:3` includes it. Moving it outside the repo would avoid that; not changed.
14. Unused code recolored but never rendered or verified: `src/components/Welcome.astro`, `src/assets/background.svg`. `src/components/Carousel.astro` has no colors of its own and was left as is.

## verify.py

Last run (`python3 rebrand/verify.py`, full output in `rebrand/verify-output.txt`):

```text
========================================================================
[a] unchanged text / outline / links / fields  PASS
[b] palette                                    PASS
[c] contrast (WCAG AA)                         PASS
[d] fonts                                      PASS
[e] logos and icons                            PASS
[f] health                                     PASS
========================================================================
pages: 6 x widths [360, 1280]; endpoints: 3; 21s; ALL CHECKS PASS
```

What the run covers: 6 pages x 2 widths with default, hover, active and keyboard-focus states for every interactive element, plus mobile menu panels; about 100 to 150 elements and 20 to 45 text runs per page. As a control, running the same script against the untouched original site fails a (16), b (3437), c (113), d (499) and e (34).
