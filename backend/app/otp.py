import uuid
from datetime import timedelta

import pyotp
from fastapi import HTTPException
from pydantic import BaseModel

from app.config import settings
from app.models import User
from app.security import create_signed, decode_signed

SETUP_MINUTES = 10


class OtpStart(BaseModel):
    secret: str
    uri: str
    setup_token: str


def start_setup(user: User) -> OtpStart:
    secret = pyotp.random_base32()
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.username or user.email, issuer_name=settings.app_name
    )
    token = create_signed(
        {"sub": str(user.id), "purpose": "otp_setup", "secret": secret},
        timedelta(minutes=SETUP_MINUTES),
    )
    return OtpStart(secret=secret, uri=uri, setup_token=token)


def finish_setup(user: User, setup_token: str, code: str) -> None:
    """Speichert das Secret erst nach gültigem Code."""
    try:
        claims = decode_signed(setup_token)
        valid = claims["purpose"] == "otp_setup" and uuid.UUID(claims["sub"]) == user.id
        secret = claims["secret"]
    except (ValueError, KeyError):
        valid = False
    if not valid:
        raise HTTPException(status_code=400, detail="Einrichtung abgelaufen, bitte neu starten")
    if not pyotp.TOTP(secret).verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Code falsch")
    user.otp_secret = secret
    user.otp_enabled = True
    user.last_modified_by = user.id
