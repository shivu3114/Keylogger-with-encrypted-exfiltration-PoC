from flask import Flask, request, jsonify
from datetime import datetime
import os, secrets, hmac, hashlib, base64
from crypto_utils import get_fernet
from dotenv import load_dotenv

# Load .env values
load_dotenv()
API_KEY = os.getenv("API_KEY", "")
HMAC_KEY = os.getenv("HMAC_KEY", "")

app = Flask(__name__)

RECV_DIR = "server_received"
os.makedirs(RECV_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])   # ✅ works for all Flask versions
def upload():
    """
    Accepts JSON payload:
    {
        "host": "...",
        "ts": "ISO-8601",
        "payload_b64": "base64-encoded encrypted bytes",
        "hmac": "hex-string"   # optional, required if HMAC_KEY set
    }
    Headers:
        X-API-KEY: must match API_KEY (if set)
    """
    try:
        # --- API key check ---
        if API_KEY:
            provided = request.headers.get("X-API-KEY", "")
            if not secrets.compare_digest(provided, API_KEY):
                return jsonify({"ok": False, "error": "unauthorized"}), 401

        # Parse JSON
        data = request.get_json(force=True, silent=False)
        host = data.get("host", "unknown")
        ts = data.get("ts") or datetime.utcnow().isoformat() + "Z"
        payload_b64 = data["payload_b64"]

        # Decode encrypted payload
        enc = base64.b64decode(payload_b64.encode())

        # --- HMAC check ---
        if HMAC_KEY:
            received_hmac = data.get("hmac", "")
            calc = hmac.new(HMAC_KEY.encode(), enc, hashlib.sha256).hexdigest()
            if not secrets.compare_digest(calc, received_hmac):
                return jsonify({"ok": False, "error": "invalid signature"}), 401

        # Validate decryptability (optional sanity check)
        _ = get_fernet().decrypt(enc)

        # Store raw encrypted payload
        fname = f"{ts.replace(':','-')}_{host}.bin"
        path = os.path.join(RECV_DIR, fname)
        with open(path, "wb") as f:
            f.write(enc)

        return jsonify({"ok": True, "stored": path}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    # Run Flask server
    app.run(host="127.0.0.1", port=5000, debug=True)
