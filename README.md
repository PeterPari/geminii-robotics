# Geminii Robotics Website

This repository houses the website for Geminii Robotics, the Browning School's secondary FTC robotics team, deployed at <https://geminii.browning.edu>. It started as a copy of the [Ultro Robotics](https://ultro.browning.edu) site; the legacy Ultro pages that used to live under `/old/` were removed and can be recovered from git commit `a6e601f`.

Our website uses the [Astro](https://astro.build/) web framework, as well as [Tailwind CSS](https://tailwindcss.com/) and [daisyUI](https://daisyui.com/) for styling. The typeface is Arvo, self-hosted under `public/assets/fonts/`.

## Project Structure

```text
/
├── public/
│   ├── assets/
│   │   ├── brand/
│   │   │   └── { GEMINII wordmark SVGs }
│   │   └── fonts/
│   │       └── { Arvo woff2 files and OFL license }
│   └── { favicons and other non-processed public assets }
├── src/
│   ├── assets/
│   │   └── { buildtime-processed assets }
│   ├── components/
│   │   └── { custom components used }
│   ├── layouts/
│   │   └── { base layouts used across different types of pages }
│   ├── pages/
│   │   └── { individual pages, plus the robots.txt endpoint }
│   └── styles/
│       └── { global css properties, tailwind/daisyui config, GEMINII theme }
└── package.json
```

## License

### Code
The code in this repository is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See the [LICENSE](LICENSE) file for details.

### Assets & Content
The image assets in this repository, located under `public/**` and `src/assets/*`, documentation, and/or other written content are licensed under the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0), except for third-party assets hosted in `src/assets/sponsors`. See the [LICENSE-CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0) file for details.

## Copyright
Copyright © Ultro Robotics

# Development
Install dependencies:
```bash
deno i
```

Run development server:
```bash
deno run dev
```

Build site pages (located in `dist/`):
```bash
deno run build
```

Preview built site:
```bash
deno run preview
```

# Deployment
Every push to `main` builds the site and publishes `dist/` to GitHub Pages via `.github/workflows/deploy.yml`. In the repo's **Settings → Pages**, **Source** must be set to **GitHub Actions** (not "Deploy from a branch", which serves the raw Astro source and 404s). The custom domain is kept in `public/CNAME`.

# TODO
- [ ] finish building content pages
- [ ] convert navbar to use CSS scroll-driven animations instead of JS
- [x] footer
- [x] replace logos with transparent SVG assets
- [x] ~~mobile support~~ (sort of)
- [ ] View Transition API
- [ ] accessibility: respect reduced motion, etc..
- [ ] make this website as fast as humanly possible
  - [ ] optimize css, js bundles
  - [ ] inline critical css (see [@playform/inline](https://github.com/PlayForm/Inline)
  - [x] preload fonts
