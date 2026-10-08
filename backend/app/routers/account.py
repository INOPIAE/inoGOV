import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import mail
from app.config import settings
from app.database import get_db
from app.models import User
from app.otp import OtpStart, finish_setup, start_setup
from app.routers.auth import TokenResponse
from app.schemas import clean_name
from app.security import (
    create_access_token,
    create_link_token,
    decode_signed,
    fingerprint,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

PATHS = {"reset": "/reset-password", "admin_reset": "/reset-password", "invite": "/setup-account", "otp_reset": "/otp-setup"}


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class SetupAccount(BaseModel):
    token: str
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)

    _clean = field_validator("first_name", "last_name", mode="before")(clean_name)

    @model_validator(mode="after")
    def need_a_name(self):
        if not (self.first_name or self.last_name):
            raise ValueError("first_name or last_name is required")
        return self


class LinkInfo(BaseModel):
    purpose: str
    username: str | None
    email: str
    otp_enabled: bool


class TokenOnly(BaseModel):
    token: str


class OtpConfirmByLink(BaseModel):
    token: str
    setup_token: str
    code: str


def user_from_link(db: Session, token: str, purposes: set[str]) -> tuple[User, str]:
    invalid = HTTPException(status_code=400, detail="Link ungültig oder abgelaufen")
    try:
        claims = decode_signed(token)
        purpose = claims["purpose"]
        user = db.get(User, uuid.UUID(claims["sub"]))
    except (ValueError, KeyError):
        raise invalid
    if purpose not in purposes or user is None or not user.active or user.blocked:
        raise invalid
    if claims.get("fp") != fingerprint(user):
        raise invalid
    return user, purpose


def send_link(kind: str, user: User, lifetime: timedelta, validity: str, tasks: BackgroundTasks) -> None:
    token = create_link_token(user, kind, lifetime)
    tasks.add_task(mail.send_link_mail, kind, user.email, PATHS[kind], token, validity)


@router.post("/forgot-password", status_code=204)
def forgot_password(data: ForgotPassword, tasks: BackgroundTasks, db: Session = Depends(get_db)) -> Response:
    users = db.scalars(
        select(User).where(User.email == data.email, User.active, ~User.blocked, User.hashed_password.is_not(None))
    ).all()
    minutes = settings.password_reset_minutes
    for user in users:
        send_link("reset", user, timedelta(minutes=minutes), f"{minutes} min", tasks)
    return Response(status_code=204)


@router.get("/link-info", response_model=LinkInfo)
def link_info(token: str, db: Session = Depends(get_db)):
    user, purpose = user_from_link(db, token, set(PATHS))
    pending = user.hashed_password is None
    return LinkInfo(
        purpose=purpose,
        username=None if pending else user.username,
        email=user.email,
        otp_enabled=user.otp_enabled,
    )


@router.post("/reset-password", status_code=204)
def reset_password(data: ResetPassword, db: Session = Depends(get_db)) -> Response:
    user, _ = user_from_link(db, data.token, {"reset", "admin_reset"})
    user.hashed_password = hash_password(data.new_password)
    user.unsuccessful_logins = 0
    user.blocked_until = None
    user.last_modified_by = user.id
    db.commit()
    return Response(status_code=204)


@router.post("/setup-account", response_model=TokenResponse)
def setup_account(data: SetupAccount, db: Session = Depends(get_db)) -> TokenResponse:
    user, _ = user_from_link(db, data.token, {"invite"})
    if db.scalar(select(User.id).where(User.username == data.username, User.id != user.id)):
        raise HTTPException(status_code=409, detail="Benutzername bereits vergeben")
    user.username = data.username
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.hashed_password = hash_password(data.password)
    user.last_login = datetime.now(UTC)
    user.last_modified_by = user.id
    db.commit()
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/otp/start", response_model=OtpStart)
def otp_start(data: TokenOnly, db: Session = Depends(get_db)):
    user, _ = user_from_link(db, data.token, {"otp_reset"})
    return start_setup(user)


@router.post("/otp/confirm", status_code=204)
def otp_confirm(data: OtpConfirmByLink, db: Session = Depends(get_db)) -> Response:
    user, _ = user_from_link(db, data.token, {"otp_reset"})
    finish_setup(user, data.setup_token, data.code)
    db.commit()
    return Response(status_code=204)
