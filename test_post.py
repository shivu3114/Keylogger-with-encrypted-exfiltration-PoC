#!/usr/bin/env python3
"""
Quick test script to POST a single encrypted payload to the server.
Usage:
  python test_post.py --server http://127.0.0.1:5000/upload
"""
import argparse
import base64
import json
import os
import socket
import hmac, hashlib
from datetime import datetime
import requests
from crypto_utils import encrypt_text
from dotenv import load_dotenv

# Load .env values
load_dotenv()
API_KEY = os.getenv("API_KEY", "")
HMAC_KEY = os.getenv("HMAC_KEY", "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os.getenv("SERVER_URL", "http://127.0.0.1:5000/upload"))
    ap.add_argument("--text", default="Test message from test_post.py")
    args = ap.parse_args()

    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": socket.gethostname(),
        "text": args.text,
    }
    rec_json = json.dumps(record, ensure_ascii=False)
    enc = encrypt_text(rec_json)
    enc_b64 = base64.b64encode(enc).decode()

    # Compute HMAC if key present
    hmac_sig = ""
    if HMAC_KEY:
        hmac_sig = hmac.new(HMAC_KEY.encode(), enc, hashlib.sha256).hexdigest()

    payload = {
        "host": record["host"],
        "ts": record["ts"],
        "payload_b64": enc_b64,
    }
    if hmac_sig:
        payload["hmac"] = hmac_sig

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-KEY"] = API_KEY

    print("Posting to:", args.server)
    r = requests.post(args.server, json=payload, headers=headers, timeout=5)
    print("Status:", r.status_code)
    print("Response:", r.text)

if __name__ == "__main__":
    main()
