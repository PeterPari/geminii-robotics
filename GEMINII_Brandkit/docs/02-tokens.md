# Tokens

One source: `tools/tokens.py`. Generated outputs: `tokens/tokens.css`, `tokens/tokens.json`, `tokens/tokens.scss`, `tokens/tailwind.preset.cjs`, `tokens/tailwind-theme.css`. Rebuild with `python3 tools/build_package.py`.

Section headings marked (kit) hold values that are on a brand kit page. Headings marked (web) hold values added for the website layer; the kit does not define them.

## Formats

| Format | File | Use |
| --- | --- | --- |
| CSS variables | `tokens/tokens.css` | Any stack. Prefix `--gm-`. |
| W3C design tokens | `tokens/tokens.json` | Style Dictionary, Tokens Studio for Figma, other pipelines. |
| SCSS variables | `tokens/tokens.scss` | Sass projects. `$gm-...`, same names as the CSS variables. |
| Tailwind v3 preset | `tokens/tailwind.preset.cjs` | `presets: [require('./tokens/tailwind.preset.cjs')]`. Replaces the default palette with the three colors. |
| Tailwind v4 theme | `tokens/tailwind-theme.css` | `@import "tailwindcss"; @import "./tokens/tailwind-theme.css";` |

## Color

| Role | Name | HEX | RGB | HSL | CMYK |
| --- | --- | --- | --- | --- | --- |
| Primary | `black` | `#000000` | 0 0 0 | 0 0% 0% | 0 0 0 100 |
| Secondary | `teal` | `#00C7C5` | 0 199 197 | 179 100% 39% | 100 0 1 22 |
| Tertiary | `white` | `#FFFFFF` | 255 255 255 | 0 0% 100% | 0 0 0 0 |

CSS: `--gm-black`, `--gm-teal`, `--gm-white`. Tailwind: `black`, `teal`, `white`, plus `bg` and `fg` that follow the theme.

### Semantic variables

These change with the theme or surface. Use them in components so one rule works on black, white and teal.

| Variable | Light | Dark | Teal |
| --- | --- | --- | --- |
| `--gm-bg` | `#ffffff` | `#000000` | `#00c7c5` |
| `--gm-fg` | `#000000` | `#ffffff` | `#000000` |
| `--gm-accent` | `#00c7c5` | `#00c7c5` | `#00c7c5` |
| `--gm-on-accent` | `#000000` | `#000000` | `#000000` |
| `--gm-accent-line` | `#00c7c5` | `#00c7c5` | `#000000` |
| `--gm-focus-outer` | `#00c7c5` | `#00c7c5` | `#000000` |
| `--gm-ring-gap` | `#ffffff` | `#000000` | `#00c7c5` |
| `--gm-knob-off` | `#000000` | `#ffffff` | `#000000` |
| `--gm-switch-on-edge` | `#000000` | `#00c7c5` | `#000000` |
| `--gm-logo-on-dark-display` | `none` | `inline-block` | `none` |
| `--gm-logo-on-light-display` | `inline-block` | `none` | `none` |
| `--gm-logo-on-teal-display` | `none` | `none` | `inline-block` |
| `--gm-edge-white` | `#000000` | `#ffffff` | `#000000` |
| `--gm-edge-teal` | `#000000` | `#00c7c5` | `#000000` |
| `--gm-edge-black` | `#000000` | `#ffffff` | `#000000` |

Button colors per theme (`--gm-btn-<kind>-bg`, `-fg`, `-border`, `-pressed-bg`, `-pressed-fg`, `-pressed-border`, `-bar`):

| Theme | Kind | Default bg / text / border | Pressed bg / text / border | Hover bar |
| --- | --- | --- | --- | --- |
| light | primary | `#000000/#ffffff/#000000` | `#00c7c5/#000000/#000000` | `#00c7c5` |
| light | secondary | `#00c7c5/#000000/#000000` | `#000000/#00c7c5/#000000` | `#000000` |
| light | tertiary | `#ffffff/#000000/#000000` | `#000000/#ffffff/#000000` | `#00c7c5` |
| dark | primary | `#ffffff/#000000/#ffffff` | `#00c7c5/#000000/#00c7c5` | `#00c7c5` |
| dark | secondary | `#00c7c5/#000000/#00c7c5` | `#000000/#00c7c5/#00c7c5` | `#000000` |
| dark | tertiary | `#000000/#ffffff/#ffffff` | `#ffffff/#000000/#ffffff` | `#00c7c5` |

The teal surface uses the light set.

### Gradient

`--gm-gradient-on-dark` (teal to white) and `--gm-gradient-on-light` (teal to black), left to right, 49 stops sampled from the original ramp of the logo. `--gm-gradient` picks the one for the current surface. Stops of the dark version:

`#00c7c5 0%, #00c7c5 8.333%, #00c7c5 16.667%, #07c8c7 25%, #15ccca 33.333%, #42d5d4 41.667%, #7ae2e1 50%, #9eeae9 58.333%, #c1f1f1 66.667%, #e3f9f9 75%, #eefbfb 83.333%, #f7fdfd 91.667%, #ffffff 100%`, every fourth of 49 stops

## Typography

Family: `--gm-font-family` = `"Arvo", "Rockwell", "Roboto Slab", Georgia, serif`. Weights: `--gm-weight-regular` 400, `--gm-weight-bold` 700. Code only: `--gm-font-mono` (web, the kit has no mono face).

| Token prefix | Size (fluid) | Line height | Weight |
| --- | --- | --- | --- |
| `--gm-text-display-` | `clamp(3rem, calc(1.23913rem + 7.8261vw), 7.5rem)` | 1.0 | 700 |
| `--gm-text-h1-` | `clamp(2.25rem, calc(1.36957rem + 3.9130vw), 4.5rem)` | 1.1111 | 700 |
| `--gm-text-h2-` | `clamp(1.75rem, calc(1.26087rem + 2.1739vw), 3rem)` | 1.1667 | 700 |
| `--gm-text-h3-` | `clamp(1.5rem, calc(1.30435rem + 0.8696vw), 2rem)` | 1.25 | 700 |
| `--gm-text-body-lg-` | `clamp(1.25rem, calc(1.15217rem + 0.4348vw), 1.5rem)` | 1.5 | 400 |
| `--gm-text-body-` | `1.125rem` | 1.5556 | 400 |
| `--gm-text-label-` | `0.875rem` | 1.4286 | 700 |

Sizes are fluid between a 360 px and a 1280 px viewport (web). At 1280 px and wider they equal the kit scale. Sizes are in `rem` so the browser's font-size setting is respected. Tracking tokens: `--gm-tracking-label` 0.14em, `--gm-tracking-button` 0.12em, `--gm-tracking-nav` 0.12em, `--gm-tracking-tag` 0.14em, `--gm-tracking-chrome` 0.14em.

## Spacing (web)

4 px grid. Subset of Tailwind's default scale, so `p-4` is 1rem in both.

| Token | rem | px |
| --- | --- | --- |
| `--gm-space-1` | 0.25rem | 4 |
| `--gm-space-2` | 0.5rem | 8 |
| `--gm-space-3` | 0.75rem | 12 |
| `--gm-space-4` | 1rem | 16 |
| `--gm-space-5` | 1.25rem | 20 |
| `--gm-space-6` | 1.5rem | 24 |
| `--gm-space-8` | 2rem | 32 |
| `--gm-space-10` | 2.5rem | 40 |
| `--gm-space-12` | 3rem | 48 |
| `--gm-space-16` | 4rem | 64 |
| `--gm-space-24` | 6rem | 96 |
| `--gm-space-32` | 8rem | 128 |

## Radius (kit)

| Token | Value | Used by |
| --- | --- | --- |
| `--gm-radius-none` | 0px | Cards |
| `--gm-radius-sm` | 3px | Checkbox |
| `--gm-radius-md` | 4px | Buttons, fields, notices, chips in cards |
| `--gm-radius-pill` | 9999px | Tags, switch |

## Border width (kit)

| Token | Value | Used by |
| --- | --- | --- |
| `--gm-border-hairline` | 1px | Divider rules |
| `--gm-border-base` | 2px | Default: buttons, fields, cards, controls |
| `--gm-border-heavy` | 3px | Table header rule |
| `--gm-border-strong` | 4px | Error edge, hover underline |
| `--gm-border-accent` | 6px | Teal accent bar height |

## Breakpoints (web)

Mobile first, `min-width`.

| Token | Min width |
| --- | --- |
| `--gm-bp-sm` | 640px |
| `--gm-bp-md` | 960px |
| `--gm-bp-lg` | 1280px |
| `--gm-bp-xl` | 1920px |

## Layout

| Token | Value | Note |
| --- | --- | --- |
| `--gm-content-max` | 1728px | Kit canvas 1920 minus 2 x 96 |
| `--gm-margin` | 16px, 32px, 48px | Container side padding; steps at 640 and 960 px |
| `--gm-gutter` | 24px | Grid gap |
| `--gm-measure` | 68ch | Max line length for prose |
| columns | 12 | `gm-grid` |

`--gm-margin` is 16 px, 32 px from `sm`, 48 px from `md`. The container is `--gm-content-max` wide plus the margins, centered. On the kit's 1920 px canvas that gives 96 px side margins, as on the kit pages.

## Motion (web)

| Token | Value |
| --- | --- |
| `--gm-duration-fast` | 120ms |
| `--gm-duration-base` | 200ms |
| `--gm-ease` | `cubic-bezier(0.2, 0, 0, 1)` |

The kit has no animation. Transitions are limited to color, padding and transform at `--gm-duration-fast`. `prefers-reduced-motion: reduce` turns all of it off.

## Z-index (web)

| Token | Value |
| --- | --- |
| `--gm-z-base` | 0 |
| `--gm-z-sticky` | 100 |
| `--gm-z-overlay` | 200 |
| `--gm-z-modal` | 300 |
| `--gm-z-toast` | 400 |

## Component geometry (kit pages 11 and 12)

| Name | What | Value |
| --- | --- | --- |
| button-height | Button height | 56px |
| button-height-sm | Small button height | 52px |
| button-pad-x | Button side padding | 32px |
| button-bar | Hover bar thickness | 6px |
| field-height | Field height | 56px |
| field-pad-x | Field side padding | 18px |
| control-size | Checkbox and radio box | 26px |
| switch-w | Switch width | 56px |
| switch-h | Switch height | 32px |
| switch-knob | Switch knob | 18px |
| tag-height | Tag height | 38px |
| tag-pad-x | Tag side padding | 20px |
| nav-height | Header height from 960 px | 92px |
| nav-height-mobile | Header height below 960 px | 72px |
| rule-w | Accent bar width | 72px |
| rule-h | Accent bar height | 6px |
| ring-gap | Focus ring gap | 3px |
| ring-ink | Focus ink ring | 2px |
| ring-teal | Focus teal ring | 3px |
| ring-teal-offset | Teal ring offset from the edge | 7.5px |
| avatar-sizes | Avatar sizes | 32px, 48px, 64px, 112px |

Focus ring: 3 px gap in the surface color, a 2 px ink ring, then a 3 px teal ring starting 7.5 px from the edge.
