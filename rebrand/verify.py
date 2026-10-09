#!/usr/bin/env python3
"""GEMINII rebrand verification (pass 1: colors, logos, typeface).

Builds the site with its own build command, serves dist/ locally, and drives Chrome
through every page at 360 and 1280 px.

    python3 rebrand/verify.py --baseline   # capture the pre-edit baseline (run on the original site)
    python3 rebrand/verify.py              # run checks a-f against the baseline
    python3 rebrand/verify.py --quick      # skip hover/focus/active state scans while iterating
    python3 rebrand/verify.py --no-build   # reuse an existing dist/

Needs: python3, `pip install playwright pillow`, Google Chrome (driven through Playwright's
"chrome" channel; falls back to Playwright's bundled Chromium), and the site's own toolchain
(deno or npm). This folder (rebrand/) is excluded from deployment.

Scope: the redesigned "in construction" site. (The legacy /old/ page was deleted at the owner's request.)

Checks
  a  unchanged: rendered text, heading outline, href/src/srcset/action values, form fields
  b  palette: every color property, shadow color and gradient stop is black, teal, white or
     transparent (black-alpha shadows pass), in default, hover, focus and active states
  c  contrast: every text run is black on white/teal, white on black or teal on black, WCAG AA
  d  fonts: Arvo 400/700 only, normal style, loaded from site files, no font-host requests
  e  logos: every logo slot renders a kit logo, no baseline Ultro logo file is referenced,
     favicon / apple-touch-icon / og:image equal the kit's
  f  health: 200 everywhere, no new console errors or failed requests, no new overflow
"""
import argparse
import base64
import functools
import hashlib
import http.server
import io
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is missing: pip install playwright pillow")
try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:
    sys.exit("pillow is missing: pip install playwright pillow")

# ============================ in-page JavaScript ============================
# ---------------------------------------------------------------------------
# COLLECT: rendered text, heading outline, attribute inventory, form controls,
# head metadata, logo slots and overflow signatures. Used for baseline and after.
# ---------------------------------------------------------------------------
COLLECT_JS = r"""
(cfg) => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const pathOf = (el) => {
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.documentElement) {
      const p = el.parentElement;
      const idx = p ? Array.prototype.indexOf.call(p.children, el) : 0;
      parts.push(el.tagName.toLowerCase() + ':' + idx);
      el = p;
    }
    return parts.reverse().join('>');
  };
  const inMarquee = (n) => { const e = n.nodeType === 1 ? n : n.parentElement; return !!(e && e.closest('.marquee')); };

  // rendered text: visible text nodes in DOM order; marquee content collapsed to its period
  const out = [];
  const skipTag = new Set(['SCRIPT', 'STYLE', 'TEMPLATE', 'NOSCRIPT', 'HEAD', 'TITLE']);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = norm(n.textContent);
    if (!t) continue;
    const pe = n.parentElement;
    if (!pe || skipTag.has(pe.tagName) || inMarquee(n)) continue;
    if (!pe.checkVisibility({ checkVisibilityCSS: true })) continue;
    out.push(t);
  }
  const marquees = [];
  document.querySelectorAll('.marquee').forEach((m) => {
    const first = m.querySelector(':scope > div');
    const items = first ? [...first.children].map(c => norm(c.textContent)) : [];
    let period = items.length;
    for (let p = 1; p <= items.length; p++) {
      if (items.length % p) continue;
      let ok = true;
      for (let i = 0; i < items.length; i++) if (items[i] !== items[i % p]) { ok = false; break; }
      if (ok) { period = p; break; }
    }
    marquees.push(items.slice(0, period));
  });

  const outline = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
    .map(h => [h.tagName.toLowerCase(), norm(h.textContent)]);

  const ATTRS = ['href', 'src', 'srcset', 'action', 'xlink:href', 'poster', 'formaction', 'data'];
  const attrs = [];
  document.querySelectorAll('*').forEach((el) => {
    if (inMarquee(el) && el.closest('.marquee') !== el) return;
    for (const a of ATTRS) {
      if (el.hasAttribute(a)) {
        const v = el.getAttribute(a);
        attrs.push({ tag: el.tagName.toLowerCase(), attr: a, value: v,
                     rel: el.getAttribute('rel') || '', as: el.getAttribute('as') || '',
                     type: el.getAttribute('type') || '', path: pathOf(el) });
      }
    }
  });

  const controls = [...document.querySelectorAll('form,input,select,textarea,button,option,label')].map(el => ({
    tag: el.tagName.toLowerCase(), type: el.getAttribute('type') || '', name: el.getAttribute('name') || '',
    id: el.id || '', value: el.getAttribute('value') || '', for: el.getAttribute('for') || '',
    required: el.hasAttribute('required'), disabled: el.hasAttribute('disabled'),
    action: el.getAttribute('action') || '', method: el.getAttribute('method') || ''
  }));

  const metas = [...document.querySelectorAll('meta')].map(m => ({
    k: m.getAttribute('name') || m.getAttribute('property') || m.getAttribute('http-equiv') || (m.hasAttribute('charset') ? 'charset' : ''),
    v: m.getAttribute('content') || m.getAttribute('charset') || '' }));
  const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent);
  const head = {
    title: document.title, lang: document.documentElement.lang,
    canonical: (document.querySelector('link[rel="canonical"]') || {}).href || null,
    metas, ld,
  };

  // logo slots (selectors are configured in verify.py)
  const slots = [];
  for (const sel of cfg.slotSelectors) {
    document.querySelectorAll(sel).forEach((el) => {
      const r = el.getBoundingClientRect();
      const inner = el.matches('img,svg') ? el : el.querySelector('img,svg');
      const ir = inner ? inner.getBoundingClientRect() : { width: 0, height: 0 };
      slots.push({ sel, path: pathOf(el), tag: inner ? inner.tagName.toLowerCase() : null,
                   src: inner && inner.tagName === 'IMG' ? inner.getAttribute('src') : null,
                   box: [Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100],
                   inner: [Math.round(ir.width * 100) / 100, Math.round(ir.height * 100) / 100] });
    });
  }

  // overflow signatures: horizontal scroll, text that spills out of or is clipped by its box
  const docW = document.documentElement.clientWidth;
  const hscroll = document.documentElement.scrollWidth > docW + 1 || document.body.scrollWidth > docW + 1;
  const sig = (el) => pathOf(el);
  const overflow = [];
  document.querySelectorAll('body *').forEach((el) => {
    if (el.closest('.marquee') || el.closest('svg') || !el.checkVisibility()) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'inline' || cs.display === 'contents' || cs.position === 'fixed') return;
    if (!(el.innerText || '').trim()) return;
    const ox = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowX);
    const oy = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowY);
    if (el.scrollWidth > el.clientWidth + 1) overflow.push((ox ? 'clipped-x ' : 'spills-x ') + sig(el));
    // vertical: ignore the few px by which a glyph box exceeds a tight line-height; flag real overflow only
    const dy = el.scrollHeight - el.clientHeight;
    if (el.clientHeight > 0 && dy > Math.max(6, parseFloat(cs.fontSize) * 0.35)) overflow.push((oy ? 'clipped-y ' : 'spills-y ') + sig(el));
    const hasText = [...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim());
    if (hasText) {
      const range = document.createRange();
      range.selectNodeContents(el);
      let clipped = false;
      for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) {
        if (['hidden', 'clip'].includes(getComputedStyle(a).overflowX)) { clipped = true; break; }
      }
      if (!clipped) {
        for (const rc of range.getClientRects()) {
          if (rc.width > 0 && (rc.right > docW + 1 || rc.left < -1)) { overflow.push('beyond-viewport ' + sig(el)); break; }
        }
      }
    }
  });

  return { text: out, marquees, outline, attrs, controls, head, slots,
           hscroll, overflow: [...new Set(overflow)].sort(),
           docSize: [document.documentElement.scrollWidth, document.documentElement.scrollHeight] };
}
"""

# ---------------------------------------------------------------------------
# SCAN: palette, contrast and font checks for the current page state.
# ---------------------------------------------------------------------------
SCAN_JS = r"""
(cfg) => {
  const ICON_FONT = /font ?awesome|material (icons|symbols)|icomoon|iconify|bootstrap-icons|glyphicons|fontello|remixicon|boxicons|ionicons|themify|linearicons/i;
  const MONO_TAGS = new Set(['CODE', 'PRE', 'KBD', 'SAMP']);
  const NO_RENDER = new Set(['SCRIPT', 'STYLE', 'TEMPLATE', 'NOSCRIPT', 'HEAD', 'TITLE', 'META', 'LINK', 'BASE']);
  const REPLACED = new Set(['IMG', 'VIDEO', 'CANVAS', 'IFRAME', 'EMBED', 'OBJECT', 'PICTURE', 'SOURCE']);

  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const ctx = cv.getContext('2d', { willReadFrequently: true });
  const cache = new Map();
  function rgba(str) {
    if (cache.has(str)) return cache.get(str);
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#010203';
    ctx.fillStyle = str;
    let res = null;
    if (!(ctx.fillStyle === '#010203' && str.replace(/\s/g, '').toLowerCase() !== '#010203')) {
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      res = [d[0], d[1], d[2], d[3]];
    }
    cache.set(str, res);
    return res;
  }
  const near = (a, b, t = 1) => Math.abs(a - b) <= t;
  function classify(c) {
    if (!c) return 'invalid';
    const [r, g, b, a] = c;
    if (a === 0) return 'transparent';
    if (a === 255) {
      if (near(r, 0) && near(g, 0) && near(b, 0)) return 'black';
      if (near(r, 255) && near(g, 255) && near(b, 255)) return 'white';
      if (near(r, 0) && near(g, 199) && near(b, 197)) return 'teal';
      return 'other';
    }
    if (near(r, 0, 2) && near(g, 0, 2) && near(b, 0, 2)) return 'black-alpha';
    return 'translucent';
  }
  const COLOR_RE = /(?:rgba?|hsla?|hwb|oklab|oklch|lab|lch|color)\([^()]*\)|#[0-9a-fA-F]{3,8}\b/g;
  const colorsIn = (s) => (s.replace(/url\([^)]*\)/g, '').match(COLOR_RE) || []);

  const lum = ([r, g, b]) => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };

  const cssPath = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && e !== document.documentElement && parts.length < 6; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.id) s += '#' + e.id;
      else if (e.classList.length) s += '.' + [...e.classList].slice(0, 2).join('.');
      parts.push(s);
    }
    return parts.reverse().join(' > ');
  };

  // kit gradients (computed through a probe so any browser serialisation matches)
  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px';
  document.body.appendChild(probe);
  const kitGradients = new Set();
  for (const g of cfg.kitGradients) {
    probe.style.backgroundImage = g;
    const v = getComputedStyle(probe).backgroundImage;
    if (v && v !== 'none') kitGradients.add(v);
  }
  probe.remove();

  const viol = [];
  const add = (kind, el, detail, pseudo) => viol.push({ kind, sel: cssPath(el) + (pseudo || ''), detail });

  const PROPS = ['color', 'background-color', 'border-top-color', 'border-right-color', 'border-bottom-color',
    'border-left-color', 'outline-color', 'text-decoration-color', 'fill', 'stroke', '-webkit-text-fill-color',
    '-webkit-text-stroke-color', 'caret-color', 'column-rule-color', 'text-emphasis-color', 'stop-color',
    'flood-color', 'lighting-color', 'accent-color'];
  const IGNORE = new Set(['none', 'auto', 'currentcolor', 'normal', '']);

  function palette(el, pseudo) {
    const cs = getComputedStyle(el, pseudo || null);
    if (pseudo && (cs.content === 'none' || cs.content === 'normal')) return;
    if (cs.display === 'none') return;
    for (const p of PROPS) {
      let v = cs.getPropertyValue(p).trim();
      if (IGNORE.has(v) || v.startsWith('url(')) continue;
      const k = classify(rgba(v));
      if (k !== 'black' && k !== 'white' && k !== 'teal' && k !== 'transparent')
        add('palette', el, p + ': ' + v + ' [' + k + ']', pseudo);
    }
    for (const p of ['box-shadow', 'text-shadow']) {
      const v = cs.getPropertyValue(p);
      if (!v || v === 'none') continue;
      for (const c of colorsIn(v)) {
        const k = classify(rgba(c));
        if (!['black', 'white', 'teal', 'transparent', 'black-alpha'].includes(k))
          add('palette', el, p + ': ' + c + ' [' + k + ']', pseudo);
      }
    }
    const fl = cs.getPropertyValue('filter') + ' ' + cs.getPropertyValue('backdrop-filter');
    if (/drop-shadow/.test(fl)) for (const c of colorsIn(fl)) {
      const k = classify(rgba(c));
      if (!['black', 'white', 'teal', 'transparent', 'black-alpha'].includes(k)) add('palette', el, 'drop-shadow: ' + c + ' [' + k + ']', pseudo);
    }
    const bi = cs.getPropertyValue('background-image');
    if (bi && bi !== 'none' && /gradient\(/.test(bi) && !kitGradients.has(bi)) {
      for (const c of colorsIn(bi)) {
        const k = classify(rgba(c));
        if (!['black', 'white', 'teal', 'transparent'].includes(k)) add('palette', el, 'gradient stop: ' + c + ' [' + k + ']', pseudo);
      }
    }
    const op = parseFloat(cs.opacity);
    if (!pseudo && op > 0 && op < 1) add('palette', el, 'opacity: ' + cs.opacity);
  }

  // ---- surface model for contrast ------------------------------------------------
  function surfaceFor(P, stack, startIdx) {
    // layers from top to bottom until an opaque color is found
    const layers = [];
    let base = null;
    for (let i = startIdx; i < stack.length && !base; i++) {
      const E = stack[i];
      if (E.nodeType !== 1) continue;
      const cs = getComputedStyle(E);
      if (E.tagName === 'IMG' || E.tagName === 'VIDEO' || E.tagName === 'CANVAS') {
        const m = /brightness\(([\d.]+)(%?)\)/.exec(cs.filter || '');
        let b = 1; if (m) b = parseFloat(m[1]) / (m[2] ? 100 : 1);
        if (E !== P) layers.push({ k: 'photo', b });
        continue;
      }
      // inset black-alpha shadow paints over background-color and image
      const sh = cs.boxShadow;
      if (sh && sh !== 'none' && /inset/.test(sh)) {
        for (const part of sh.split(/,(?![^(]*\))/)) {
          if (!/inset/.test(part)) continue;
          const c = rgba((colorsIn(part)[0]) || 'transparent');
          if (c && c[3] > 0 && near(c[0], 0, 2) && near(c[1], 0, 2) && near(c[2], 0, 2)) layers.push({ k: 'overlay', a: c[3] / 255 });
        }
      }
      const bi = cs.backgroundImage;
      if (bi && bi !== 'none') {
        if (/url\(/.test(bi)) layers.push({ k: 'photo', b: 1 });
        else if (/gradient\(/.test(bi)) {
          const stops = colorsIn(bi).map(rgba).filter(c => c && c[3] > 0);
          if (stops.length) layers.push({ k: 'gradient', stops: stops.map(c => c.slice(0, 3)) });
        }
      }
      const bg = rgba(cs.backgroundColor);
      if (bg && bg[3] === 255) { base = bg.slice(0, 3); break; }
      if (bg && bg[3] > 0) layers.push({ k: 'translucent' });
    }
    if (!base) {
      const dark = (getComputedStyle(document.documentElement).colorScheme || '').includes('dark');
      base = dark ? [18, 18, 18] : [255, 255, 255];   // the browser's default canvas
    }
    let S = [base];
    for (let i = layers.length - 1; i >= 0; i--) {
      const L = layers[i];
      if (L.k === 'overlay') S = S.map(c => c.map(v => v * (1 - L.a)));
      else if (L.k === 'photo') S = S.concat([[0, 0, 0], [255, 255, 255]].map(c => c.map(v => v * L.b)));
      else if (L.k === 'gradient') S = L.stops;
      else if (L.k === 'translucent') S = S.concat([[0, 0, 0], [255, 255, 255]]);
    }
    return { S, layers, base };
  }

  function runs() {
    const res = [];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      if (!n.textContent.trim()) continue;
      const P = n.parentElement;
      if (!P || NO_RENDER.has(P.tagName) || P.closest('svg')) continue;
      if (!P.checkVisibility({ checkVisibilityCSS: true })) continue;
      if (cfg.scope && !cfg.scope.contains(n)) continue;
      res.push(n);
    }
    return res;
  }
  const usedWeights = new Set();

  function text(textNodes) {
    let sampled = 0, occluded = 0;
    for (const n of textNodes) {
      const P = n.parentElement;
      const cs = getComputedStyle(P);
      const fam = cs.fontFamily;
      const first = fam.split(',')[0].trim().replace(/^["']|["']$/g, '');
      const iconFont = ICON_FONT.test(fam);
      // fonts
      if (!iconFont) {
        const mono = MONO_TAGS.has(P.tagName) || !!P.closest('code,pre,kbd,samp');
        if (mono) { if (!/^ui-monospace/.test(fam.trim())) add('font', P, 'mono element family: ' + fam); }
        else if (first !== 'Arvo') add('font', P, 'family: ' + fam);
        const wt = cs.fontWeight;
        if (!mono) usedWeights.add(wt);
        if (wt !== '400' && wt !== '700') add('font', P, 'weight: ' + wt);
        if (cs.fontStyle !== 'normal') add('font', P, 'style: ' + cs.fontStyle);
        if (cs.fontSynthesisWeight !== 'none' || cs.fontSynthesisStyle !== 'none') add('font', P, 'font-synthesis: ' + cs.fontSynthesisWeight + '/' + cs.fontSynthesisStyle);
      }
      // contrast
      let fg = rgba(cs.color);
      const tf = cs.webkitTextFillColor;
      if (tf && tf !== cs.color) fg = rgba(tf);
      const fk = classify(fg);
      if (fk === 'transparent') { add('contrast', P, 'text fill transparent'); continue; }
      if (!['black', 'white', 'teal'].includes(fk)) { add('contrast', P, 'text color not in palette: ' + cs.color + ' [' + fk + ']'); continue; }
      const fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
      const need = (fs >= 24 || (fs >= 18.66 && bold)) ? 3 : 4.5;
      const range = document.createRange(); range.selectNodeContents(n);
      let rects = [...range.getClientRects()].filter(r => r.width > 1 && r.height > 1);
      for (let ri = 0; ri < rects.length; ri++) {
        // bring the rect into the middle of the viewport so hit-testing works
        let r = rects[ri];
        const cy = r.top + r.height / 2;
        if (cy < 4 || cy > innerHeight - 4 || r.left + r.width / 2 > innerWidth || r.right < 0) {
          window.scrollBy(0, cy - innerHeight / 2);
          range.selectNodeContents(n);
          rects = [...range.getClientRects()].filter(q => q.width > 1 && q.height > 1);
          r = rects[ri]; if (!r) break;
        }
        const x = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1);
        const y = Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1);
        if (x !== r.left + r.width / 2 && (r.left + r.width / 2 > innerWidth || r.right < 0)) { continue; }
        const stack = document.elementsFromPoint(x, y);
        let idx = stack.findIndex(e => e === P || P.contains(e));
        if (idx < 0) { occluded++; continue; }
        // anything above P that is not an ancestor of P or inside P hides the text
        let covered = false;
        for (let i = 0; i < idx; i++) if (!stack[i].contains(P) && !P.contains(stack[i])) { covered = true; break; }
        if (covered) { occluded++; continue; }
        const pi = stack.indexOf(P) >= 0 ? stack.indexOf(P) : idx;
        const surf = surfaceFor(P, stack, pi);
        sampled++;
        let worst = Infinity;
        for (const c of surf.S) worst = Math.min(worst, ratio(fg.slice(0, 3), c));
        if (worst < need) add('contrast', P, 'ratio ' + worst.toFixed(2) + ' < ' + need + ' (' + fk + ' text on ' + JSON.stringify(surf.S.slice(0, 4).map(c => c.map(Math.round))) + ')');
        else {
          const allBlack = surf.S.every(c => c[0] + c[1] + c[2] <= 3);
          const allWhite = surf.S.every(c => c.every(v => v >= 254));
          const allTeal = surf.S.every(c => near(c[0], 0) && near(c[1], 199) && near(c[2], 197));
          const dark = surf.S.every(c => lum(c) < 0.18);
          const ok = (fk === 'black' && (allWhite || allTeal || !dark)) ||
                     (fk === 'white' && dark) ||
                     (fk === 'teal' && allBlack);
          if (!ok || (fk === 'teal' && !allBlack) || (fk === 'white' && allTeal) ) add('contrast', P, fk + ' text on disallowed surface ' + JSON.stringify(surf.S.slice(0, 3).map(c => c.map(Math.round))));
        }
        break; // one sample per text node is enough once covered text found
      }
    }
    return { sampled, occluded };
  }

  const out = { viol: viol, stats: {} };
  if (cfg.palette) {
    let count = 0;
    document.querySelectorAll('*').forEach((el) => {
      if (NO_RENDER.has(el.tagName) || REPLACED.has(el.tagName)) return;
      if (el.closest('[data-gm-skip]')) return;
      count++;
      palette(el);
      if (el.tagName !== 'svg') { palette(el, '::before'); palette(el, '::after'); }
      if (el.tagName === 'LI') palette(el, '::marker');
    });
    out.stats.elements = count;
    const hb = rgba(getComputedStyle(document.documentElement).backgroundColor), bb = rgba(getComputedStyle(document.body).backgroundColor);
    if (hb && bb && hb[3] === 0 && bb[3] === 0) add('palette', document.documentElement, 'page canvas is the browser default (' + (getComputedStyle(document.documentElement).colorScheme.includes('dark') ? 'dark #121212' : 'white') + '), no explicit background');
  }
  if (cfg.text) {
    const sy = window.scrollY;
    const t = text(runs());
    window.scrollTo(0, sy);
    out.stats.textSampled = t.sampled; out.stats.textOccluded = t.occluded;
  }
  out.usedWeights = [...usedWeights];
  // loaded fonts
  out.fonts = [...document.fonts].map(f => ({ family: f.family.replace(/["']/g, ''), weight: f.weight, style: f.style, status: f.status }));
  return out;
}
"""

# ---------------------------------------------------------------------------
# list of interactive elements (selectors used to drive hover/active states)
# ---------------------------------------------------------------------------
INTERACTIVE_SEL = "a[href], button, input, select, textarea, summary, label[for], [tabindex], [role=button], [role=menuitem]"

# ============================================================================

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
WIDTHS = (360, 1280)
VIEW_H = 800

# ---- site-specific configuration (the only place that knows about this site) -----------
# Elements that hold a logo. Matched in the baseline and after, whatever they contain.
LOGO_SLOTS = {
    "*": ['#fullnav > a[href="/"]', 'footer a[aria-label="Main page"]'],
}
# Routes that are not rebranded (route -> reason). verify.py then only asserts they are unchanged (text,
# links, markup data, screenshot) and healthy, and skips the palette, contrast, font and logo checks.
# Empty now: the legacy page (/old/) that used to be here was deleted at the owner's request.
OUT_OF_SCOPE = {}
OUT_OF_SCOPE_PATHS = ()  # path prefixes (relative to dist/ or the site) skipped by the static font checks
# Files of the Ultro logo that must no longer be referenced.
BASELINE_LOGO_NAMES = ["ultro_dark", "ultro_small_dark", "UltroLogo6", "ultroblack", "ultrosmall"]
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "use.typekit.net", "fonts.bunny.net",
              "use.fontawesome.com", "kit.fontawesome.com", "fonts.adobe.com", "cdn.jsdelivr.net/npm/@fontsource")
ICON_FONT_NAME = re.compile(r"font-?awesome|material|icomoon|iconify|glyphicon|fontello", re.I)
# ---------------------------------------------------------------------------------------


def log(*a):
    print(*a, flush=True)


def slug(route):
    s = route.strip("/").replace("/", "-")
    return s or "index"


def norm_url(v):
    """Hashed build artefact names (/_astro/name.HASH.ext) compare by name only."""
    v = re.sub(r"(/_astro/[^?#]*?)\.[A-Za-z0-9_-]{8,}(\.[A-Za-z0-9]+)(?=$|[?#])", r"\1\2", v)
    return v


def sha(path_or_bytes):
    data = path_or_bytes if isinstance(path_or_bytes, bytes) else Path(path_or_bytes).read_bytes()
    return hashlib.sha256(data).hexdigest()


# ---- build and serve ------------------------------------------------------------------
def build_site(site):
    pkg = json.loads((site / "package.json").read_text())
    if "build" not in pkg.get("scripts", {}):
        log("no build script in package.json; serving the folder as is")
        return site
    if not (site / "node_modules").exists():
        cmd = ["deno", "install"] if shutil.which("deno") else ["npm", "install"]
        log("$", " ".join(cmd))
        subprocess.run(cmd, cwd=site, check=True)
    cmd = ["deno", "task", "build"] if shutil.which("deno") and (site / "deno.lock").exists() else ["npm", "run", "build"]
    log("$", " ".join(cmd))
    r = subprocess.run(cmd, cwd=site, capture_output=True, text=True)
    if r.returncode:
        log(r.stdout[-3000:], r.stderr[-3000:])
        sys.exit("build failed")
    return site / "dist"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(directory):
    handler = functools.partial(Quiet, directory=str(directory))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def discover_routes(site, dist):
    pages_dir = site / "src" / "pages"
    routes, endpoints = [], []
    for f in sorted(pages_dir.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(pages_dir)
        if any(p.startswith("_") for p in rel.parts) or "[" in f.name:
            continue
        if f.suffix in (".astro", ".html", ".md", ".mdx"):
            parts = list(rel.with_suffix("").parts)
            if parts[-1] == "index":
                parts = parts[:-1]
            routes.append("/" + "/".join(parts) + ("/" if parts else ""))
        elif f.suffix in (".ts", ".js"):
            endpoints.append("/" + "/".join(list(rel.parent.parts) + [f.stem]))
    for extra in ("sitemap-index.xml", "sitemap-0.xml"):
        if (dist / extra).exists():
            endpoints.append("/" + extra)
    return sorted(set(routes)), sorted(set(endpoints))


# ---- kit ------------------------------------------------------------------------------
def load_kit(kit):
    tokens = (kit / "tokens" / "tokens.css").read_text()
    grads = re.findall(r"--gm-gradient-on-(?:dark|light):\s*([^;]+);", tokens)
    names = {p.name for p in (kit / "logos" / "svg").glob("*.svg")} | {p.name for p in (kit / "logos" / "png").glob("*.png")}
    return {"gradients": grads, "logo_names": names}


# ---- page capture ---------------------------------------------------------------------
def slot_selectors(route):
    return LOGO_SLOTS.get("*", []) + LOGO_SLOTS.get(route, [])


def open_page(ctx, url):
    page = ctx.new_page()
    net = {"requests": [], "failed": [], "console": [], "pageerrors": [], "bad": []}
    page.on("request", lambda r: net["requests"].append(r.url))
    page.on("requestfailed", lambda r: net["failed"].append(f"{r.url} :: {r.failure}"))
    page.on("response", lambda r: net["bad"].append(f"{r.status} {r.url}") if r.status >= 400 else None)
    page.on("console", lambda m: net["console"].append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: net["pageerrors"].append(str(e)))
    resp = page.goto(url, wait_until="load")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    page.evaluate("document.fonts.ready.then(() => true)")
    page.wait_for_timeout(250)
    return page, resp, net


def norm_net(net, origin):
    def n(u):
        if u.startswith(origin):
            return norm_url(u[len(origin):])
        return re.sub(r"[?#].*$", "", u)
    return {
        "requests": sorted({n(u) for u in net["requests"] if not u.startswith("data:")}),
        "failed": sorted({n(f.split(" :: ")[0]) + " :: " + f.split(" :: ")[1] for f in net["failed"]}),
        "console": sorted(set(net["console"])),
        "pageerrors": sorted(set(net["pageerrors"])),
        "bad": sorted({b.split(" ", 1)[0] + " " + n(b.split(" ", 1)[1]) for b in net["bad"]}),
    }


def capture(browser, base, route, width, shot_path):
    ctx = browser.new_context(viewport={"width": width, "height": VIEW_H}, device_scale_factor=1)
    page, resp, net = open_page(ctx, base + route)
    data = page.evaluate(COLLECT_JS, {"slotSelectors": slot_selectors(route)})
    data["status"] = resp.status if resp else None
    data["net"] = norm_net(net, base)
    data["net_raw"] = net
    page.screenshot(path=str(shot_path), full_page=True, animations="disabled")
    return ctx, page, data


# ---- scans ----------------------------------------------------------------------------
FREEZE_CSS = "*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}"
REVEAL_JS = """(el) => {
  const vis = e => e.checkVisibility({visibilityProperty: true, opacityProperty: true}) && e.getBoundingClientRect().width > 0;
  if (vis(el)) return 'visible';
  for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
    for (const f of a.querySelectorAll('[tabindex]:not([tabindex="-1"]), a[href], button')) {
      if (f === el || el.contains(f) || f.contains(el) || !vis(f)) continue;
      f.focus();
      if (vis(el)) return 'revealed';
    }
  }
  return 'hidden';
}"""
CENTER_JS = """(el) => { el.scrollIntoView({block: 'center', inline: 'center'}); const r = el.getBoundingClientRect();
  const x = r.left + r.width / 2, y = r.top + r.height / 2; const t = document.elementFromPoint(x, y);
  return {x, y, hit: !!t && (el === t || el.contains(t) || t.contains(el))}; }"""
SCOPE_JS = "(el) => el.closest('li, .dropdown, nav, footer, a, button') || el"


def scan(page, kit, scope=None, state="default", palette=True):
    cfg = {"palette": palette, "text": True, "kitGradients": kit["gradients"]}
    if scope is not None:
        cfg["scope"] = scope
    r = page.evaluate(SCAN_JS, cfg)
    for v in r["viol"]:
        v["state"] = state
    return r


def scan_page(page, kit, quick):
    """Default state plus hover, active and keyboard-focus on every interactive element."""
    page.add_style_tag(content=FREEZE_CSS)
    page.evaluate("window.scrollTo(0, 0)")
    res = scan(page, kit)
    viol = list(res["viol"])
    fonts = res["fonts"]
    used_weights = res.get("usedWeights", [])
    stats = {"default": res["stats"], "states": 0}
    if not quick:
        els = page.query_selector_all(INTERACTIVE_SEL)
        for el in els:
            try:
                status = page.evaluate(REVEAL_JS, el)
                if status == "hidden":
                    continue
                c = page.evaluate(CENTER_JS, el)
                if not c["hit"]:
                    continue
                scope = page.evaluate_handle(SCOPE_JS, el)
                page.mouse.move(c["x"], c["y"])
                viol += scan(page, kit, scope, "hover")["viol"]
                page.mouse.down()
                viol += scan(page, kit, scope, "active")["viol"]
                page.mouse.move(0, 0)
                page.mouse.up()
                stats["states"] += 2
                page.evaluate("document.activeElement && document.activeElement.blur()")
                page.evaluate("window.scrollTo(0, 0)")
            except Exception as e:  # keep going; report at the end
                viol.append({"kind": "harness", "sel": "?", "detail": f"state scan error: {e}", "state": "?"})
        # slide / tab style pages: show every radio-driven panel and scan it
        radios = page.query_selector_all("input[type=radio]")
        for r in radios:
            try:
                rid = r.get_attribute("id")
                lab = page.query_selector(f'label[for="{rid}"]') if rid else None
                if lab is None or r.is_checked():
                    continue
                lab.click()
                page.wait_for_timeout(50)
                viol += scan(page, kit, None, f"panel:{rid}")["viol"]
                stats["states"] += 1
            except Exception as e:
                viol.append({"kind": "harness", "sel": "?", "detail": f"panel scan error: {e}", "state": "?"})
        if radios:
            first = radios[0].get_attribute("id")
            page.evaluate("(id) => { const r = document.getElementById(id); if (r) r.click(); }", first)
        # real keyboard focus (:focus-visible) through the tab order
        page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
        seen = set()
        for _ in range(60):
            page.keyboard.press("Tab")
            info = page.evaluate("(() => { const e = document.activeElement; return e && e !== document.body ? "
                                 "[e.tagName + (e.id ? '#' + e.id : '') + ':' + [...(e.parentElement ? e.parentElement.children : [])].indexOf(e) + ':' + (e.getAttribute('href') || ''), "
                                 "e.matches(':focus-visible')] : null; })()")
            if not info or info[0] in seen:
                break
            seen.add(info[0])
            scope = page.evaluate_handle("(() => { const el = document.activeElement; return el.closest('li, .dropdown, nav, footer, a, button') || el; })()")
            viol += scan(page, kit, scope, "focus")["viol"]
            stats["states"] += 1
    # dedupe
    seen, out = set(), []
    for v in viol:
        k = (v["kind"], v["sel"], v["detail"])
        if k in seen:
            continue
        seen.add(k)
        out.append(v)
    return out, fonts, used_weights, stats


# ---- comparisons ----------------------------------------------------------------------
def is_font_host(url):
    return any(h in url for h in FONT_HOSTS)


def attr_key(e):
    return (e["tag"], e["attr"], norm_url(e["value"]))


def filter_attrs(entries, side, kit_names):
    """Drop the edits this pass is allowed to make; return (kept, logo_count)."""
    kept, logos = [], 0
    for e in entries:
        v, rel = e["value"], e["rel"].lower()
        if e["tag"] == "link" and any(x in rel for x in ("icon", "apple-touch", "manifest", "preload", "prefetch")):
            continue
        if is_font_host(v):
            continue
        if e["tag"] == "img" and e["attr"] in ("src", "srcset"):
            base = re.sub(r"[?#].*$", "", v.split()[0] if v.strip() else v).rsplit("/", 1)[-1]
            if side == "before" and any(n in v for n in BASELINE_LOGO_NAMES):
                logos += 1
                continue
            if side == "after" and base in kit_names:
                logos += 1
                continue
        kept.append(e)
    return kept, logos


def compare_unchanged(base, after, kit_names, strict=False):
    """strict: nothing may differ at all (out-of-scope pages); otherwise the edits this pass allows are exempt."""
    msgs = []
    if base["text"] != after["text"]:
        a, b = base["text"], after["text"]
        for i in range(max(len(a), len(b))):
            x, y = (a[i] if i < len(a) else "<none>"), (b[i] if i < len(b) else "<none>")
            if x != y:
                msgs.append(f"text[{i}] baseline={x!r} after={y!r}")
                break
        msgs.append(f"text differs ({len(a)} vs {len(b)} runs)")
    if base["marquees"] != after["marquees"]:
        msgs.append(f"marquee text differs: {base['marquees']} vs {after['marquees']}")
    if base["outline"] != after["outline"]:
        msgs.append(f"heading outline differs: {base['outline']} vs {after['outline']}")
    if strict:
        bk, bl, ak, al = base["attrs"], 0, after["attrs"], 0
    else:
        bk, bl = filter_attrs(base["attrs"], "before", kit_names)
        ak, al = filter_attrs(after["attrs"], "after", kit_names)
    bkeys, akeys = [attr_key(e) for e in bk], [attr_key(e) for e in ak]
    if bkeys != akeys:
        miss = [k for k in bkeys if k not in akeys]
        extra = [k for k in akeys if k not in bkeys]
        msgs.append(f"href/src/srcset/action differ: missing={miss[:5]} extra={extra[:5]}")
    if not strict and al != len(base["slots"]):
        msgs.append(f"{al} kit logo images in page, baseline had {len(base['slots'])} logo slots")
    if base["controls"] != after["controls"]:
        msgs.append("form fields differ")
    bh, ah = dict(base["head"]), dict(after["head"])
    bm = [m for m in bh["metas"] if strict or m["k"] != "theme-color"]
    am = [m for m in ah["metas"] if strict or m["k"] != "theme-color"]
    if bm != am or bh["title"] != ah["title"] or bh["canonical"] != ah["canonical"] or bh["ld"] != ah["ld"] or bh["lang"] != ah["lang"]:
        msgs.append("head metadata (title, meta, canonical, JSON-LD) differs")
    return msgs


def pixel_diff(a_bytes, b_bytes):
    a = Image.open(io.BytesIO(a_bytes)).convert("RGBA")
    b = Image.open(io.BytesIO(b_bytes)).convert("RGBA")
    if a.size != b.size:
        return 255.0
    mean = ImageStat.Stat(ImageChops.difference(a, b)).mean
    return sum(mean) / len(mean)


class Renderer:
    """Renders an image file in Chrome so SVG files can be compared by pixels."""

    def __init__(self, browser):
        self.page = browser.new_context(viewport={"width": 600, "height": 600}).new_page()

    def render(self, data, mime, width, height=None):
        b64 = base64.b64encode(data).decode()
        h = f"{height}px" if height else "auto"
        self.page.set_content(f'<body style="margin:0;background:#808080"><img id="i" src="data:{mime};base64,{b64}" '
                              f'style="width:{width}px;height:{h};display:block"></body>')
        self.page.wait_for_function("document.getElementById('i').complete")
        return self.page.locator("#i").screenshot(omit_background=False)


def health(name, data, bl):
    msgs = []
    if data["status"] != 200:
        msgs.append(f"{name}: HTTP {data['status']}")
    for k, label in (("failed", "failed request"), ("console", "console error"), ("pageerrors", "page error"), ("bad", "HTTP error")):
        msgs += [f"{name}: new {label}: {x}" for x in data["net"][k] if x not in bl["net"][k]]
    if data["hscroll"] and not bl["hscroll"]:
        msgs.append(f"{name}: horizontal scroll (baseline had none)")
    msgs += [f"{name}: new overflow: {o}" for o in data["overflow"] if o not in bl["overflow"]]
    return msgs


def mime_of(p):
    return {".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}.get(Path(p).suffix, "application/octet-stream")


def static_font_checks(site, dist, kit_dir):
    """Source and build output: no font other than Arvo (icon fonts excepted), no font hosts, Arvo files equal the kit's."""
    msgs = []
    for css in list(dist.rglob("*.css")):
        text = css.read_text(errors="ignore")
        rel = css.relative_to(dist)
        if str(rel).startswith(OUT_OF_SCOPE_PATHS):
            continue
        for m in re.finditer(r"@font-face\s*\{([^}]*)\}", text):
            fam = re.search(r"font-family:\s*[\"']?([^;\"'}]+)", m.group(1))
            name = fam.group(1).strip() if fam else "?"
            if name != "Arvo" and not ICON_FONT_NAME.search(name):
                msgs.append(f"dist/{rel}: @font-face for {name}")
        for imp in re.findall(r"@import\s+(?:url\()?[\"']?([^\"')\s;]+)", text):
            if is_font_host(imp) or "font" in imp.lower():
                msgs.append(f"dist/{rel}: @import {imp}")
    for html in dist.rglob("*.html"):
        if str(html.relative_to(dist)).startswith(OUT_OF_SCOPE_PATHS):
            continue
        t = html.read_text(errors="ignore")
        for h in FONT_HOSTS:
            if h in t:
                msgs.append(f"dist/{html.relative_to(dist)}: references {h}")
    for src in list((site / "src").rglob("*")) + list((site / "public").rglob("*.css")) + list((site / "public").rglob("*.html")):
        if str(src.relative_to(site)).startswith(OUT_OF_SCOPE_PATHS):
            continue
        if src.is_file() and src.suffix in (".astro", ".css", ".html", ".ts", ".js", ".tsx", ".jsx", ".mjs"):
            t = src.read_text(errors="ignore")
            for needle in FONT_HOSTS + ("@fontsource",):
                if needle in t:
                    msgs.append(f"{src.relative_to(site)}: mentions {needle}")
    fonts = [p for p in dist.rglob("*") if p.suffix.lower() in (".woff", ".woff2", ".ttf", ".otf", ".eot")
             and not str(p.relative_to(dist)).startswith(OUT_OF_SCOPE_PATHS)]
    for p in fonts:
        if not p.name.startswith("Arvo-") and not ICON_FONT_NAME.search(p.name):
            msgs.append(f"dist/{p.relative_to(dist)}: font file that is not Arvo")
    for fn in ("Arvo-Regular.woff2", "Arvo-Bold.woff2", "OFL.txt"):
        cands = [p for p in dist.rglob(fn)]
        if not cands:
            msgs.append(f"{fn} missing from dist")
        elif sha(cands[0]) != sha(kit_dir / "fonts" / fn):
            msgs.append(f"{fn} differs from the kit's file")
    if len({p.parent for p in dist.rglob("Arvo-*.woff2")} | {p.parent for p in dist.rglob("OFL.txt")}) > 1:
        msgs.append("OFL.txt is not next to the Arvo font files")
    return msgs


# ---- main -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", action="store_true", help="capture the baseline instead of checking")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--quick", action="store_true", help="skip hover/focus/active scans")
    ap.add_argument("--only", help="comma separated routes to run, e.g. /,/about/")
    ap.add_argument("--site", default=str(SITE))
    ap.add_argument("--kit", default=str(SITE / "GEMINII_Brandkit"))
    ap.add_argument("--shots-dir", help="where to write screenshots (default rebrand/screenshots/before|after)")
    args = ap.parse_args()
    site, kit_dir = Path(args.site).resolve(), Path(args.kit).resolve()
    base_dir = HERE / "baseline"
    shots = Path(args.shots_dir) if args.shots_dir else HERE / "screenshots" / ("before" if args.baseline else "after")
    shots.mkdir(parents=True, exist_ok=True)
    base_dir.mkdir(exist_ok=True)

    dist = (site / "dist") if args.no_build else build_site(site)
    routes, endpoints = discover_routes(site, dist)
    if args.only:
        wanted = set(args.only.split(","))
        routes = [r for r in routes if r in wanted]
    missing = [r for r in routes if not (dist / r.strip("/") / "index.html").exists()]
    if missing:
        sys.exit(f"routes without built output: {missing}")
    kit = load_kit(kit_dir)
    httpd, base = serve(dist)
    log(f"serving {dist} at {base}\npages: {routes}\nendpoints: {endpoints}")

    results = {"a": [], "b": [], "c": [], "d": [], "e": [], "f": []}
    t0 = time.time()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)
        log("browser:", browser.version)

        if args.baseline:
            meta = {"route_list": routes, "endpoints": endpoints, "browser": browser.version,
                    "captured": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=SITE, capture_output=True, text=True).stdout.strip(),
                    "site_captured_from": str(site)}
            for route in routes:
                for w in WIDTHS:
                    name = f"{slug(route)}-{w}"
                    ctx, page, data = capture(browser, base, route, w, shots / f"{name}.png")
                    data.pop("net_raw")
                    data["route"], data["width"] = route, w
                    (base_dir / f"{name}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
                    log(f"baseline {name}: status={data['status']} text={len(data['text'])} attrs={len(data['attrs'])} slots={len(data['slots'])}")
                    ctx.close()
            for ep in endpoints:
                import urllib.request
                try:
                    with urllib.request.urlopen(base + ep) as r:
                        meta.setdefault("endpoint_status", {})[ep] = r.status
                except Exception as e:
                    meta.setdefault("endpoint_status", {})[ep] = str(e)
            (base_dir / "meta.json").write_text(json.dumps(meta, indent=1))
            log("baseline written to", base_dir)
            browser.close()
            httpd.shutdown()
            return 0

        # ---------- checks ----------
        results["d"] += static_font_checks(site, dist, kit_dir)
        rend = Renderer(browser)
        kit_logo_render = {}
        fonts_loaded_anywhere = {"400": False, "700": False}
        all_font_reqs = set()
        for route in routes:
            for w in WIDTHS:
                name = f"{slug(route)}-{w}"
                bpath = base_dir / f"{name}.json"
                if not bpath.exists():
                    results["a"].append(f"{name}: no baseline captured")
                    continue
                bl = json.loads(bpath.read_text())
                ctx, page, data = capture(browser, base, route, w, shots / f"{name}.png")
                if route in OUT_OF_SCOPE:
                    log(f"{name}: out of scope ({OUT_OF_SCOPE[route]}), must be unchanged ...")
                    results["a"] += [f"{name}: {m}" for m in compare_unchanged(bl, data, kit["logo_names"], strict=True)]
                    before = HERE / "screenshots" / "before" / f"{name}.png"
                    if before.exists():
                        d = pixel_diff(before.read_bytes(), (shots / f"{name}.png").read_bytes())
                        if d > 0.5:
                            results["a"].append(f"{name}: screenshot differs from the baseline (mean pixel diff {d:.2f}); this page must stay as it was")
                    results["f"] += health(name, data, bl)
                    ctx.close()
                    continue
                log(f"{name}: scanning ...")
                viol, fonts, used_weights, stats = scan_page(page, kit, args.quick)
                raw = data["net_raw"]

                # a: unchanged
                results["a"] += [f"{name}: {m}" for m in compare_unchanged(bl, data, kit["logo_names"])]

                # b, c, d from the scans
                for v in viol:
                    tag = {"palette": "b", "contrast": "c", "font": "d", "harness": "f"}[v["kind"]]
                    results[tag].append(f"{name} [{v['state']}] {v['sel']}: {v['detail']}")

                # d: Arvo loaded from site files, no font hosts
                arvo = [f for f in fonts if f["family"] == "Arvo"]
                for wt in used_weights:
                    if not any(f["weight"] == str(wt) and f["status"] == "loaded" for f in arvo):
                        results["d"].append(f"{name}: Arvo {wt} is used on the page but not loaded")
                for f in arvo:
                    if f["status"] == "loaded":
                        fonts_loaded_anywhere[f["weight"]] = True
                reqs = raw["requests"]
                for u in reqs:
                    if is_font_host(u):
                        results["d"].append(f"{name}: request to a font host: {u}")
                    if re.search(r"\.(woff2?|ttf|otf|eot)(\?|$)", u):
                        all_font_reqs.add(urlparse(u).path)
                        if not u.startswith(base) and not ICON_FONT_NAME.search(u):
                            results["d"].append(f"{name}: font file from outside the site: {u}")
                        elif u.startswith(base) and "Arvo" not in u and not ICON_FONT_NAME.search(u):
                            results["d"].append(f"{name}: non-Arvo font file requested: {u}")

                # e: logos
                for s in data["slots"]:
                    if s["tag"] != "img" or not s["src"]:
                        results["e"].append(f"{name}: slot {s['sel']} renders {s['tag']} (src={s['src']}), not a kit logo image")
                        continue
                    fname = re.sub(r"[?#].*$", "", norm_url(s["src"])).rsplit("/", 1)[-1]
                    if fname not in kit["logo_names"]:
                        results["e"].append(f"{name}: slot {s['sel']} src {s['src']} is not a kit logo file")
                        continue
                    key = (s["src"], fname)
                    if key not in kit_logo_render:
                        served = (dist / s["src"].lstrip("/")) if s["src"].startswith("/") else (dist / route.strip("/") / s["src"])
                        kit_file = kit_dir / "logos" / ("svg" if fname.endswith(".svg") else "png") / fname
                        if not served.exists():
                            kit_logo_render[key] = f"{s['src']} not found in dist"
                        elif sha(served) == sha(kit_file):
                            kit_logo_render[key] = None
                        else:
                            d = pixel_diff(rend.render(served.read_bytes(), mime_of(fname), 400),
                                           rend.render(kit_file.read_bytes(), mime_of(fname), 400))
                            kit_logo_render[key] = None if d < 1.0 else f"{s['src']} differs from kit {fname} (mean pixel diff {d:.2f})"
                    if kit_logo_render[key]:
                        results["e"].append(f"{name}: {kit_logo_render[key]}")
                    ratio_ok = True
                    iw, ih = s["inner"]
                    if ih and abs(iw / ih - (2000 / 565 if "wordmark" in fname else 2000 / 1896 if fname.startswith("icon") else iw / ih)) > 0.02 * max(iw / ih, 1):
                        ratio_ok = False
                    if not ratio_ok:
                        results["e"].append(f"{name}: logo {fname} rendered {iw}x{ih}, aspect ratio is not the kit's")
                    bw, bh_ = s["box"]
                    if "wordmark" in fname and iw < 160:
                        results["e"].append(f"{name}: wordmark rendered {iw}px wide (< 160 px minimum), use the icon")
                for u in reqs:
                    if any(n in u for n in BASELINE_LOGO_NAMES):
                        results["e"].append(f"{name}: request for baseline Ultro logo file {u}")
                bg_refs = page.evaluate("""(names) => { const out = [];
                  document.querySelectorAll('*').forEach(el => { for (const ps of [null, '::before', '::after']) {
                    const bi = getComputedStyle(el, ps).backgroundImage; if (bi && names.some(n => bi.includes(n))) out.push(bi); } });
                  document.querySelectorAll('img[src],source[srcset],img[srcset],link[href]').forEach(el => { const v = (el.getAttribute('src') || el.getAttribute('srcset') || el.getAttribute('href') || '');
                    if (names.some(n => v.includes(n))) out.push(v); });
                  return out; }""", BASELINE_LOGO_NAMES)
                results["e"] += [f"{name}: baseline logo referenced: {b[:120]}" for b in bg_refs]

                # f: health
                results["f"] += health(name, data, bl)
                ctx.close()

        # e: fixed-path icon files and og:image
        checks = [("favicon.ico", kit_dir / "favicons/favicon.ico"), ("apple-touch-icon.png", kit_dir / "favicons/apple-touch-icon.png")]
        for fn, kf in checks:
            if not (dist / fn).exists():
                results["e"].append(f"/{fn} missing")
            elif sha(dist / fn) != sha(kf):
                results["e"].append(f"/{fn} differs from the kit file {kf.name}")
        if (dist / "favicon.svg").exists():
            d = pixel_diff(rend.render((dist / "favicon.svg").read_bytes(), "image/svg+xml", 96),
                           rend.render((kit_dir / "favicons/favicon.svg").read_bytes(), "image/svg+xml", 96))
            if d >= 1.0:
                results["e"].append(f"/favicon.svg does not render like the kit favicon.svg (pixel diff {d:.2f})")
        if (dist / "favicon-96x96.png").exists():
            png = (dist / "favicon-96x96.png").read_bytes()
            if Image.open(io.BytesIO(png)).size != (96, 96):
                results["e"].append("/favicon-96x96.png is not 96x96")
            else:
                kit_svg_96 = rend.render((kit_dir / "favicons/favicon.svg").read_bytes(), "image/svg+xml", 96, 96)
                if pixel_diff(png, kit_svg_96) >= 8.0:  # the PNG is rasterised on transparency; the reference sits on grey
                    ref = Image.open(io.BytesIO(png)).convert("RGBA")
                    bg = Image.new("RGBA", ref.size, (128, 128, 128, 255))
                    bg.alpha_composite(ref)
                    out = io.BytesIO(); bg.save(out, "PNG")
                    if pixel_diff(out.getvalue(), kit_svg_96) >= 2.0:
                        results["e"].append("/favicon-96x96.png is not the kit favicon.svg rasterised")
        for page_html in [dist / r.strip("/") / "index.html" for r in routes if r not in OUT_OF_SCOPE]:
            html = page_html.read_text(errors="ignore")
            m = re.search(r'<meta[^>]+property=["\']?og:image["\']?[^>]*content=["\']?([^"\' >]+)', html)
            if m:
                tail = urlparse(m.group(1)).path
                f = dist / tail.lstrip("/")
                if not f.exists() or sha(f) != sha(kit_dir / "social/og-image.png"):
                    results["e"].append(f"{page_html.parent.name or 'index'}: og:image {m.group(1)} is not the kit og-image.png")
        # d: both weights loaded somewhere
        for wt, ok in fonts_loaded_anywhere.items():
            if not ok:
                results["d"].append(f"Arvo {wt} never loaded on any page")
        # f: endpoints
        import urllib.request
        for ep in endpoints:
            try:
                with urllib.request.urlopen(base + ep) as r:
                    if r.status != 200:
                        results["f"].append(f"{ep}: HTTP {r.status}")
            except Exception as e:
                results["f"].append(f"{ep}: {e}")
        browser.close()
    httpd.shutdown()

    # ---------- report ----------
    titles = {"a": "unchanged text / outline / links / fields", "b": "palette", "c": "contrast (WCAG AA)",
              "d": "fonts", "e": "logos and icons", "f": "health"}
    failed = 0
    log("\n" + "=" * 72)
    for k in "abcdef":
        msgs = sorted(set(results[k]))
        status = "PASS" if not msgs else "FAIL"
        failed += bool(msgs)
        log(f"[{k}] {titles[k]:<42} {status}" + (f" ({len(msgs)})" if msgs else ""))
        for m in msgs[:40]:
            log("     -", m)
        if len(msgs) > 40:
            log(f"     ... {len(msgs) - 40} more (see rebrand/verify-report.json)")
    log("=" * 72)
    log(f"pages: {len(routes)} x widths {list(WIDTHS)}; endpoints: {len(endpoints)}; {time.time() - t0:.0f}s; "
        + ("ALL CHECKS PASS" if not failed else f"{failed} check group(s) failing"))
    (HERE / "verify-report.json").write_text(json.dumps({k: sorted(set(v)) for k, v in results.items()}, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
