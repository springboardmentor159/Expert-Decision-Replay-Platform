"""
Password hashing using bcrypt directly.

Uses the bcrypt library directly instead of passlib to avoid the
passlib+bcrypt version compatibility bug (ValueError: password cannot
be longer than 72 bytes).
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
