# SPEED METER

A self-hosted internet speed test — analog dial gauge, dark monochrome instrument-panel look. Flask backend measures real download/upload throughput and ping against your own server (no third-party API dependency).

## Files

```
speedtest/
├── server.py           ← Flask backend
├── requirements.txt
└── public/
    └── index.html      ← frontend (dial gauge, all logic, no build step)
```

## Run locally

```bash
pip install -r requirements.txt
python server.py
```

Open `http://localhost:5000` (or your LAN IP on port 5000 from another device on the same network).

## How it works

**Ping** — 5 quick round-trips to `/api/ping`, takes the median to avoid one slow request skewing the result.

**Download** — fetches `/api/download-test?size=N` in increasing sizes (4MB → 12MB → 24MB) so a slow connection doesn't get stuck waiting on a huge file, and a fast connection gets enough data for an accurate reading. The needle updates live as bytes stream in.

**Upload** — posts random bytes to `/api/upload-test` (2MB → 6MB → 12MB), same ramping approach. The server just reads and discards the data — nothing is saved to disk.

The dial itself is a real instrument-style analog gauge (SVG), with a non-linear scale (0, 5, 10, 25, 50, 100, 250, 500, 1000 Mbps) so typical home-internet speeds (5–200 Mbps) get most of the dial's resolution instead of being crushed into a tiny sliver next to gigabit numbers.

Recent test results are kept in the browser's local storage (last 10 runs) — nothing is sent to or stored on the server beyond the transfer itself.

## Deploy

Same stack you already use for other tools:
- **Render** — deploy `server.py` as a Python web service (`python server.py` or via gunicorn)
- Make sure the platform doesn't buffer/compress the streamed download response — that would throw off timing accuracy (Render's default proxy is fine; Cloudflare-proxied domains can sometimes buffer, worth testing after deploy)

## Notes

- This measures your connection to **this specific server**, not a global "internet speed" — for best accuracy, host it somewhere with good general connectivity (same as speedtest.net's model of using nearby test servers).
- Numbers are estimates. Browser overhead, other apps using the network, and Wi-Fi conditions all affect the result — same caveats as any speed test tool.
