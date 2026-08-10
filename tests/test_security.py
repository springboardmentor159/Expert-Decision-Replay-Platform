from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_token


def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "1"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "1"


def test_verify_token_valid():
    token = create_access_token({"sub": "2"})
    assert verify_token(token)["sub"] == "2"


def test_verify_token_invalid_returns_empty():
    assert verify_token("not-a-jwt") == {}


def test_verify_token_expired():
    token = create_access_token(
        {"sub": "3"},
        expires_delta=timedelta(seconds=-1),
    )
    assert verify_token(token) == {}
