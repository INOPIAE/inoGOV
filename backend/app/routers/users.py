import uuid
from datetime import timedelta

import pyotp
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user, get_current_user_any, get_roles, needs_otp_setup, require_admin
from app.models import Role, User, UserRole
from app.otp import OtpStart, finish_setup, start_setup
from app.routers.account import send_link
from app.schemas import (
    OtpConfirm,
    OtpPassword,
    PasswordChange,
    ProfileUpdate,
    UserCreate,
    UserInvite,
    UserOut,
    UserUpdate,
)
from app.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


def to_out(db: Session, user: User) -> UserOut:
    out = UserOut.model_validate(user)
    out.roles = get_roles(db, user.id)
    out.pending = user.hashed_password is None
    out.otp_setup_required = needs_otp_setup(db, user)
    return out


def send_admin_link(kind: str, user: User, tasks: BackgroundTasks) -> None:
    hours = settings.admin_link_hours
    send_link(kind, user, timedelta(hours=hours), f"{hours} h", tasks)


def check_password_and_otp(user: User, data: OtpPassword) -> None:
    if not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Passwort falsch")
    if user.otp_enabled and not (data.otp and pyotp.TOTP(user.otp_secret).verify(data.otp)):
        raise HTTPException(status_code=400, detail="OTP-Code falsch")


def set_roles(db: Session, user: User, names: list[str], actor_id: uuid.UUID) -> None:
    roles = db.scalars(select(Role).where(Role.rolename.in_(names), Role.active)).all()
    missing = set(names) - {r.rolename for r in roles}
    if missing:
        raise HTTPException(status_code=422, detail=f"Unbekannte Rollen: {sorted(missing)}")
    db.execute(delete(UserRole).where(UserRole.user_id == user.id))
    db.add_all(UserRole(user_id=user.id, role_id=r.id, created_by=actor_id) for r in roles)


def get_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user_any), db: Session = Depends(get_db)):
    return to_out(db, user)


@router.patch("/me", response_model=UserOut)
def update_me(data: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    changes = data.model_dump(exclude_unset=True, exclude={"current_password"})
    new_email = changes.pop("email", None)

    if "first_name" in changes or "last_name" in changes:
        merged = {"first_name": user.first_name, "last_name": user.last_name, **changes}
        if not (merged["first_name"] or merged["last_name"]):
            raise HTTPException(status_code=422, detail="Vor- oder Nachname erforderlich")

    # E-Mail-Adresse dient dem Passwort-Reset, daher nur mit aktuellem Passwort änderbar
    if new_email and new_email.lower() != user.email.lower():
        if not data.current_password or not user.hashed_password or not verify_password(
            data.current_password, user.hashed_password
        ):
            raise HTTPException(status_code=400, detail="Passwort falsch")
        changes["email"] = new_email

    for field, value in changes.items():
        setattr(user, field, value)
    user.last_modified_by = user.id
    db.commit()
    return to_out(db, user)


@router.put("/me/password", status_code=204)
def change_password(
    data: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    if not user.hashed_password or not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Aktuelles Passwort falsch")
    user.hashed_password = hash_password(data.new_password)
    user.last_modified_by = user.id
    db.commit()
    return Response(status_code=204)


@router.get("", response_model=list[UserOut])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.username)).all()
    return [to_out(db, u) for u in users]


@router.post("", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(User.id).where(User.username == data.username)):
        raise HTTPException(status_code=409, detail="Benutzername bereits vergeben")
    user = User(
        username=data.username,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hash_password(data.password),
        created_by=admin.id,
    )
    db.add(user)
    db.flush()
    set_roles(db, user, data.roles, admin.id)
    db.commit()
    return to_out(db, user)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return to_out(db, get_or_404(db, user_id))


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_or_404(db, user_id)
    changes = data.model_dump(exclude_unset=True)

    if user.id == admin.id and (
        changes.get("active") is False
        or changes.get("blocked") is True
        or ("roles" in changes and "admin" not in (changes["roles"] or []))
    ):
        raise HTTPException(status_code=400, detail="Eigenen Admin-Zugang nicht entziehbar")

    if changes.get("password"):
        user.hashed_password = hash_password(changes.pop("password"))
    else:
        changes.pop("password", None)
    if "roles" in changes:
        roles = changes.pop("roles")
        if roles is not None:
            set_roles(db, user, roles, admin.id)
    if changes.get("blocked") is False:
        user.unsuccessful_logins = 0
        user.blocked_until = None
    for field, value in changes.items():
        if value is not None:
            setattr(user, field, value)
    user.last_modified_by = admin.id
    db.commit()
    return to_out(db, user)


@router.delete("/{user_id}", status_code=204)
def deactivate_user(user_id: uuid.UUID, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = get_or_404(db, user_id)
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Eigenen Benutzer nicht deaktivierbar")
    user.active = False
    user.last_modified_by = admin.id
    db.commit()
    return Response(status_code=204)


@router.post("/invite", response_model=UserOut, status_code=201)
def invite_user(
    data: UserInvite,
    tasks: BackgroundTasks,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = User(
        username=f"invited-{uuid.uuid4().hex[:12]}",
        email=data.email,
        created_by=admin.id,
    )
    db.add(user)
    db.flush()
    set_roles(db, user, data.roles, admin.id)
    db.commit()
    send_admin_link("invite", user, tasks)
    return to_out(db, user)


@router.post("/{user_id}/reset-password", status_code=204)
def admin_reset_password(
    user_id: uuid.UUID,
    tasks: BackgroundTasks,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    user = get_or_404(db, user_id)
    send_admin_link("invite" if user.hashed_password is None else "admin_reset", user, tasks)
    return Response(status_code=204)


@router.post("/{user_id}/reset-otp", status_code=204)
def admin_reset_otp(
    user_id: uuid.UUID,
    tasks: BackgroundTasks,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    send_admin_link("otp_reset", get_or_404(db, user_id), tasks)
    return Response(status_code=204)


@router.post("/me/otp/start", response_model=OtpStart)
def otp_start(data: OtpPassword, user: User = Depends(get_current_user_any)):
    check_password_and_otp(user, data)
    return start_setup(user)


@router.post("/me/otp/confirm", status_code=204)
def otp_confirm(data: OtpConfirm, user: User = Depends(get_current_user_any), db: Session = Depends(get_db)) -> Response:
    finish_setup(user, data.setup_token, data.code)
    db.commit()
    return Response(status_code=204)


@router.post("/me/otp/disable", status_code=204)
def otp_disable(data: OtpPassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    if "admin" in get_roles(db, user.id):
        raise HTTPException(status_code=403, detail="Administratoren können OTP nicht deaktivieren")
    check_password_and_otp(user, data)
    user.otp_enabled = False
    user.otp_secret = None
    user.last_modified_by = user.id
    db.commit()
    return Response(status_code=204)
