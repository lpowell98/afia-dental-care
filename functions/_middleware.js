// Temporary password lock for the whole site (Cloudflare Pages Function).
// To remove the lock: delete this file (or the whole functions/ folder) and push.
// The repo is public, so only a SHA-256 hash of the password lives here.
// Hash = sha256("afia-lock:" + PASSWORD), password compared case-insensitively.

const HASH = "4e3dbf670822a5cd701cd2b4aeefc5cbad6c47c7abf43cfea34f43c0d70d7037";
const COOKIE = "afia_unlock";
const MAX_AGE = 60 * 60 * 24 * 30; // stay unlocked 30 days per browser

// Files that must stay public (email signature logo, favicons).
const PUBLIC = new Set([
  "/icon-192.png", "/icon-512.png", "/favicon-32.png",
  "/favicon.svg", "/apple-touch-icon.png",
]);

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function getCookie(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return "";
}

function safeNext(value) {
  return typeof value === "string" && value.startsWith("/") && !value.startsWith("//") ? value : "/";
}

function lockPage(next, wrong) {
  const esc = (s) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Afia Dental</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;
    font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#0f4c45;color:#fff}
  .box{width:100%;max-width:360px;text-align:center}
  img{width:72px;height:72px;border-radius:16px}
  h1{font-size:1.5rem;margin:16px 0 4px}
  p{margin:0 0 20px;opacity:.85}
  label{display:block;text-align:left;font-size:.9rem;margin-bottom:6px}
  input{width:100%;padding:12px 14px;font-size:1rem;border-radius:10px;border:2px solid transparent}
  input:focus{outline:none;border-color:#d4a73a}
  button{margin-top:12px;width:100%;padding:12px;font-size:1rem;font-weight:600;border:0;border-radius:10px;
    background:#d4a73a;color:#1d1d1d;cursor:pointer}
  button:focus-visible{outline:3px solid #fff;outline-offset:2px}
  .err{color:#ffd6d6;margin:10px 0 0;font-size:.9rem}
</style></head>
<body><main class="box">
  <img src="/icon-192.png" alt="">
  <h1>Afia Dental</h1>
  <p>Our new website is coming soon. Call us at <a href="tel:+16173254100" style="color:#fff">(617) 325-4100</a>.</p>
  <form method="post" action="/__unlock">
    <input type="hidden" name="next" value="${esc(next)}">
    <label for="pw">Password</label>
    <input id="pw" name="password" type="password" autocomplete="current-password" required autofocus>
    <button type="submit">Enter</button>
    ${wrong ? '<p class="err" role="alert">Wrong password. Please try again.</p>' : ""}
  </form>
</main></body></html>`;
}

function respond(html, status) {
  return new Response(html, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Retry-After": "86400",
      "X-Frame-Options": "DENY",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export async function onRequest({ request, next }) {
  const url = new URL(request.url);

  if (PUBLIC.has(url.pathname)) return next();

  if (url.pathname === "/__unlock" && request.method === "POST") {
    const form = await request.formData();
    const pw = String(form.get("password") || "").trim().toUpperCase();
    const dest = safeNext(String(form.get("next") || "/"));
    if ((await sha256("afia-lock:" + pw)) === HASH) {
      return new Response(null, {
        status: 303,
        headers: {
          Location: dest,
          "Set-Cookie": `${COOKIE}=${HASH}; Max-Age=${MAX_AGE}; Path=/; Secure; HttpOnly; SameSite=Lax`,
          "Cache-Control": "no-store",
        },
      });
    }
    return respond(lockPage(dest, true), 401);
  }

  if (getCookie(request, COOKIE) === HASH) {
    const res = await next();
    const out = new Response(res.body, res);
    out.headers.set("Cache-Control", "private, no-store");
    return out;
  }

  // 503 + Retry-After tells search engines the outage is temporary.
  return respond(lockPage(url.pathname + url.search, false), 503);
}
