# afiadentalcare.com

Static site for Afia Dental Care (West Roxbury, MA). Plain HTML/CSS/JS on Cloudflare Pages.

| Path | What it is |
|---|---|
| `site.json` | Business facts (name, phone, address, hours, dentists). Edit here first. |
| `src/pages/*.html` | Page bodies. `index.html` is the homepage. |
| `src/partials/footer.html` | Shared footer for every page. |
| `site/css/site.css`, `site/js/site.js` | Styles and behavior (open-now status, dentist picker, Simplifeye booking). |
| `site/img/`, `site/fonts/` | Images (WebP) and the self-hosted font. |
| `site/_headers`, `site/_redirects` | Security/cache headers and old Parkway Dental URL redirects. |
| `tools/make-images.py` | Favicons and share images. |
| `tools/build.py` | Builds every page, `sitemap.xml`, `robots.txt`, `llms.txt`. |
| `seo/` | BRAND, VOICE, TOPICAL-MAP, BRIEF. Read before content or SEO work. |

## Build
    python3 tools/make-images.py && python3 tools/build.py

Never hand-edit the built `.html`, `sitemap.xml`, `robots.txt` or `llms.txt` in `site/`.

## Deploy
Cloudflare Pages, build output directory `site`, no build command. Pushes to `main` go live; other branches get preview links.
