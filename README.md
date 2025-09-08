# Consent-Only Input Logger Lab (Safe PoC)
**Ethical Notice:** This project is strictly for learning *defensive security* and software engineering patterns (event capture, encryption at rest/in transit, timestamped logging, and safe "exfiltration" to a localhost server). **It does not capture global system keystrokes** and records input only inside its own window. Do not modify it to spy on others. Obtain explicit, informed consent for any monitoring in your environment.

## What this demonstrates
- Event capture limited to the app's own text box (Tkinter)
- AES-128 equivalent encryption via `cryptography.Fernet` (symmetric key)
- Timestamped, encrypted local logs
- Base64-encoded payloads
- A localhost Flask server that accepts encrypted uploads
- A kill switch: `Ctrl+Shift+Q` inside the app stops logging and closes the window

## What this **intentionally** does NOT include
- Global keylogging, OS hooks, clipboard capture
- Startup persistence or stealth features
These are harmful in real-world contexts and are excluded for safety and ethics.

---

## Project layout
```
.
├── client_app.py          # GUI app that records input typed *into this app only*
├── crypto_utils.py        # Fernet key management and helpers
├── server.py              # Local Flask receiver (simulates exfiltration)
├── requirements.txt
├── .env.example           # Example environment file for the shared key
├── logs/                  # Encrypted log files created by the client
└── server_received/       # Encrypted blobs received by the server
```

## Quick start

### 1) Create and activate a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Create a `.env` with a Fernet key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copy the printed key into a new file named `.env` in this folder:
```
FERNET_KEY=REPLACE_WITH_YOUR_KEY
```

### 4) Start the local server
In one terminal:
```bash
python server.py
```
It will listen on `http://127.0.0.1:5000`.

### 5) Run the client app
In another terminal:
```bash
python client_app.py
```
Type into the main text area. Press **Ctrl+Shift+Q** to stop and close.

### 6) Files produced
- Encrypted log files are written to `logs/` with names like `log_YYYYMMDD_HHMMSS.txt.enc`.
- The server stores received encrypted blobs in `server_received/` with timestamps.

### 7) Decrypting a log (optional)
If you want to inspect a saved log file:
```bash
python -c "from crypto_utils import get_fernet; import sys; data=open(sys.argv[1],'rb').read(); print(get_fernet().decrypt(data).decode())" logs/log_*.txt.enc
```

---

## Kill switch
Inside the app window, press **Ctrl+Shift+Q** to gracefully stop the logger and close the window.

## Notes for blue-teamers
- Try adding simple detections in `server.py` (rate limiting, header checks, or signature verification).
- Extend the client to sign payloads (HMAC) before encrypting for authenticity.
- Explore endpoint monitoring patterns in a lab: autoruns auditing (*without* creating persistence), process/network inventory, and anomaly alerts.
