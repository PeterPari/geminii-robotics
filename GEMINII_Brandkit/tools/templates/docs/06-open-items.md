# Open items

What the brand kit pages do not define, what this package assumes in the meantime, and what needs a decision. Nothing here was invented as brand content: the defaults are technical, and copy is left as `[placeholders]`.

## Needs content or a decision from the owner

| Area | State | Package default | Decision |
| --- | --- | --- | --- |
| Site structure | Not defined | Starter has header, hero, cards, call to action, form, footer | Sitemap and page list |
| Copy, voice and tone | Not defined | `[placeholders]` only | Write the voice guide, then the copy |
| Tagline, description, meta descriptions | Not defined | `[Page description]` | Final text |
| Domain, canonical URLs | Unknown | `https://example.com` | Production origin |
| Social profiles | Unknown | None | URLs for the JSON-LD `sameAs` list |
| Photography | Not defined | None in the starter; technical rules in `docs/04-website-guide.md` | Art direction |
| Illustration | Not defined | None | Style, or none |
| Legal pages, cookie notice, copyright line | Not defined | `© [Year] GEMINII` | Final text, jurisdiction |
| Form handling | Unknown | `action="#"` | Endpoint, spam protection |
| Analytics | Not in the package | None | Choice, and a consent approach if needed |

## Defaults added for the web (the kit is silent)

These are in the token files marked **web**. Change them in `tools/tokens.py`.

| Area | Default |
| --- | --- |
| Spacing | 4 px grid, twelve steps |
| Breakpoints | 640, 960, 1280, 1920 px |
| Fluid type | Interpolates from a 360 px to a 1280 px viewport; minimums 48, 36, 28, 24, 20, 18, 14 px |
| Container | 1728 px content plus margins, which gives the kit's 96 px margins at 1920 px |
| Motion | 120 ms and 200 ms, color, padding, transform; none decorative |
| Z-index | 0, 100, 200, 300, 400 |
| Fallback fonts | Rockwell, Roboto Slab, Georgia, serif |
| Monospace | System stack, for code only |
| Italics | Not used. `em` renders Bold |
| UI icons | Eleven line icons and four status icons. The error icon follows the kit; the rest are new |
| Notice and table | New components built from kit parts |
| Theme default | Follows the system setting |
| Favicon | Profile mark (white glyph on teal) |

## Components not designed

Build these from the tokens when needed, then add them to the style guide: modal, toast, tooltip, popover, accordion, pagination, breadcrumbs, progress bar, skeleton, date picker, file upload, search field, dropdown menu, carousel.

## Data visualization

Three colors cannot separate many series. Proposal when charts arrive: black and teal fills, white with a 2 px black outline, plus dash and hatch patterns, direct labels instead of a legend. Not shipped, because it is a design decision.

## Known compromises

* The profile mark is white on teal (2.11:1). It is the supplied identity and a logo, so it is exempt, but it is the weakest contrast in the system.
* The favicon is that same mark. A black glyph on teal would read better at 16 px; say if you want it.
* The four neutral grays in the gem artwork are part of the logo and outside the three-color palette.
* CMYK values are a direct sRGB conversion. Proof before print.
