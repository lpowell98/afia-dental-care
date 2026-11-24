#!/usr/bin/env python3
"""Make favicons and 1200x630 share images. Run before tools/build.py:
   python3 tools/make-images.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "site"
import sys; sys.path.insert(0, str(ROOT / "src")); from services import SERVICES
# Tooth-A mark and app icon, from the supplied brand file afia-app-icon.svg (never redraw)
TOOTH = 'M50 15 C56 9 66 6 74 9 C84 13 86 26 83 38 C81 47 79 53 79 60 L84 88 C85 93 79 96 76 91 L60 64 C57 59 43 59 40 64 L24 91 C21 96 15 93 16 88 L21 60 C21 53 19 47 17 38 C14 26 16 13 26 9 C34 6 44 9 50 15 Z M50 31 C49 31 48.6 31.4 48.2 32.2 L40.6 48.6 C40 50 40.7 51 42.2 51 L57.8 51 C59.3 51 60 50 59.4 48.6 L51.8 32.2 C51.4 31.4 51 31 50 31 Z'
def app_icon(rx=22): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="{rx}" fill="#1E3A35"/><path transform="translate(18 17) scale(0.64)" fill="#D6A653" fill-rule="evenodd" d="{TOOTH}"/></svg>'
FAV = app_icon()
(OUT / "favicon.svg").write_text(FAV + "\n")
PAGES = {"home": ("Dentist in West Roxbury, MA", "Afia Dental"),
         "privacy": ("Afia Dental", "Privacy Policy"), "terms": ("Afia Dental", "Terms of Use"),
         "disclaimer": ("Afia Dental", "Disclaimer"), "accessibility": ("Afia Dental", "Accessibility"),
         "404": ("Afia Dental", "Page not found")}
PAGES.update({"contact": ("Afia Dental · West Roxbury, MA", "Contact & Directions"), "our-dentists": ("Afia Dental · West Roxbury, MA", "Our Dentists"), "new-patients": ("Afia Dental · West Roxbury, MA", "New Patients")})
PAGES.update({x["slug"]: ("Afia Dental · West Roxbury, MA", x["name"]) for x in SERVICES})
import base64
FONT = "data:font/woff2;base64," + base64.b64encode((OUT / "fonts/bricolage-grotesque.woff2").read_bytes()).decode()
# Share images carry the supplied logo files (brand guide: never retype or redraw the logo)
LOCKUP = (OUT / "img/brand/afia-lockup-on-dark.svg").read_text().strip()
STACKED = (OUT / "img/brand/afia-lockup-stacked-on-dark.svg").read_text().strip()
def sentence(t):  # headings in sentence case (brand guide p.15); proper nouns kept
    keep = {"Invisalign®", "MA"}
    w = t.split(" ")
    return " ".join([w[0]] + [x if x in keep else x.lower() for x in w[1:]])
def og(kick, title, home=False):
    title = sentence(title)
    css = f'''@font-face{{font-family:B;src:url({FONT});font-weight:200 800}}
body{{margin:0;width:1200px;height:630px;background:#1E3A35;color:#F1F5F3;font-family:B;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.logo svg{{display:block;height:{'300' if home else '120'}px;width:auto}}
small{{font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:#EBD3A6;font-weight:500;margin-top:28px}}
h1{{font-size:{'112' if len(title)<18 else '92'}px;font-weight:600;letter-spacing:-.05em;line-height:.95;margin:40px 60px 0}}
p{{font-size:28px;margin-top:{'28' if home else '40'}px;opacity:.9}}'''
    if home:
        body = f'<div class="logo">{STACKED}</div><small>{kick}</small>'
    else:
        body = f'<div class="logo">{LOCKUP}</div><h1>{title}</h1>'
    return f'''<html><head><style>{css}</style></head><body>{body}
<p>1208B VFW Parkway, West Roxbury · (617) 325-4100</p></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch()
    # apple-touch-icon is full-bleed: iOS rounds the corners itself
    for name, size, svg in [("favicon-32.png", 32, FAV), ("icon-192.png", 192, FAV), ("icon-512.png", 512, FAV), ("apple-touch-icon.png", 180, app_icon(0))]:
        pg = b.new_page(viewport={"width": size, "height": size})
        pg.set_content(f'<body style="margin:0">{svg.replace("<svg ", f"<svg width={size} height={size} ")}</body>')
        pg.screenshot(path=str(OUT / name), omit_background=True); pg.close()
    for slug, (k, t) in PAGES.items():
        pg = b.new_page(viewport={"width": 1200, "height": 630}); pg.set_content(og(k, t, home=(slug == "home"))); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f"img/og-{slug}.png")); pg.close()
    b.close()
print("images done")
