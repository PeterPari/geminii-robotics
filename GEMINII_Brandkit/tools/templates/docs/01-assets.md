# Assets

Every file, what it is for, and how to embed it. All SVG text is outlined: no font is needed to display a logo.

## Logos, SVG (`logos/svg/`)

{{LOGO_FILE_TABLE}}

Files carry fixed size attributes (2000 px wide, profile marks 1500 px) so design tools open them large. Set the width in CSS or in the tag. The files are cropped to the artwork: add 1X clear space around them.

### Embedding

```html
<!-- Full color: use <img>. Pick the variant for the background. -->
<img src="logos/svg/wordmark-full-color-on-dark.svg" alt="GEMINII" width="190" height="54">

<!-- One color that follows the text color: inline sprite. -->
<svg class="logo" width="190" height="54" role="img" aria-label="GEMINII"><use href="logos/sprite.svg#wordmark"></use></svg>
```

```css
.logo { color: var(--gm-fg); }
```

`logos/sprite.svg` has three symbols: `wordmark`, `icon`, `gem`, all in `currentColor`. The same artwork is also in `wordmark-currentcolor.svg`, `icon-currentcolor.svg` and `gem-currentcolor.svg` for inlining; those have no fixed width or height.

The full-color files use gradients with fixed ids. Do not paste two of them inline in one page: ids collide. Use `<img>`.

### A logo that follows the theme

Render the variants and let CSS pick:

```html
<img class="gm-logo--on-dark" src="logos/svg/wordmark-full-color-on-dark.svg" alt="GEMINII" width="190" height="54">
<img class="gm-logo--on-light" src="logos/svg/wordmark-full-color-on-light.svg" alt="GEMINII" width="190" height="54">
```

`gm-logo--on-dark`, `gm-logo--on-light` and `gm-logo--on-teal` show only inside the matching theme or surface. Hidden images are not read by screen readers, so each can carry the same alt text.

## Logos, PNG (`logos/png/`)

Transparent. Named `<file>-<width>w.png`. Use them where SVG is not accepted: email, slides, office documents, marketplaces.

{{PNG_TABLE}}

Email signature: `wordmark-full-color-on-light-480w.png` displayed at 240 px wide. Never use the dark-background file on white.

## Site icons (`favicons/`)

{{FAVICON_TABLE}}

The favicon is the profile mark (white glyph on teal), so the tab, the home-screen icon and the social avatar match. `icon-maskable-512.png` shrinks the glyph to fit the 80% safe circle that Android masks to. Keep all of these in the site root, next to `index.html`. Head tags are in `docs/04-website-guide.md`.

## Social images (`social/`)

{{SOCIAL_TABLE}}

All are the full-color wordmark on black, centered. `og-image.png` is the default share image for Open Graph and X (`summary_large_image`). Keep the important content inside the middle of each banner: platforms crop the edges.

## UI icons (`icons/`)

`icons/sprite.svg` (all icons as symbols) and `icons/svg/<name>.svg` (one file each). 24 px grid, `currentColor`.

{{ICON_TABLE}}

```html
<svg width="24" height="24" aria-hidden="true" focusable="false"><use href="icons/sprite.svg#arrow-right"></use></svg>
```

Icons are decorative when a text label sits next to them: use `aria-hidden="true"`. An icon-only button needs a text label: use a `gm-visually-hidden` span.

## Fonts (`fonts/`)

`Arvo-Regular.woff2`, `Arvo-Bold.woff2` for the web. `Arvo-Regular.ttf`, `Arvo-Bold.ttf` for design tools and documents. `OFL.txt` is the license, keep it with the fonts.

## Guidelines (`guidelines/`)

`GEMINII_Brandkit.pdf` (12 pages, bookmarked), `GEMINII_Brandkit.svg` (all pages stacked) and `pages/01..12-*.svg` (one 1920 x 1080 SVG per page).
