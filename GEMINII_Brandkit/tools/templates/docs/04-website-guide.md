# Building the website

What the site needs, in the order you need it. The starter in `web/starter/` already does all of it with placeholders.

## 1. Pick a path

| Path | Do this |
| --- | --- |
| Static HTML | Copy `web/starter/`. Edit `index.html`. Add pages by copying it. |
| Tailwind v3 | `presets: [require('./tokens/tailwind.preset.cjs')]`, import `css/brand.css` for themes and components. |
| Tailwind v4 | `@import "tailwindcss"; @import "./tokens/tailwind-theme.css"; @import "./css/brand.css";` |
| React, Next, Astro, Vue, Svelte | Import `css/brand.min.css` once in the root layout. Use the `gm-` classes in markup. Put `theme-init.js` in the document head. Reimplement the behaviors in `js/brand.js` (theme toggle, menu, tabs) with the framework's state; the class and attribute contract is in `docs/03-components.md`. |

Tailwind's default palette is removed by the preset: `bg-black`, `bg-teal`, `bg-white`, `text-fg`, `bg-bg` exist, `bg-slate-500` does not. That is the point.

## 2. Head block

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page title | GEMINII</title>
  <meta name="description" content="150 to 160 characters">
  <meta name="theme-color" content="#000000">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="https://example.com/page">

  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="GEMINII">
  <meta property="og:title" content="Page title">
  <meta property="og:description" content="Description">
  <meta property="og:url" content="https://example.com/page">
  <meta property="og:image" content="https://example.com/assets/social/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="GEMINII wordmark on black">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="preload" href="/assets/fonts/Arvo-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/Arvo-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <script src="/assets/js/theme-init.js"></script>
  <link rel="stylesheet" href="/assets/css/brand.min.css">
</head>
```

Rules: Open Graph image URLs are absolute. The font preload needs `crossorigin` even on the same origin. `theme-init.js` is synchronous on purpose, {{THEME_INIT_BYTES}} bytes, and prevents a flash of the wrong theme. The manifest is relative to its own location.

## 3. Fonts

Self-hosted. Do not link Google Fonts: it adds a third-party request, a privacy exposure and a render dependency. `fonts.css` sets `font-display: swap`; the two preloads remove the visible swap on first load. Weight on the wire: {{FONT_KB}} KB for both files.

The fallback stack is Rockwell, Roboto Slab, Georgia, serif: slab serifs, so a missed load looks close. `font-synthesis: none` stops browsers from faking italic or bold.

Characters outside Arvo's Latin set fall back to another font. Use SVG icons, not symbol characters, for arrows and check marks.

## 4. Theme and surfaces

* No `data-theme` attribute: follows the system setting.
* `<html data-theme="light">` or `"dark"` forces a theme. `js/brand.js` toggles it from any `[data-gm-theme-toggle]` button and saves the choice in `localStorage` under `gm-theme`.
* `gm-surface-light|dark|teal` on any section overrides the page theme for that section. Use it for the hero, call-to-action bands and the footer.
* Components never hard-code colors. They read `--gm-bg`, `--gm-fg` and the button variables, so they work on every surface.
* The logo must match the surface: see "A logo that follows the theme" in `docs/01-assets.md`.

## 5. Page anatomy

The starter follows the kit's own page pattern:

1. Skip link, then `header.gm-nav`.
2. `section.gm-hero.gm-surface-dark`: eyebrow, `gm-display` heading (one `h1`), lead, actions.
3. Sections in `gm-section` with a `gm-section-header`: label, counter, 72 x 6 teal bar, `h2`.
4. Content: `gm-cards`, `gm-grid`, `gm-prose` for long text.
5. A teal band for one call to action.
6. `footer.gm-footer.gm-surface-dark`.

Keep one `h1` per page, headings in order, and landmarks (`header`, `nav`, `main`, `footer`). Uppercase headings are CSS, not typed capitals: write headings in normal case in the HTML.

## 6. Responsive

Design from 360 px up. Breakpoints are 640, 960, 1280 and 1920 px. Type is fluid between 360 and 1280 px. Grid spans apply from 960 px; below that every column is full width. The nav collapses below 960 px. Nothing may scroll sideways at 360 px: wrap wide tables in `gm-table-wrap`, and use `overflow-wrap` on long words.

## 7. Images and media

The kit defines no photography or illustration. Defaults until it does:

* Every `<img>` has `alt`, `width` and `height`. Decorative images get `alt=""`.
* `loading="lazy"` below the fold, `fetchpriority="high"` on the hero image only.
* Serve WebP or AVIF with a JPEG fallback, at most 2x the displayed size.
* No drop shadows, filters or rounded corners on imagery (the system is flat, cards are square).
* Do not place text over an image without a solid black or white panel behind it.

## 8. Forms

* A visible `gm-label` for every control, linked with `for`/`id`. A placeholder is an example, never the label.
* `autocomplete` on personal fields, correct `type` (`email`, `tel`).
* Errors: `aria-invalid="true"`, the error icon, a message linked with `aria-describedby`, and a summary `gm-notice--error` with `role="alert"` at the top of long forms. Never rely on color.
* The starter form has `action="#"`. Point it at your endpoint before launch.

## 9. SEO and social

* Unique `title` and `description` per page. Title pattern: `Page | GEMINII`.
* One canonical URL per page.
* Open Graph and `twitter:card` as in the head block. Test with each platform's debugger after deploy.
* `robots.txt` is in the starter. Add `sitemap.xml` and a `Sitemap:` line once the domain is known.
* The JSON-LD block describes the organization. Replace `example.com`. Add `sameAs` with the real social profile URLs.
* `styleguide.html` is `noindex`. Remove it before launch if it should not be public.

## 10. Performance budget

Measured on this package:

| Asset | Size |
| --- | --- |
| `brand.min.css` | {{CSS_MIN_KB}} KB ({{CSS_GZ_KB}} KB gzip) |
| `brand.js` + `theme-init.js` | {{JS_KB}} KB |
| Arvo Regular + Bold | {{FONT_KB}} KB |
| Wordmark SVG | {{WORDMARK_KB}} KB |
| Icon sprite | {{SPRITE_KB}} KB |

No third-party requests. The tests fail if the starter makes one.

## 11. Security headers

The starter has no inline scripts (apart from the JSON-LD data block), no inline styles and no third-party origins, so a strict policy works:

```
Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
```

The tests load the starter under this policy and fail on any violation. Adjust `form-action` to your endpoint. Also send `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and HSTS on the production host.

## 12. Browser support

Current evergreen browsers (Chrome, Edge, Safari, Firefox, roughly the last two years). The CSS uses custom properties, `clamp()`, `:is()`, `:where()`, `:focus-visible`, `inset` and `text-wrap`. `:has()` and `text-wrap: balance` are enhancements: nothing breaks without them. The site works without JavaScript; only the theme toggle, the collapsed mobile menu and tab switching need it.

## 13. Before launch

- [ ] Every `[placeholder]` replaced.
- [ ] `example.com` replaced everywhere (head, JSON-LD).
- [ ] Form action set; spam protection decided.
- [ ] `sitemap.xml` added; `robots.txt` reviewed.
- [ ] Favicons in the site root; manifest served as `application/manifest+json`.
- [ ] Share image checked in platform debuggers.
- [ ] Security headers set.
- [ ] `python3 tests/verify_package.py` passes, or the same checks on the new pages.
- [ ] Open items in `docs/06-open-items.md` decided or consciously deferred.
