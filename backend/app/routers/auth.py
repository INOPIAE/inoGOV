from datetime import UTC, datetime

import pyotp
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.lockout import lock_duration
from app.models import User
from app.security import DUMMY_HASH, create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str
    otp: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    invalid = HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")
    user = db.scalar(select(User).where(User.username == data.username, User.active))
    if user is None:
        verify_password(data.password, DUMMY_HASH)
        raise invalid

    if user.blocked:
        raise HTTPException(status_code=403, detail="Benutzer gesperrt")

    now = datetime.now(UTC)
    if user.blocked_until and _aware(user.blocked_until) > now:
        retry = int((_aware(user.blocked_until) - now).total_seconds()) + 1
        raise HTTPException(
            status_code=423,
            detail="Zu viele Fehlversuche, Anmeldung vorübergehend gesperrt",
            headers={"Retry-After": str(retry)},
        )

    ok = bool(user.hashed_password) and verify_password(data.password, user.hashed_password)
    if ok and user.otp_enabled:
        ok = bool(data.otp) and bool(user.otp_secret) and pyotp.TOTP(user.otp_secret).verify(data.otp)

    if not ok:
        user.unsuccessful_logins += 1
        duration = lock_duration(user.unsuccessful_logins, settings.lockout_tier_list)
        if duration:
            user.blocked_until = now + duration
        db.commit()
        raise invalid

    user.unsuccessful_logins = 0
    user.blocked_until = None
    user.last_login = now
    db.commit()
    return TokenResponse(access_token=create_access_token(str(user.id)))
