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

{{COLOR_TABLE}}

CSS: `--gm-black`, `--gm-teal`, `--gm-white`. Tailwind: `black`, `teal`, `white`, plus `bg` and `fg` that follow the theme.

### Semantic variables

These change with the theme or surface. Use them in components so one rule works on black, white and teal.

{{THEME_TABLE}}

Button colors per theme (`--gm-btn-<kind>-bg`, `-fg`, `-border`, `-pressed-bg`, `-pressed-fg`, `-pressed-border`, `-bar`):

{{BUTTON_TABLE}}

### Gradient

`--gm-gradient-on-dark` (teal to white) and `--gm-gradient-on-light` (teal to black), left to right, 49 stops sampled from the original ramp of the logo. `--gm-gradient` picks the one for the current surface. Stops of the dark version:

{{GRADIENT_STOPS}}

## Typography

Family: `--gm-font-family` = `{{FAMILY}}`. Weights: `--gm-weight-regular` 400, `--gm-weight-bold` 700. Code only: `--gm-font-mono` (web, the kit has no mono face).

{{TYPE_TOKEN_TABLE}}

Sizes are fluid between a {{VP_MIN}} px and a {{VP_MAX}} px viewport (web). At 1280 px and wider they equal the kit scale. Sizes are in `rem` so the browser's font-size setting is respected. Tracking tokens: `--gm-tracking-label` {{TR_LABEL}}em, `--gm-tracking-button` {{TR_BUTTON}}em, `--gm-tracking-nav` {{TR_NAV}}em, `--gm-tracking-tag` {{TR_TAG}}em, `--gm-tracking-chrome` {{TR_CHROME}}em.

## Spacing (web)

4 px grid. Subset of Tailwind's default scale, so `p-4` is 1rem in both.

{{SPACE_TABLE}}

## Radius (kit)

{{RADIUS_TABLE}}

## Border width (kit)

{{BORDER_TABLE}}

## Breakpoints (web)

Mobile first, `min-width`.

{{BREAKPOINT_TABLE}}

## Layout

{{LAYOUT_TABLE}}

`--gm-margin` is 16 px, 32 px from `sm`, 48 px from `md`. The container is `--gm-content-max` wide plus the margins, centered. On the kit's 1920 px canvas that gives 96 px side margins, as on the kit pages.

## Motion (web)

{{MOTION_TABLE}}

The kit has no animation. Transitions are limited to color, padding and transform at `--gm-duration-fast`. `prefers-reduced-motion: reduce` turns all of it off.

## Z-index (web)

{{Z_TABLE}}

## Component geometry (kit pages 11 and 12)

{{COMPONENT_TABLE}}

Focus ring: 3 px gap in the surface color, a 2 px ink ring, then a 3 px teal ring starting 7.5 px from the edge.
