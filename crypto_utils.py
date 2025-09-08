import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

_KEY_ENV = "FERNET_KEY"

def get_key() -> bytes:
    key = os.getenv(_KEY_ENV, "").strip()
    if not key:
        raise RuntimeError(f"Missing {_KEY_ENV} in environment (.env).")
    # Validate base64 urlsafe key length for Fernet
    try:
        base64.urlsafe_b64decode(key)
    except Exception as e:
        raise RuntimeError("FERNET_KEY is not valid urlsafe base64.") from e
    return key.encode()

def get_fernet() -> Fernet:
    return Fernet(get_key())

def encrypt_text(plain: str) -> bytes:
    f = get_fernet()
    return f.encrypt(plain.encode())

def decrypt_bytes(ct: bytes) -> str:
    f = get_fernet()
    try:
        return f.decrypt(ct).decode()
    except InvalidToken as e:
        raise RuntimeError("Invalid encryption key or corrupted data.") from e
