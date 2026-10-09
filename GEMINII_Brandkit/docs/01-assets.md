# Assets

Every file, what it is for, and how to embed it. All SVG text is outlined: no font is needed to display a logo.

## Logos, SVG (`logos/svg/`)

| File | What | Use |
| --- | --- | --- |
| `gem-black.svg` | Gem, one color black | On white or teal. |
| `gem-currentcolor.svg` | Gem, one color, inherits text color | Inline use. |
| `gem-full-color.svg` | Gem, full artwork | Small accents, 24 px and up. |
| `gem-white.svg` | Gem, one color white | On black. |
| `icon-black.svg` | Icon, one color black | On white or teal. |
| `icon-currentcolor.svg` | Icon, one color, inherits text color | Inline use, theming. |
| `icon-gradient-on-dark.svg` | Icon, gradient to white | On black. |
| `icon-gradient-on-light.svg` | Icon, gradient to black | On white. |
| `icon-teal.svg` | Icon, teal | On black. Teal on white fails contrast. |
| `icon-white.svg` | Icon, one color white | On black. |
| `profile-mark-circle.svg` | Profile mark, circle | Round avatars, `gm-avatar`. |
| `profile-mark-square.svg` | Profile mark, square | Avatars, app icons, favicon source. |
| `wordmark-black.svg` | Wordmark, one color black | On white or teal. |
| `wordmark-currentcolor.svg` | Wordmark, one color, inherits text color | Inline use, theming. On black, white or teal. |
| `wordmark-full-color-on-dark.svg` | Wordmark, full color | On black. Primary. |
| `wordmark-full-color-on-light.svg` | Wordmark, full color | On white. |
| `wordmark-white.svg` | Wordmark, one color white | On black only. |

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

| File prefix | Sizes (px) |
| --- | --- |
| `gem-black-<w>w.png` | 1024 x 1182, 128 x 148, 512 x 591 |
| `gem-full-color-<w>w.png` | 1024 x 1182, 128 x 148, 512 x 591 |
| `gem-white-<w>w.png` | 1024 x 1182, 128 x 148, 512 x 591 |
| `icon-black-<w>w.png` | 1024 x 971, 128 x 121, 512 x 485 |
| `icon-gradient-on-dark-<w>w.png` | 1024 x 971, 128 x 121, 512 x 485 |
| `icon-gradient-on-light-<w>w.png` | 1024 x 971, 128 x 121, 512 x 485 |
| `icon-teal-<w>w.png` | 1024 x 971, 128 x 121, 512 x 485 |
| `icon-white-<w>w.png` | 1024 x 971, 128 x 121, 512 x 485 |
| `profile-mark-circle-<w>w.png` | 1024 x 1024, 128 x 128, 512 x 512 |
| `profile-mark-square-<w>w.png` | 1024 x 1024, 128 x 128, 512 x 512 |
| `wordmark-black-<w>w.png` | 1920 x 543, 480 x 136, 960 x 271 |
| `wordmark-full-color-on-dark-<w>w.png` | 1920 x 543, 480 x 136, 960 x 271 |
| `wordmark-full-color-on-light-<w>w.png` | 1920 x 543, 480 x 136, 960 x 271 |
| `wordmark-white-<w>w.png` | 1920 x 543, 480 x 136, 960 x 271 |

Email signature: `wordmark-full-color-on-light-480w.png` displayed at 240 px wide. Never use the dark-background file on white.

## Site icons (`favicons/`)

| File | Size (px) | Use |
| --- | --- | --- |
| `apple-touch-icon.png` | 180 x 180 | iOS home screen. Opaque, no rounding (iOS rounds it). |
| `favicon.ico` | 16, 32, 48 | Legacy and default. 16, 32, 48 px in one file. |
| `favicon.svg` | vector | Modern browsers. Profile mark, scales to any size. |
| `icon-192.png` | 192 x 192 | Android and manifest. |
| `icon-512.png` | 512 x 512 | Manifest, splash. |
| `icon-maskable-512.png` | 512 x 512 | Manifest `purpose: maskable`. Glyph inside the 80% safe zone. |
| `site.webmanifest` | text | Name, colors, icons. |

The favicon is the profile mark (white glyph on teal), so the tab, the home-screen icon and the social avatar match. `icon-maskable-512.png` shrinks the glyph to fit the 80% safe circle that Android masks to. Keep all of these in the site root, next to `index.html`. Head tags are in `docs/04-website-guide.md`.

## Social images (`social/`)

| File | Size (px) | Use |
| --- | --- | --- |
| `linkedin-banner-1584x396.png` | 1584 x 396 | LinkedIn profile banner. |
| `og-image.png` | 1200 x 630 | Open Graph and X large card. Default share image. |
| `profile-1080.png` | 1080 x 1080 | Instagram and other square avatars. The platform crops the circle. |
| `x-header-1500x500.png` | 1500 x 500 | X profile header. |
| `youtube-banner-2560x1440.png` | 2560 x 1440 | YouTube channel banner. Safe area is the center 1546 x 423. |

All are the full-color wordmark on black, centered. `og-image.png` is the default share image for Open Graph and X (`summary_large_image`). Keep the important content inside the middle of each banner: platforms crop the edges.

## UI icons (`icons/`)

`icons/sprite.svg` (all icons as symbols) and `icons/svg/<name>.svg` (one file each). 24 px grid, `currentColor`.

| Id | Family | Name |
| --- | --- | --- |
| `menu` | line | Menu |
| `close` | line | Close |
| `chevron-down` | line | Chevron down |
| `chevron-right` | line | Chevron right |
| `arrow-right` | line | Arrow right |
| `arrow-up-right` | line | Arrow up right (external) |
| `check` | line | Check |
| `plus` | line | Plus |
| `minus` | line | Minus |
| `search` | line | Search |
| `mail` | line | Mail |
| `error` | status | Error |
| `success` | status | Success |
| `warning` | status | Warning |
| `info` | status | Information |

```html
<svg width="24" height="24" aria-hidden="true" focusable="false"><use href="icons/sprite.svg#arrow-right"></use></svg>
```

Icons are decorative when a text label sits next to them: use `aria-hidden="true"`. An icon-only button needs a text label: use a `gm-visually-hidden` span.

## Fonts (`fonts/`)

`Arvo-Regular.woff2`, `Arvo-Bold.woff2` for the web. `Arvo-Regular.ttf`, `Arvo-Bold.ttf` for design tools and documents. `OFL.txt` is the license, keep it with the fonts.

## Guidelines (`guidelines/`)

`GEMINII_Brandkit.pdf` (12 pages, bookmarked), `GEMINII_Brandkit.svg` (all pages stacked) and `pages/01..12-*.svg` (one 1920 x 1080 SVG per page).
