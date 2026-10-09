# GEMINII brand rules

Version {{VERSION}}, 2026. These are the rules from the brand kit pages, in text. The PDF is `guidelines/GEMINII_Brandkit.pdf`. Values live in `docs/02-tokens.md`.

## Name

GEMINII. Set in capitals in the wordmark.

## Logo suite

| Piece | What | Files |
| --- | --- | --- |
| Wordmark | Letters G E M I N in Arvo Bold, a teal I that carries the gem, the Gemini glyph with the signature gradient | `logos/svg/wordmark-*.svg` |
| Icon | The Gemini glyph alone | `logos/svg/icon-*.svg` |
| Profile mark | White glyph on a teal square or circle | `logos/svg/profile-mark-*.svg` |
| Gem | Seven concentric hexagons, the dot of the I | `logos/svg/gem-*.svg` |

## Clear space and minimum size

* Clear space is 1X on every side. X is the flat-to-flat width of the gem, {{X_PERCENT}}% of the wordmark width.
* Minimum wordmark width: 160 px on screen, 40 mm in print.
* Minimum icon width: 24 px on screen, 8 mm in print.
* Below the minimum, use the icon.

The exported files are cropped to the artwork. Add the clear space when placing them.

## Color versions

| Version | Background | File |
| --- | --- | --- |
| Full color | Black | `wordmark-full-color-on-dark.svg` |
| Full color | White | `wordmark-full-color-on-light.svg` |
| One color white | Black only | `wordmark-white.svg` |
| One color black | White or teal | `wordmark-black.svg` |

* The glyph gradient runs from teal to the highest-contrast color: white on black, black on white.
* Never place the full-color wordmark on teal.

## Misuse

Do not: stretch or squash, rotate or skew, swap the color roles, outline the letters, use full color on teal, move or resize the gem, crop the wordmark, use the dark version on white.

## Color

Exactly three colors. No tints, no shades.

{{COLOR_TABLE}}

* Primary is black, secondary is teal, tertiary is white.
* Teal is a fill and an accent. Teal text works on black only.
* White text on teal and teal text on white fail contrast. Do not use them for text.
* CMYK is a direct conversion from sRGB. Proof before print.

Contrast (WCAG 2.2):

{{CONTRAST_TABLE}}

The gem artwork carries four neutral grays and a glow (`#E0E1DD #B3B2B2 #494949 #373737`). They belong to the logo, not to the palette. The gradient is an interpolation between teal and white or black.

## Signature gradient

Left to right. Teal is solid for the first 19%, then eases to the far color. White is the far color on black, black is the far color on white. Use it for the glyph and for decorative fills. Black text is the only text color that passes on the teal to white ramp. Do not set text on the teal to black ramp.

## Typography

Arvo, by Anton Koovit. Regular 400 and Bold 700. SIL Open Font License 1.1.

* Bold uppercase is primary text. Regular sentence case is secondary text.
* Emphasis inside copy is Bold. Arvo italic is not part of the kit.

{{TYPE_TABLE}}

## Interface principles

* Flat. No shadows, no blur, no gradients on controls.
* 2 px borders. 4 px radius on buttons and fields. Square cards. Pill tags.
* Labels are Bold, uppercase, tracked.
* Three surfaces: black, white, teal. Text on a surface is the opposite color: white on black, black on white, black on teal.
* Focus is a double ring: an ink ring, then a teal ring.
* Disabled is a dashed outline in Regular weight, not a faded fill.
* Status is carried by an icon and a heading, never by color alone.

Component specifications are in `docs/03-components.md`.

## Not decided

Voice and tone, photography, illustration, motion, data visualization, and several interface elements are not defined by the kit. The package ships working defaults for what a website needs. `docs/06-open-items.md` lists each one.
