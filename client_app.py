import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import json
import base64
import os
import socket
import hmac
import hashlib
from datetime import datetime
import requests

from crypto_utils import encrypt_text

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SERVER_URL = "http://127.0.0.1:5000/upload"

# Load secrets from environment (recommended)
API_KEY = os.getenv("API_KEY", "")
HMAC_KEY = os.getenv("HMAC_KEY", "")


class ConsentLoggerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Consent-Only Input Logger Lab")
        self.geometry("800x520")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.buffer = []
        self.queue = queue.Queue()
        self.stop_event = threading.Event()

        self.create_widgets()
        self.bind_all("<Control-Shift-q>", self.kill_switch)  # Ctrl+Shift+Q

        self.flush_thread = threading.Thread(
            target=self._background_flush_loop, daemon=True
        )
        self.flush_thread.start()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        info = """Type into the box below. Only this text box is recorded.
Press Ctrl+Shift+Q to stop and close.
Ethical Notice: Do not use this to monitor others without explicit consent."""
        ttk.Label(frm, text=info, wraplength=760, justify="left").pack(
            anchor="w", pady=(0, 8)
        )

        self.text = tk.Text(frm, height=18)
        self.text.pack(fill="both", expand=True)

        self.text.bind("<KeyPress>", self.on_keypress)

        btn_row = ttk.Frame(frm)
        btn_row.pack(fill="x", pady=8)
        ttk.Button(btn_row, text="Flush Now", command=self.flush_now).pack(side="left")
        ttk.Button(
            btn_row, text="Clear Text", command=lambda: self.text.delete("1.0", "end")
        ).pack(side="left", padx=6)
        ttk.Button(
            btn_row, text="Quit (Kill Switch)", command=self.safe_quit
        ).pack(side="right")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var).pack(anchor="w")

    def on_keypress(self, event):
        # Record printable keys into the buffer
        ch = event.char
        if ch and ch.isprintable():
            self.buffer.append(ch)
        elif event.keysym == "space":
            self.buffer.append(" ")
        elif event.keysym == "Return":
            self.buffer.append("\n")
        # else: ignore control keys

    def _background_flush_loop(self):
        while not self.stop_event.is_set():
            try:
                self._flush()
            except Exception as e:
                # Update status but keep running
                self.status_var.set(f"Flush error: {e}")
            time.sleep(5)

    def _flush(self):
        if not self.buffer:
            return
        text = "".join(self.buffer)
        self.buffer.clear()

        # Timestamped entry with minimal context
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "host": socket.gethostname(),
            "text": text,
        }
        record_json = json.dumps(record, ensure_ascii=False)

        enc_bytes = encrypt_text(record_json)

        # Save encrypted log locally
        fname = f"log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt.enc"
        fpath = os.path.join(LOG_DIR, fname)
        with open(fpath, "wb") as f:
            f.write(enc_bytes)

        # Build payload
        payload = {
            "host": socket.gethostname(),
            "ts": record["ts"],
            "payload_b64": base64.b64encode(enc_bytes).decode(),
        }

        # Optional HMAC signing
        if HMAC_KEY:
            sig = hmac.new(HMAC_KEY.encode(), enc_bytes, hashlib.sha256).hexdigest()
            payload["hmac"] = sig

        # Optional API Key in headers
        headers = {}
        if API_KEY:
            headers["X-API-KEY"] = API_KEY

        try:
            r = requests.post(SERVER_URL, json=payload, timeout=3, headers=headers)
            if r.ok:
                self.status_var.set(f"Flushed {fname} (local+server)")
            else:
                self.status_var.set(f"Server rejected: {r.text}")
        except requests.RequestException as e:
            self.status_var.set(f"Server unavailable: {e}")

    def flush_now(self):
        try:
            self._flush()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def kill_switch(self, event=None):
        self.safe_quit()

    def safe_quit(self):
        self.stop_event.set()
        self.after(200, self.on_close)

    def on_close(self):
        # Final flush attempt
        try:
            self._flush()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = ConsentLoggerApp()
    app.mainloop()
