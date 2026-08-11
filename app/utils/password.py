"""
Password hashing utilities.

Integrated from Jamuna Rani's branch. Provides the same bcrypt hashing
as app/utils/security.py but as a standalone module for compatibility.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt. Never store plaintext."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)
