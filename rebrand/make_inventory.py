#!/usr/bin/env python3
"""Builds rebrand/INVENTORY.md: every place that carries the Ultro name, a link, a contact, a
description or other copy that the later text-and-links pass has to rewrite.

Rows are `file:line | kind | exact value | location`, one per occurrence. Nothing is edited here.
Edits made in pass 1 (swapped logo alt text, new Arvo/brand files) are not listed; selectors and
variables that still carry an Ultro identifier are listed because a later rename must follow them.
This folder (rebrand/) is excluded from deployment.
"""
import re
import subprocess
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "rebrand" / "INVENTORY.md"
SKIP_DIRS = {".git", "node_modules", "dist", ".astro", "rebrand", "GEMINII_Brandkit"}
TEXT_EXT = {".astro", ".html", ".css", ".ts", ".js", ".json", ".md", ".yml", ".yaml", ".svg", ".txt", ".mjs"}
SKIP_FILES = {"deno.lock", "LICENSE", "LICENSE-CC-BY-SA-4.0"}
SKIP_PREFIXES = ("public/assets/", "public/favicon", "public/apple-touch-icon")  # files written or overwritten in pass 1
GENERIC_HOSTS = ("w3.org", "schema.org", "astro.build", "daisyui.com", "tailwindcss.com", "PlayForm", "inkscape.org",
                 "sodipodi", "boxy-svg", "sil.org", "docs.astro.build")

rows = []  # (file, line, kind, value, location)


def add(f, ln, kind, value, location):
    rows.append((f, ln, kind, value.strip(), location))


def files():
    for p in sorted(SITE.rglob("*")):
        rel = p.relative_to(SITE)
        if not p.is_file() or any(part in SKIP_DIRS for part in rel.parts) or p.name in SKIP_FILES:
            continue
        if str(rel).startswith(SKIP_PREFIXES):
            continue
        yield rel, p


URL_RE = re.compile(r"""(?:https?://[^\s"'<>)`\\]+|mailto:[^\s"'<>)`\\]+)""")
HREF_RE = re.compile(r"""href\s*[=:]\s*\{?\\?["'`]([^"'`\\]+)\\?["'`]""")
ULTRO_RE = re.compile(r"[A-Za-z0-9_:\-\\/.@~]*[uU][lL][tT][rR][oO][A-Za-z0-9_\-\\/.@]*")

LOCATIONS = {
    "src/components/NavigationBar.astro": "header navigation",
    "src/components/Footer.astro": "site footer",
    "src/components/Socials.astro": "floating social links",
    "src/components/Link.astro": "inline link component",
    "src/components/Button.astro": "button component",
    "src/layouts/MainLayout.astro": "page title template",
    "src/layouts/BaseLayout.astro": "document head",
    "src/pages/index.astro": "home page (/)",
    "src/pages/about.astro": "about page (/about/)",
    "src/pages/outreach.astro": "outreach page (/outreach/)",
    "src/pages/ex-nihilo.astro": "ex nihilo page (/ex-nihilo/)",
    "src/pages/resources.astro": "resources page (/resources/)",
    "src/pages/robots.astro": "robots page (/robots/)",
    "src/pages/robots.txt.ts": "robots.txt endpoint",
    "src/pages/old/index.html": "legacy page (/old/)",
    "src/styles/global.css": "global stylesheet",
    "astro.config.ts": "Astro config",
    ".github/workflows/deploy.yml": "deploy workflow",
    "README.md": "README",
}


def loc(rel, line_text):
    base = LOCATIONS.get(str(rel), str(rel))
    ctx = ""
    if "<title" in line_text or re.search(r'\btitle="(?!GEMINII)', line_text):
        ctx = ", title"
    if "<Card" in line_text:
        ctx = ", card title"
    return base + ctx


def classify_url(url):
    if url.startswith("mailto:"):
        return "email"
    if "docs.google.com/forms" in url:
        return "form-endpoint"
    if re.search(r"(youtube\.com/@|instagram\.com/|github\.com/BrowningUltro-10539/?$)", url):
        return "social-handle"
    return "link"


def scan_file(rel, p):
    srel = str(rel)
    suffix = p.suffix
    # file names carrying the name
    if re.search(r"ultro", p.name, re.I):
        add(srel, 1, "ultro-name-in-identifier", p.name, "file name" + (" (logo file, unreferenced after the logo swap)" if p.suffix in (".svg", ".png") else ""))
    if suffix not in TEXT_EXT:
        return
    lines = p.read_text(errors="ignore").splitlines()
    in_jsonld = False
    for i, line in enumerate(lines, 1):
        masked = line
        # JSON-LD data block in the home page
        if srel == "src/pages/index.astro" and re.match(r"const structuredData", line):
            in_jsonld = True
        if in_jsonld:
            if line.strip().startswith("}"):
                in_jsonld = False
            elif re.search(r"ultro|url:|name:|alternateName", line, re.I):
                add(srel, i, "json-ld", line.strip().rstrip(","), "JSON-LD WebSite block on the home page")
                continue
        # robots / sitemap
        if srel == "src/pages/robots.txt.ts" and re.search(r"^(Sitemap:|User-agent:|Allow:|# Hey)", line):
            add(srel, i, "sitemap-or-robots-entry", line.strip(), "robots.txt template")
            continue
        if srel == "astro.config.ts":
            if "site:" in line:
                add(srel, i, "canonical-or-og-url", re.search(r'"([^"]+)"', line).group(1), "Astro `site`, base of canonical, sitemap and JSON-LD URLs")
                continue
            if re.search(r"sitemap\(\)", line):
                add(srel, i, "sitemap-or-robots-entry", line.strip(), "sitemap integration")
                continue
        # meta descriptions
        m = re.search(r'\bdescription=(?:"([^"]*)"|\{([^}]*)\})', line)
        if m and srel.startswith("src/") and m.group(1) is not None:
            add(srel, i, "meta-description", m.group(1), loc(rel, line))
            continue
        # urls and links
        spans = []
        for u in URL_RE.finditer(line):
            url = u.group(0).rstrip(".,;")
            if srel == ".github/workflows/deploy.yml":
                continue
            spans.append(u.span())
            if any(h in url for h in GENERIC_HOSTS):
                continue
            kind = classify_url(url)
            if srel == "README.md":
                kind = "link"
            add(srel, i, kind, url, loc(rel, line))
        for h in HREF_RE.finditer(line):
            v = h.group(1)
            if v.startswith(("http", "mailto:", "#")) or v == "":
                continue
            if re.search(r"\.(png|ico|svg|woff2?|css|js)$", v):
                continue  # asset references, not site links
            add(srel, i, "link", v, loc(rel, line))
        if srel == "README.md":
            for mm in re.finditer(r"\]\((/[^)]+)\)", line):
                add(srel, i, "link", mm.group(1), "README link")
        for sp in reversed(spans):
            masked = masked[:sp[0]] + " " * (sp[1] - sp[0]) + masked[sp[1]:]
        # ultro tokens
        for t in ULTRO_RE.finditer(masked):
            tok = t.group(0)
            kind = None
            if re.search(r"[-_.\\/@:]", tok.strip(".")) and not re.fullmatch(r"[Uu]ltro[.,:;!?]?", tok):
                kind = "ultro-name-in-identifier"
                value = tok
            elif re.search(r'(aria-label|alt|title|content)="[^"]*ultro', line, re.I) and srel.startswith("src/"):
                kind, value = "ultro-name-in-attribute", re.search(r'(aria-label|alt|title|content)="[^"]*ultro[^"]*"', line, re.I).group(0)
            else:
                kind, value = "ultro-name-in-text", line.strip()
            if srel == ".github/workflows/deploy.yml":
                kind, value = "ultro-name-in-identifier", "~/ultro.browning.edu/public"
            if srel == "src/layouts/MainLayout.astro":
                kind, value = "ultro-name-in-text", line.strip()
            add(srel, i, kind, value, loc(rel, line))


def main():
    for rel, p in files():
        scan_file(rel, p)
    # a description that is a prop with no Ultro name still needs rewriting; already listed above
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    seen, uniq = set(), []
    for r in rows:
        if r in seen:
            continue
        seen.add(r)
        uniq.append(r)
    kinds = {}
    for r in uniq:
        kinds[r[2]] = kinds.get(r[2], 0) + 1
    head = f"""# INVENTORY: Ultro occurrences for the text-and-links pass

Nothing in this file was edited in pass 1. Format: `file:line | kind | exact value | location`, one row per occurrence.
Edits made in pass 1 (logo alt/title/aria-label set to "GEMINII", brand files, Arvo, palette) are not listed.
Rows for CSS selectors and variables that still carry an Ultro identifier are listed because a rename must follow them
(`src/styles/global.css` holds the palette override rules added in pass 1; they use the original names).

Kinds with no occurrence in the site: analytics-id, manifest-name, legal-page (no pages; README copyright line is listed as text).

Counts: {', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}; total {len(uniq)}.

```text
"""
    body = "\n".join(f"{f}:{ln} | {k} | {v} | {l}" for f, ln, k, v, l in uniq)
    OUT.write_text(head + body + "\n```\n")
    print(f"{len(uniq)} rows -> {OUT.relative_to(SITE)}")
    print(kinds)


if __name__ == "__main__":
    main()
