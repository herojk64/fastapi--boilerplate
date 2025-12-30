import os
from dotenv import load_dotenv
import warnings
import bcrypt
import hashlib

load_dotenv()

# Do not raise at import time; allow runtime to validate secret presence.
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    warnings.warn("SECRET_KEY not found in environment variables; using empty secret (insecure)")

# Bcrypt work factor (salt rounds)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


def _prehash(password: str) -> bytes:
    """Pre-hash password+secret with SHA-256 to avoid bcrypt 72-byte limit.

    Returns raw bytes suitable for bcrypt.hashpw/checkpw.
    """
    secret_password = (password + SECRET_KEY).encode("utf-8")
    return hashlib.sha256(secret_password).digest()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly.

    Uses SHA-256 pre-hash to produce a fixed-length input for bcrypt.
    Returns the bcrypt hash as a UTF-8 string for storage.
    """
    pre = _prehash(password)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(pre, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    pre = _prehash(password)
    try:
        return bcrypt.checkpw(pre, hashed_password.encode("utf-8"))
    except ValueError:
        return False
