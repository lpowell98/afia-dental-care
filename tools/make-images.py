#!/usr/bin/env python3
"""Make favicons and 1200x630 share images. Run before tools/build.py:
   python3 tools/make-images.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "site"
import sys; sys.path.insert(0, str(ROOT / "src")); from services import SERVICES
TOOTH = 'M11 3.2C8.6 1 3 .3 2 5.4c-.7 3.7 1.3 6 2 9 .6 2.5.7 8.2 3 8.2s1.9-5.6 4-5.6 1.7 5.6 4 5.6 2.4-5.7 3-8.2c.7-3 2.7-5.3 2-9C19 .3 13.4 1 11 3.2Z'
FAV = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#1E3A35"/><g transform="translate(5 4)"><path d="{TOOTH}" fill="#D6A653"/></g></svg>'
(OUT / "favicon.svg").write_text(FAV + "\n")
PAGES = {"home": ("Dentist in West Roxbury, MA", "Afia Dental"),
         "privacy": ("Afia Dental", "Privacy Policy"), "terms": ("Afia Dental", "Terms of Use"),
         "disclaimer": ("Afia Dental", "Disclaimer"), "accessibility": ("Afia Dental", "Accessibility"),
         "404": ("Afia Dental", "Page not found")}
PAGES.update({x["slug"]: ("Afia Dental · West Roxbury, MA", x["name"]) for x in SERVICES})
import base64
FONT = "data:font/woff2;base64," + base64.b64encode((OUT / "fonts/bricolage-grotesque.woff2").read_bytes()).decode()
def og(kick, title):
    return f'''<html><head><style>@font-face{{font-family:B;src:url({FONT});font-weight:200 800}}
body{{margin:0;width:1200px;height:630px;background:#1E3A35;color:#F1F5F3;font-family:B;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
small{{font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:#EBD3A6;font-weight:500}}
h1{{font-size:{'128' if len(title)<18 else '104'}px;font-weight:600;letter-spacing:-.05em;line-height:.95;margin:22px 60px 0}}
svg.arc{{width:440px;margin-top:22px;color:#D6A653}} p{{font-size:28px;margin-top:34px;opacity:.9}}</style></head><body>
<small>{kick}</small><h1>{title}</h1><svg class="arc" viewBox="0 0 400 60"><path d="M4 6 Q200 112 396 6 Q200 64 4 6 Z" fill="currentColor"/></svg>
<p>1208B VFW Parkway, West Roxbury · (617) 325-4100</p></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, size in [("favicon-32.png", 32), ("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)]:
        pg = b.new_page(viewport={"width": size, "height": size})
        pg.set_content(f'<body style="margin:0">{FAV.replace("<svg ", f"<svg width={size} height={size} ")}</body>')
        pg.screenshot(path=str(OUT / name), omit_background=True); pg.close()
    for slug, (k, t) in PAGES.items():
        pg = b.new_page(viewport={"width": 1200, "height": 630}); pg.set_content(og(k, t)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f"img/og-{slug}.png")); pg.close()
    b.close()
print("images done")
