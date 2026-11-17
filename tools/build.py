#!/usr/bin/env python3
"""Build afiadentalcare.com into site/.

Sources: site.json (business facts), src/pages/*.html (page bodies),
src/partials/footer.html (shared footer). Never hand-edit the built
.html files, robots.txt, sitemap.xml or llms.txt in site/; edit the
sources and run:  python3 tools/build.py
"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "site"
sys.path.insert(0, str(SRC))
from services import SERVICES  # noqa: E402
SVC = {x["slug"]: x for x in SERVICES}
S = json.loads((ROOT / "site.json").read_text())
UPDATED_ISO = "2026-11-14"          # change when page content changes
UPDATED = "November 14, 2026"
URL = S["url"]

PAGES = [  # slug, title (<60 chars), description (~140-160), indexable
    ("", "Dentist in West Roxbury, MA | Afia Dental",
     "Family and cosmetic dentistry in West Roxbury for over 40 years. Same-day crowns, implants, Invisalign, kids' care and emergencies. Book online.", True),
    ("privacy", "Privacy Policy | Afia Dental",
     "How the Afia Dental website handles visit statistics, online booking through Simplifeye and the information you share with our West Roxbury office.", True),
    ("terms", "Terms of Use | Afia Dental",
     "Terms for using afiadentalcare.com, including site information, online booking through Simplifeye, links to other sites and Massachusetts governing law.", True),
    ("disclaimer", "Disclaimer | Afia Dental",
     "The Afia Dental website offers general dental information, not a diagnosis. Call (617) 325-4100 for urgent problems or 911 for emergencies.", True),
    ("accessibility", "Accessibility | Afia Dental",
     "Afia Dental aims to meet WCAG 2.1 AA on afiadentalcare.com. Call (617) 325-4100 for help booking or to report an accessibility problem.", True),
    ("contact", "Contact & Directions | Afia Dental, West Roxbury MA",
     "Call (617) 325-4100, book online or visit Afia Dental at 1208B VFW Parkway, Suite 307 in the Ingleside Mall, West Roxbury. Hours, parking and directions.", True),
    ("new-patients", "New Patients | Afia Dental, West Roxbury MA",
     "New to Afia Dental? Your $139 first visit includes an exam, cleaning and 4 digital X-rays. What to bring, insurance and payment options in West Roxbury.", True),
    ("our-dentists", "Our Dentists in West Roxbury, MA | Afia Dental",
     "Meet owner Dr. Alla Edriss, DMD, and our West Roxbury dentists: Dr. Raza Baig, Dr. Eriselda Bano, Dr. Suky Sidhu and Dr. Natalie Sokoloff.", True),
    ("404", "Page Not Found | Afia Dental",
     "This page doesn't exist. Visit the Afia Dental homepage, book online or call (617) 325-4100.", False),
]


def page_url(slug):
    return f"{URL}/" if slug in ("", "404") else f"{URL}/{slug}/"


def business():
    a = S["address"]
    days = [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"],
             "opens": h["opens"], "closes": h["closes"]} for h in S["hours"]]
    b = {
        "@type": S["schemaType"], "@id": f"{URL}/#business",
        "name": S["name"], "legalName": S["legalName"], "url": f"{URL}/",
        "description": S["description"], "telephone": S["telephone"],
        "logo": f"{URL}/icon-512.png", "image": f"{URL}/img/og-home.png",
        "address": {"@type": "PostalAddress", **a},
        "openingHoursSpecification": days, "priceRange": S["priceRange"],
        "hasMap": S["hasMap"], "sameAs": S["sameAs"],
        "areaServed": [{"@type": "Place", "name": n} for n in S["areaServed"]],
        "contactPoint": {"@type": "ContactPoint", "telephone": S["telephone"],
                         "contactType": "appointments", "areaServed": "US",
                         "availableLanguage": "en"},
        "employee": [{"@type": "Person", "name": d["name"], "jobTitle": d["focus"]} for d in S["dentists"]],
    }
    if S.get("email"):
        b["email"] = S["email"]
    return b


def faq(body, fid=None):
    qs = re.findall(r"<summary>(.*?)<span class=\"plus\"></span></summary><p>(.*?)</p>", body)
    return {"@type": "FAQPage", "@id": fid or f"{URL}/#faq", "mainEntity": [
        {"@type": "Question", "name": html.unescape(re.sub("<[^>]+>", "", q)),
         "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<[^>]+>", "", a))}}
        for q, a in qs]}


def graph(slug, title, body):
    g = [business(), {"@type": "WebSite", "@id": f"{URL}/#website", "url": f"{URL}/",
                      "name": S["name"], "publisher": {"@id": f"{URL}/#business"}}]
    if slug == "":
        g.append(faq(body))
    elif slug in SVC:
        sv = SVC[slug]
        g.append({"@type": "Service", "@id": f"{page_url(slug)}#service", "name": title.split(" | ")[0],
                  "serviceType": sv["name"].replace("®", ""), "description": sv["desc"], "url": page_url(slug),
                  "provider": {"@id": f"{URL}/#business"},
                  "areaServed": [{"@type": "Place", "name": n} for n in S["areaServed"]]})
        g.append(faq(body, f"{page_url(slug)}#faq"))
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": f"{URL}/#services"},
            {"@type": "ListItem", "position": 3, "name": sv["name"], "item": page_url(slug)}]})
    if slug == "our-dentists":
        g += [{"@type": "Person", "@id": f"{page_url(slug)}#{d['id']}", "name": d["name"], "jobTitle": d["focus"],
               "image": f"{URL}/img/{d['id']}.webp", "url": f"{page_url(slug)}#{d['id']}",
               "worksFor": {"@id": f"{URL}/#business"}, **({"alumniOf": [{"@type": "CollegeOrUniversity", "name": n} for n in d["alumniOf"]]} if d.get("alumniOf") else {})}
              for d in S["dentists"]]
    if slug == "new-patients":
        g.append(faq(body, f"{page_url(slug)}#faq"))
    if slug == "contact":
        g.append({"@type": "ContactPage", "@id": page_url(slug), "url": page_url(slug), "name": title.split(" | ")[0], "about": {"@id": f"{URL}/#business"}})
    if slug not in ("", "404") and slug not in SVC:
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{URL}/"},
            {"@type": "ListItem", "position": 2, "name": title.split(" | ")[0], "item": page_url(slug)}]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, separators=(",", ":"))


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{canon}">
<meta name="theme-color" content="{theme}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{url}/img/og-{og}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{url}/img/og-{og}.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://embed.simplifeye.co" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css?v={ver}">
<script>document.documentElement.classList.add('js')</script>
<script src="/js/site.js?v={ver}" defer></script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
"""

HEADER = """<a class="skip" href="#main">Skip to content</a>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="tooth" viewBox="0 0 22 24"><path d="M11 3.2C8.6 1 3 .3 2 5.4c-.7 3.7 1.3 6 2 9 .6 2.5.7 8.2 3 8.2s1.9-5.6 4-5.6 1.7 5.6 4 5.6 2.4-5.7 3-8.2c.7-3 2.7-5.3 2-9C19 .3 13.4 1 11 3.2Z" fill="currentColor"/></symbol></svg>
<header class="bar" id="top">
  {{TOPBAR}}
</header>
"""

BAR = HEADER + """<main id="main" class="wrap doc">
{body}</main>
"""

SHORT = {
    "dental-check-ups": "Exam, cleaning and oral cancer screening every six months.",
    "preventative-dentistry": "Fluoride, sealants and habits that stop problems early.",
    "dental-crowns-and-bridges": "Most crowns fitted in a single visit.",
    "restorative-dentistry": "Fillings, crowns, bridges, implants and dentures.",
    "dental-implants": "Permanent replacements for missing teeth, including All-on-4®.",
    "invisalign": "Clear aligners that straighten teeth without metal braces.",
    "cosmetic-dentistry": "Whitening, veneers, bonding and smile makeovers.",
    "pediatric-dentistry": "Gentle visits for toddlers to teens, led by Dr. Bano.",
    "tooth-extraction": "Simple and surgical extractions, including wisdom teeth.",
    "dental-emergencies": "Same-day care for pain, chips and broken teeth.",
}


def tile(slug):
    from PIL import Image
    sv = SVC[slug]
    iw, ih = Image.open(OUT / f"img/{sv['img']}.webp").size
    return (f'<a class="tile" href="/{slug}/"><div class="stage"><div class="smile-img">'
            f'<img src="/img/{sv["img"]}.webp" alt="" width="{iw}" height="{ih}" loading="lazy"></div></div>'
            f'<h3>{notr(sv["name"])}</h3><p>{SHORT[slug]}</p></a>')


def notr(t):
    """Keep brand names out of browser auto-translation in visible copy."""
    return re.sub(r"(Invisalign®?(?: Teen)?|All-on-4®|Afia Dental)", r'<span translate="no">\1</span>', t)


def service_body(sv):
    from PIL import Image
    w, h = Image.open(OUT / f"img/{sv['img']}.webp").size
    h1 = sv["title"].split(" | ")[0]
    secs = notr("".join(f'<h2>{hd}</h2>\n{bd.strip()}\n' for hd, bd in sv["sections"]))
    qs = notr("".join(f'<details name="faq"><summary>{q}<span class="plus"></span></summary><p>{a}</p></details>\n'
                 for q, a in sv["faqs"]))
    rel = "".join(tile(r) for r in sv["related"])
    return HEADER + f"""<main id="main">
<section class="svc-hero"><div class="wrap svc-hero-in">
<div class="svc-hero-text">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/#services">Services</a><span aria-hidden="true">/</span><span aria-current="page">{sv["name"]}</span></nav>
<h1>{notr(h1)}</h1>
<p class="svc-lead">{notr(sv["lead"])}</p>
<div class="hero-actions"><a class="btn" href="/#book" data-book>Request an appointment</a><a class="btn ghost" href="tel:+16173254100">Call (617) 325-4100</a></div>
</div>
<div class="svc-hero-img smile-img"><img src="/img/{sv["img"]}.webp" alt="{sv["alt"]}" width="{w}" height="{h}" fetchpriority="high"></div>
</div></section>
<div class="wrap svc-body">
<article class="svc-article">
{secs}<h2 id="faq-h">Frequently asked questions</h2>
<div class="qs">
{qs}</div>
</article>
<div class="svc-side"><div class="side-card">
<p class="side-h">Book a visit</p>
<p>New patients: <strong>$139</strong> exam, cleaning and 4 digital X-rays. Emergency exam <strong>$59</strong>.</p>
<a class="btn" href="/#book" data-book>Request an appointment</a>
<a class="side-tel" href="tel:+16173254100">(617) 325-4100</a>
<p class="side-small">Mon–Fri 9–5 · Sat 9–3 · Sun closed<br>1208B VFW Parkway, Suite 307, West Roxbury</p>
</div></div>
</div>
<section class="wrap svc-related" aria-labelledby="rel-h"><h2 id="rel-h">Related services</h2><div class="tiles rel">{rel}</div></section>
</main>

{{{{FOOTER}}}}
"""


def build():
    import hashlib
    ver = hashlib.md5((OUT / "css/site.css").read_bytes() + (OUT / "js/site.js").read_bytes()).hexdigest()[:8]
    footer = (SRC / "partials/footer.html").read_text()
    topbar = (SRC / "partials/topbar.html").read_text().strip()
    email_sentence = f", email <a href=\"mailto:{S['email']}\">{S['email']}</a>," if S.get("email") else ","
    allp = [(s_, t, d, i, None) for s_, t, d, i in PAGES] + [(x["slug"], x["title"], x["desc"], True, service_body(x)) for x in SERVICES]
    for slug, title, desc, index, sbody in allp:
        assert len(title) <= 60, (slug, len(title))
        if sbody:
            body = sbody
        else:
            body = (SRC / f"pages/{slug or 'index'}.html").read_text()
            if slug:
                if body.startswith("<!--wide-->"):
                    body = BAR.replace('<main id="main" class="wrap doc">', '<main id="main" class="wrap page">').replace("{body}", body[len("<!--wide-->"):].lstrip()) + "\n{{FOOTER}}\n"
                else:
                    body = BAR.replace("{body}", body) + "\n{{FOOTER}}\n"
        body = body.replace("{{FOOTER}}", footer).replace("{{TOPBAR}}", topbar)
        body = body.replace("{{UPDATED}}", UPDATED).replace("{{EMAIL_SENTENCE}}", email_sentence).replace("{{EMAIL}}", S.get("email", ""))
        head = HEAD.format(title=html.escape(title), desc=html.escape(desc), canon=page_url(slug),
                           robots='<meta name="robots" content="noindex">\n' if not index else "",
                           theme=S["themeColor"], name=S["name"], url=URL, og=slug or "home",
                           ver=ver, ld=graph(slug, title, body))
        out = OUT / ("index.html" if slug == "" else "404.html" if slug == "404" else f"{slug}/index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        page = head + body.rstrip() + "\n</body>\n</html>\n"
        # Version tag on photos so browsers and Cloudflare fetch new files when a photo changes
        page = re.sub(r'(/img/[\w-]+\.webp)"', lambda m: f'{m.group(1)}?v={hashlib.md5((OUT / m.group(1)[1:]).read_bytes()).hexdigest()[:8]}"', page)
        out.write_text(page)
        assert "{{" not in out.read_text(), out

    idx = [p[:4] for p in allp if p[3]]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{page_url(s)}</loc><lastmod>{UPDATED_ISO}</lastmod></url>\n" for s, *_ in idx)
        + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n")
    a = S["address"]
    (OUT / "llms.txt").write_text(
        f"# {S['name']}\n\n> {S['description']}\n\n"
        f"- Address: {a['streetAddress']}, {a['addressLocality']}, {a['addressRegion']} {a['postalCode']} (Ingleside Mall)\n"
        f"- Phone: {S['phoneDisplay']}\n- Hours: Mon-Fri 9 am-5 pm, Sat 9 am-3 pm, Sun closed\n"
        f"- New-patient visit $139 (exam, cleaning, 4 digital X-rays); emergency exam $59\n"
        f"- Dentists: " + "; ".join(f"{d['name']} ({d['focus'].lower()})" for d in S["dentists"]) + "\n"
        f"- Book online: {URL}/#book\n\n## Pages\n\n"
        + "".join(f"- [{t.split(' | ')[0]}]({page_url(s)}): {d}\n" for s, t, d, _ in idx))
    print("built", len(allp), "pages, version", ver)


if __name__ == "__main__":
    sys.exit(build())
