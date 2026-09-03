from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    data: dict,
    expires_minutes: int = 30
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm="HS256"
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"]
    )