# Accessibility

Target: WCAG 2.2 AA. The palette decides most of it.

## Contrast

| Pair | Ratio | Level |
| --- | --- | --- |
| black on white | 21:1 | AAA |
| white on black | 21:1 | AAA |
| black on teal | 9.98:1 | AAA |
| teal on black | 9.98:1 | AAA |
| white on teal | 2.11:1 | FAIL |
| teal on white | 2.11:1 | FAIL |

Allowed text pairings: black on white, white on black, black on teal, teal on black. Not allowed: white on teal, teal on white.

Teal on white (2.11:1) fails the 3:1 needed for UI parts too. It is used only where something else carries the meaning:

| Teal on white or teal | Carried by |
| --- | --- |
| Current nav item underline | Bold weight and `aria-current="page"` |
| Selected tab underline | Bold weight and `aria-selected="true"` |
| Link hover underline | The underline thickens from 2 px to 4 px |
| Accent bar (72 x 6) | Decoration, `aria-hidden` |
| Outer focus ring | The ink ring inside it, 21:1 |
| Switch on state | The knob position and the black border |

The profile mark (white glyph on teal, 2.11:1) is a logo, which WCAG exempts from contrast requirements.

## Focus

Every interactive element shows the double ring on `:focus-visible`: 2 px ink ring, then a 3 px teal outline. The outline also shows in forced-colors mode. Hidden native inputs (checkbox, radio, switch) pass focus to the drawn control.

## Targets

Buttons are 56 px (52 small) high. Check, radio and switch rows are at least 44 px high. Inline links are exempt. Nothing is under 24 x 24 px (WCAG 2.5.8).

## Motion

Transitions last 120 ms and affect color, padding and transform only. `prefers-reduced-motion: reduce` sets them to 0.01 ms. There is no autoplay and no parallax.

## Structure the components assume

* One `h1`, headings in order, landmarks present, `lang` set.
* Skip link first in the body.
* Every control has a label; icon-only buttons have a hidden text label.
* Errors use `aria-invalid`, `aria-describedby`, an icon and text.
* Tabs follow the ARIA tabs pattern with arrow, Home and End keys.
* The mobile menu button has `aria-expanded` and `aria-controls`, and Escape closes it.
* Tables that scroll are focusable regions.

## Color alone

Status never depends on color: error, warning, success and information have different icon shapes and a heading. Disabled controls are dashed, not faded. Required, selected, current and checked states have a shape or weight change.

## How it is tested

`tests/verify_package.py` runs axe-core on the starter and the style guide, in light and dark, at 360 and 1280 px, and fails on any violation. It also computes the contrast of every rendered text run against the background behind it, tabs through each page to confirm a ring on every stop, and checks reduced-motion. Automated checks cover part of WCAG. Before launch, do a keyboard pass and a screen reader pass on the real pages.

Demonstrations of failing pairings in the style guide are marked `data-demo-fail` and excluded from the checks.
