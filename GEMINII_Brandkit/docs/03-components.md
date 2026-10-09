# Components

All classes carry the `gm-` prefix and read the tokens in `tokens/tokens.css`. Open `web/starter/styleguide.html` to see each one live, with every state. Geometry comes from kit pages 11 and 12.

State classes `is-hover`, `is-pressed`, `is-focus` exist only to show a state in documentation. Real states come from `:hover`, `:active`, `:focus-visible`, `:disabled` and ARIA attributes.

## Surfaces

`gm-surface-light` (white, black text), `gm-surface-dark` (black, white text), `gm-surface-teal` (teal, black text). Put one on any section. It re-scopes `--gm-bg`, `--gm-fg` and every component variable. With no surface class the page follows `<html data-theme="light|dark">`, or the system setting when the attribute is absent.

Teal is a surface for one-color-black content. Do not put the full-color wordmark on it: use `wordmark-black.svg` (`gm-logo--on-teal`).

## Button

```html
<button class="gm-btn gm-btn--primary" type="button">Button</button>
<a class="gm-btn gm-btn--secondary" href="/">Link styled as a button</a>
<button class="gm-btn gm-btn--tertiary gm-btn--sm" type="button" disabled>Disabled</button>
```

56 px high (`gm-btn--sm`: 52), 4 px radius, 2 px border. Label: Bold 16 px, uppercase, 0.12em tracking. States:

| State | Look |
| --- | --- |
| Default | Per kind and surface, see the button table in `docs/02-tokens.md`. |
| Hover | A 6 px bar at the foot, label lifts 2 px. Only on devices that hover. |
| Pressed | Colors invert. |
| Focus | Double ring. |
| Disabled | Dashed outline, Regular label, no fill. Use the `disabled` attribute, or `aria-disabled="true"` on a link. |

Use primary for the one main action per view, secondary for supporting actions, tertiary for the rest. Add an icon with `<svg>` inside the button; it is sized to the text.

## Text field

```html
<div class="gm-field">
  <label class="gm-label" for="email">Label</label>
  <input class="gm-input" id="email" type="email" placeholder="Placeholder" autocomplete="email">
</div>
```

56 px high, 2 px border, 4 px radius. Placeholder is Regular, an entered value is Bold. Always set `placeholder` (the Bold-when-filled rule reads `:placeholder-shown`) and always keep the visible label. Textarea: `gm-textarea`. Select: wrap in `<div class="gm-select">`.

Error: set `aria-invalid="true"`, add the icon inside `gm-field__control`, and a message linked with `aria-describedby`:

```html
<div class="gm-field">
  <label class="gm-label" for="e">Label</label>
  <div class="gm-field__control">
    <input class="gm-input" id="e" type="text" placeholder="Placeholder" aria-invalid="true" aria-describedby="e-msg">
    <svg class="gm-field__icon" aria-hidden="true"><use href="icons/sprite.svg#error"></use></svg>
  </div>
  <p class="gm-field__message" id="e-msg">Error message text.</p>
</div>
```

The error edge reads 4 px thick, drawn as an inset shadow so the layout does not move. Disabled is a dashed border.

## Checkbox, radio, switch

```html
<label class="gm-check"><input type="checkbox"><span class="gm-check__box"></span>Label</label>
<label class="gm-radio"><input type="radio" name="g"><span class="gm-radio__dot"></span>Label</label>
<label class="gm-switch"><input type="checkbox" role="switch"><span class="gm-switch__track"></span>Label</label>
```

The native input stays in the page for forms, keyboard and screen readers. The span is what you see. The control is 26 px, the switch 56 x 32. The label row is at least 44 px high.

## Link

Bare `<a>` is the inline link: underline 2 px, thickens to 4 px in teal on hover. Links inside buttons, nav and cards reset it.

## Header and navigation

```html
<header class="gm-nav">
  <div class="gm-container"><div class="gm-nav__inner">
    <a class="gm-nav__brand" href="/">...logo...</a>
    <button class="gm-nav__toggle" type="button" data-gm-nav-toggle="menu" aria-expanded="false" aria-controls="menu">...</button>
    <nav class="gm-nav__menu" id="menu" aria-label="Primary">
      <ul class="gm-nav__list"><li><a class="gm-nav__link" href="/" aria-current="page">Item</a></li></ul>
      <div class="gm-nav__actions"><a class="gm-btn gm-btn--secondary gm-btn--sm" href="/">Action</a></div>
    </nav>
  </div></div>
</header>
```

92 px high from 960 px, 72 px below. Items: 16 px, uppercase, 0.12em tracking; the current item is Bold with a 4 px teal underline and `aria-current="page"`. Below 960 px the menu collapses behind the toggle when `js/brand.js` runs; without JavaScript it stays open. `gm-nav--boxed` draws the full 2 px border, as on kit page 12.

## Tabs

```html
<div data-gm-tabs>
  <div class="gm-tablist" role="tablist" aria-label="Example">
    <button class="gm-tab" role="tab" id="t1" aria-selected="true" aria-controls="p1" type="button">Tab one</button>
    <button class="gm-tab" role="tab" id="t2" aria-selected="false" aria-controls="p2" tabindex="-1" type="button">Tab two</button>
  </div>
  <div class="gm-tabpanel" role="tabpanel" id="p1" aria-labelledby="t1" tabindex="0">...</div>
  <div class="gm-tabpanel" role="tabpanel" id="p2" aria-labelledby="t2" tabindex="0" hidden>...</div>
</div>
```

Arrow keys, Home and End move between tabs. The selected tab is Bold with a 5 px teal underline.

## Card

```html
<article class="gm-card gm-card--teal">
  <h3 class="gm-card__title">Card title</h3>
  <div class="gm-card__body"><p>Text</p></div>
  <a class="gm-card__link" href="#">Link</a>
</article>
```

Square corners, 2 px edge, 24 px padding. Variants `gm-card--white`, `gm-card--teal`, `gm-card--black`. Each re-scopes the theme, so links, buttons and focus rings inside it use the card colors. Use `gm-cards` for an auto-fitting grid.

## Tag

`<span class="gm-tag">Tag</span>`. Pill, 38 px high, Label type. Variants `gm-tag--white|teal|black`. Plain `gm-tag` is an outline in the surface colors.

## Avatar

```html
<span class="gm-avatar"><img src="logos/svg/profile-mark-circle.svg" alt="GEMINII"></span>
```

Sizes: 32 (`--sm`), 48 (default), 64 (`--lg`), 112 (`--xl`).

## Notice (web)

```html
<div class="gm-notice gm-notice--error" role="alert">
  <svg class="gm-notice__icon" aria-hidden="true"><use href="icons/sprite.svg#error"></use></svg>
  <div><p class="gm-notice__title">Error</p><p>Message text.</p></div>
</div>
```

Icons: `error`, `warning`, `success`, `info`. Use `role="alert"` for errors, `role="status"` otherwise. The error notice has the heavier edge, the same signal as the error field.

## Table (web)

Wrap in `<div class="gm-table-wrap" tabindex="0" role="region" aria-label="...">` so a wide table scrolls and stays keyboard reachable.

## Section header

```html
<header class="gm-section-header">
  <div class="gm-section-header__meta"><span class="gm-eyebrow">01 Section</span><span class="gm-counter">01 / 03</span></div>
  <span class="gm-rule" aria-hidden="true"></span>
  <h2>Title</h2>
</header>
```

The kit page header: label, counter, 72 x 6 teal bar, title.

## Layout helpers (web)

`gm-container`, `gm-section` (48 px, 96 px from `md`), `gm-grid` with `gm-span-1` to `gm-span-12` (spans apply from `md`, full width below), `gm-cards`, `gm-stack` (+ `--sm|--lg|--xl`), `gm-cluster` (+ `--sm|--lg`), `gm-prose`, `gm-hero`, `gm-footer`, `gm-skip-link`, `gm-visually-hidden`.

## Where the CSS differs from the kit pages

| Item | Kit page | CSS | Why |
| --- | --- | --- | --- |
| Field focus ring | Teal ring only | Double ring: ink, then teal | Teal on white is 2.11:1, below the 3:1 a focus indicator needs. Buttons already use the double ring; fields now match. |
| Card padding | 22 px | 24 px | Keeps the 4 px grid. |
| Hover bar | 6 px visible plus 1 px over the border | 6 px inside the border | CSS inset shadow stops at the border. |
| Error field edge | 4 px stroke | 2 px border plus 2 px inset shadow | Same look, no layout shift. |
| Link underline offset | Fixed 6 px below the baseline | `0.25em` | Scales with the text size. |

Everything else is taken from the kit pages.
