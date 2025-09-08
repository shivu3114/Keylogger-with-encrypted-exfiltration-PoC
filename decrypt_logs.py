#!/usr/bin/env python3
"""
Usage:
  python decrypt_logs.py logs/log_20250901_191022.txt.enc
  python decrypt_logs.py "logs/*.enc"
"""
import argparse
import glob
import sys
from crypto_utils import get_fernet

def decrypt_file(path):
    f = get_fernet()
    data = open(path, "rb").read()
    try:
        return f.decrypt(data).decode(errors="replace")
    except Exception as e:
        return f"<DECRYPTION ERROR: {e}>"

def main():
    ap = argparse.ArgumentParser(description="Decrypt one or more encrypted log files.")
    ap.add_argument("paths", nargs="+", help="One or more file paths or glob patterns")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        files.extend(sorted(glob.glob(p)))
    if not files:
        print("No files matched.", file=sys.stderr)
        sys.exit(2)

    for path in files:
        print("="*60)
        print(f"File: {path}")
        print("-"*60)
        print(decrypt_file(path))
        print()

if __name__ == "__main__":
    main()
