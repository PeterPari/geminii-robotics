# GEMINII starter site

Static, no build step, no dependencies. Serve the folder with any static host.

```
python3 -m http.server 8000      # then open http://localhost:8000
```

Open it through a server, not as a file: some browsers block fonts loaded from `file://`.

| File | What |
| --- | --- |
| `index.html` | Page skeleton: head metadata, header, hero, cards, call to action, form, footer. Placeholders are in `[brackets]`. |
| `styleguide.html` | Every token and component, live, in light and dark. Set to `noindex`. Delete before launch if it should not be public. |
| `assets/css/brand.min.css` | Tokens, fonts, base, components in one file. `brand.css` is the readable version. |
| `assets/js/` | `theme-init.js` (load in `<head>`), `brand.js` (theme toggle, mobile menu, tabs). |
| `assets/fonts/` | Arvo Regular and Bold, woff2. |
| `assets/logos/`, `assets/icons/`, `assets/social/` | Logo SVGs, icon sprite, Open Graph image. |
| `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, `icon-*.png`, `site.webmanifest` | Site icons. Keep them in the site root. |

Before launch: replace every `[placeholder]`, replace `https://example.com` in `index.html` with the production origin, and add a `sitemap.xml`.
Full documentation is in the package `docs/` folder.
