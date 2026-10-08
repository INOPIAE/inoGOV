import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_roles, require_admin
from app.models import Role, User, UserRole
from app.schemas import PasswordChange, UserCreate, UserOut, UserUpdate
from app.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


def to_out(db: Session, user: User) -> UserOut:
    out = UserOut.model_validate(user)
    out.roles = get_roles(db, user.id)
    return out


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
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
