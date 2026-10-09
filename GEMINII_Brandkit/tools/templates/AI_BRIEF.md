# Brief for AI tools and contractors: build with GEMINII

Paste this file into the prompt, or point the tool at this folder. Read `BRAND.md` for the rules and `docs/03-components.md` for markup.

## Hard rules

1. Three colors only: black `#000000`, teal `#00C7C5`, white `#FFFFFF`. No tints, no shades, no other hex. Use `var(--gm-black)`, `var(--gm-teal)`, `var(--gm-white)` or the semantic `var(--gm-bg)`, `var(--gm-fg)`.
2. Font is Arvo, Regular 400 and Bold 700, self-hosted from `fonts/`. No Google Fonts link. No italics. No other weights.
3. Headings and labels: Bold, uppercase. Body: Regular, sentence case. Emphasis: Bold.
4. Never use teal for text on white. Never use white text on teal. Teal text is allowed on black only.
5. No shadows, no blur, no opacity-based states, no gradients on controls, no rounded cards. Radius: 4 px on buttons and fields, 0 on cards, pill on tags and switches.
6. Borders are 2 px. Focus is the double ring (already in `brand.css`). Disabled is a dashed outline. Do not remove focus styles.
7. Status (error, success, warning, info) is shown with an icon from `icons/sprite.svg` and a heading, not with color.
8. Logo: use the files in `logos/svg/`. Never redraw, recolor, stretch, rotate, outline or crop. Keep 1X clear space (X is the gem width, 6.1% of the wordmark width). Full color on black or white, one-color white on black only, one-color black on white or teal. Minimum width 160 px, below that use the icon.
9. Use the `gm-` classes from `css/components.css` before writing new CSS. New CSS must use `var(--gm-*)` tokens, never literal values.
10. Choose a section surface with `gm-surface-light`, `gm-surface-dark` or `gm-surface-teal`. Components inside follow it.
11. Do not invent copy, claims, testimonials, statistics or imagery. Leave `[placeholders]` where content is missing and list them at the end.
12. Meet WCAG 2.2 AA: 4.5:1 text, 3:1 for large text and UI parts, 44 px touch targets for primary actions, visible focus, one `h1`, labels on every field, alt text on every image.

## Files

| Need | File |
| --- | --- |
| Everything in one stylesheet | `css/brand.min.css` (readable: `css/brand.css`) |
| Tokens as CSS variables | `tokens/tokens.css` |
| Tokens as JSON, SCSS, Tailwind | `tokens/tokens.json`, `tokens/tokens.scss`, `tokens/tailwind.preset.cjs`, `tokens/tailwind-theme.css` |
| Theme toggle, mobile menu, tabs | `js/brand.js`, plus `js/theme-init.js` in `<head>` |
| Icons | `icons/sprite.svg`, ids: {{ICON_IDS}} |
| Page skeleton | `web/starter/index.html` |
| Every component live | `web/starter/styleguide.html` |

## Class cheat sheet

Layout: `gm-container`, `gm-section`, `gm-grid` + `gm-span-1..12`, `gm-cards`, `gm-stack`, `gm-cluster`, `gm-prose`, `gm-section-header`, `gm-rule`.
Type: `gm-display`, `gm-h1`, `gm-h2`, `gm-h3`, `gm-body-lg`, `gm-body`, `gm-label-text`. Bare `h1` to `h6`, `p`, `a`, `strong`, `em` are already styled.
Controls: `gm-btn` + `gm-btn--primary|secondary|tertiary` + `gm-btn--sm|block`, `gm-field`, `gm-label`, `gm-input`, `gm-textarea`, `gm-select`, `gm-check`, `gm-radio`, `gm-switch`.
Content: `gm-card` + `gm-card--white|teal|black`, `gm-tag` + `gm-tag--white|teal|black`, `gm-avatar`, `gm-notice`, `gm-table`, `gm-tablist` + `gm-tab` + `gm-tabpanel`.
Chrome: `gm-nav`, `gm-hero`, `gm-footer`, `gm-skip-link`, `gm-visually-hidden`.

## Done means

The page passes `python3 tests/verify_package.py` for the starter, or the same checks on the new pages: no console errors, no horizontal scroll at 360 px, axe clean in light and dark, no color outside the palette.
