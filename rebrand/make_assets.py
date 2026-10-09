#!/usr/bin/env python3
"""Copies the brand-kit assets this site needs into public/ (pass 1 of the rebrand).

Reads only fonts/, logos/svg/ and favicons/ from the kit and never modifies the kit.
Needs: pip install playwright pillow (Chrome rasterises the 96x96 favicon, which the kit lacks).
This folder (rebrand/) is excluded from deployment.
"""
import base64
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent.parent
KIT = SITE / "GEMINII_Brandkit"
PUBLIC = SITE / "public"


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"{src.relative_to(KIT)} -> {dst.relative_to(SITE)}")


def main():
    # self-hosted Arvo, license next to the font files
    for f in ("Arvo-Regular.woff2", "Arvo-Bold.woff2", "OFL.txt"):
        copy(KIT / "fonts" / f, PUBLIC / "assets" / "fonts" / f)
    # logo used in the header, footer and legacy page slot: icon, full color on black
    copy(KIT / "logos" / "svg" / "icon-gradient-on-dark.svg", PUBLIC / "assets" / "brand" / "icon-gradient-on-dark.svg")
    # fixed-path icon files, overwritten at the same path and size
    copy(KIT / "favicons" / "favicon.ico", PUBLIC / "favicon.ico")
    copy(KIT / "favicons" / "favicon.svg", PUBLIC / "favicon.svg")
    copy(KIT / "favicons" / "apple-touch-icon.png", PUBLIC / "apple-touch-icon.png")
    # 96x96 PNG: the kit has no such size, so rasterise the kit's favicon.svg
    svg = (KIT / "favicons" / "favicon.svg").read_bytes()
    b64 = base64.b64encode(svg).decode()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 96, "height": 96}, device_scale_factor=1)
        page.set_content('<body style="margin:0;background:transparent"><img id="i" width="96" height="96" '
                         f'style="display:block" src="data:image/svg+xml;base64,{b64}"></body>')
        page.wait_for_function("document.getElementById('i').complete")
        page.screenshot(path=str(PUBLIC / "favicon-96x96.png"), omit_background=True,
                        clip={"x": 0, "y": 0, "width": 96, "height": 96})
        browser.close()
    print("rasterised favicons/favicon.svg -> public/favicon-96x96.png (96x96)")


if __name__ == "__main__":
    sys.exit(main())
