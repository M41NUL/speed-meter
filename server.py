# ─────────────────────────────────────────
#  SPEED METER — server.py (Flask backend)
#  Dev: Md. Mainul Islam (CODEX-M41NUL)
# ─────────────────────────────────────────

import os
import time
import secrets

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "public"), static_url_path="")
CORS(app)

# Pre-generate a chunk of random bytes once at startup — reused for every
# download test so we're not burning CPU generating random data per request.
CHUNK_SIZE = 256 * 1024  # 256 KB per streamed chunk
_RANDOM_CHUNK = secrets.token_bytes(CHUNK_SIZE)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/ping")
def ping():
    """Empty response as fast as possible — client measures round-trip time from this."""
    return jsonify({"ok": True, "ts": time.time()})


@app.route("/api/download-test")
def download_test():
    """
    Streams `size` bytes of random data to the client. The client measures how
    long the full transfer takes and computes throughput from that.
    """
    try:
        size_mb = float(request.args.get("size", "10"))
    except (TypeError, ValueError):
        size_mb = 10.0
    size_mb = max(0.5, min(size_mb, 200))  # clamp to a sane range (0.5MB - 200MB)
    total_bytes = int(size_mb * 1024 * 1024)

    def generate():
        sent = 0
        while sent < total_bytes:
            remaining = total_bytes - sent
            chunk = _RANDOM_CHUNK if remaining >= CHUNK_SIZE else _RANDOM_CHUNK[:remaining]
            sent += len(chunk)
            yield chunk

    return Response(
        stream_with_context(generate()),
        mimetype="application/octet-stream",
        headers={
            "Content-Length": str(total_bytes),
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Content-Disposition": "inline",
        },
    )


@app.route("/api/upload-test", methods=["POST"])
def upload_test():
    """
    Receives and discards uploaded bytes. The client sends a payload of known
    size and measures how long the request took to compute upload throughput.
    """
    total = 0
    # read in chunks so we don't buffer a huge payload in memory at once
    while True:
        chunk = request.stream.read(65536)
        if not chunk:
            break
        total += len(chunk)
    return jsonify({"ok": True, "bytesReceived": total})


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
