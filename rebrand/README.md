# rebrand/

Everything pass 1 of the GEMINII rebrand (colors, logos, typeface) created that is not part of the site. **This folder is excluded from deployment** (Astro builds only `src/` and `public/`; nothing here is imported by the site).

| File | What |
| --- | --- |
| `REPORT.md` | Counts, page list, gradients, list-only items, overflow fixes, open questions, verify output |
| `INVENTORY.md` | Ultro name, links, contacts and descriptions for the later text-and-links pass (nothing in it is edited) |
| `verify.py` | Builds and serves the site, then checks every page at 360 and 1280 px (checks a to f) |
| `make_assets.py` | Copies the kit files the site uses (Arvo, icon logo, favicons) into `public/` and rasterises the 96 px favicon |
| `make_inventory.py` | Regenerates `INVENTORY.md` |
| `baseline/` | Pre-edit capture per page and width: rendered text, heading outline, every href/src/srcset/action, form fields, head metadata, network and overflow data (`meta.json` records the git commit) |
| `screenshots/before/`, `screenshots/after/` | Full-page screenshots, `page-width.png` |
| `verify-output.txt`, `verify-report.json` | Output of the last `verify.py` run |

## Run

```bash
pip install playwright pillow      # Chrome is driven through Playwright's "chrome" channel
python3 rebrand/verify.py          # build, serve, check a to f against baseline/
python3 rebrand/verify.py --quick  # skip hover/focus/active scans
```

Scope: the redesigned "in construction" site. The legacy `/old/` page was deleted at the owner's request (recoverable from git commit `a6e601f`); its baseline capture stays in `baseline/` as a record.
