import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import settings

_hasher = PasswordHash.recommended()
DUMMY_HASH = _hasher.hash("dummy-password")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _hasher.verify(password, hashed)


def create_access_token(user_id: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expires}, settings.secret_key, algorithm="HS256")


def fingerprint(user) -> str:
    """Ändert sich mit Passwort, OTP oder Benutzername und macht Links damit einmalig."""
    raw = f"{user.hashed_password}|{user.otp_secret}|{user.otp_enabled}|{user.username}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def create_link_token(user, purpose: str, lifetime: timedelta) -> str:
    claims = {
        "sub": str(user.id),
        "purpose": purpose,
        "fp": fingerprint(user),
        "exp": datetime.now(UTC) + lifetime,
    }
    return jwt.encode(claims, settings.secret_key, algorithm="HS256")


def create_signed(claims: dict, lifetime: timedelta) -> str:
    return jwt.encode(
        {**claims, "exp": datetime.now(UTC) + lifetime}, settings.secret_key, algorithm="HS256"
    )


def decode_signed(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise ValueError("invalid token") from exc
