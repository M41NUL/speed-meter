# SPEED METER (static, no backend)

Same analog dial speed test — this version has **no server at all**. It measures your connection directly against Cloudflare's public speed-test edge (`speed.cloudflare.com`), the same endpoints that power speed.cloudflare.com itself. Deploys as a single static HTML file, works on Vercel, Netlify, GitHub Pages, or any static host.

## Files

```
speedtest-vercel/
├── index.html      ← everything: markup, styles, logic
└── vercel.json     ← static hosting config (optional but explicit)
```

## Deploy to Vercel

```bash
npm i -g vercel   # if you don't have it already
cd speedtest-vercel
vercel
```

Or just connect the GitHub repo in the Vercel dashboard — no build command needed, no environment variables, no framework preset (choose "Other").

## How it works

- **Ping** — 5 zero-byte requests to `https://speed.cloudflare.com/__down?bytes=0`, takes the median round-trip time.
- **Download** — fetches `https://speed.cloudflare.com/__down?bytes=N` at increasing sizes (5MB → 15MB → 30MB), reading the stream and computing live throughput as bytes arrive.
- **Upload** — POSTs random bytes (2MB → 6MB → 12MB) to `https://speed.cloudflare.com/__up`.

These are the same (unofficial but stable and widely used) endpoints that Cloudflare's own `@cloudflare/speedtest` npm package and speed.cloudflare.com use internally.

## Why no backend?

Vercel's serverless functions aren't a good fit for streaming a large response over time (needed to measure real throughput) — they're built for short, stateless requests. Rather than fight that, this version skips having any backend of our own and points directly at Cloudflare's edge, which is built to handle exactly this kind of test at scale.

## Trade-offs vs. the self-hosted version

- You're testing against Cloudflare's network specifically, not "the internet" in general — though this is the same approach speedtest.net and Cloudflare's own tool use (test against a known, well-connected server).
- No control over the test server's location — Cloudflare's anycast network automatically routes you to their nearest edge location, which is usually a good thing.
- If Cloudflare ever changes or removes these endpoints, the tool would need updating — they're undocumented but have been stable for years and are actively used by Cloudflare's own product.

## Notes

- Requires internet access to `speed.cloudflare.com` — if that domain is blocked on a network (rare, but some corporate/school networks block it), the test will fail to connect.
- Recent test results are kept in the browser's local storage (last 10 runs) — nothing is sent anywhere except the Cloudflare test traffic itself.
