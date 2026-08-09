from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a password using the recommended hashing algorithm."""
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hashed version."""
    return password_hash.verify(password, hashed_password)