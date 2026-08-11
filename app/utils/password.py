"""
Password hashing utilities (Jamuna Rani integration).
Uses bcrypt directly to avoid passlib compatibility issues.
"""
import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt. Never store plaintext."""
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
