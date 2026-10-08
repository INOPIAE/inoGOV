import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import read_access, require_admin
from app.models import Sprache, User
from app.routers.common import apply_changes, get_active
from app.schemas_geo import SpracheIn, SpracheOut, SpracheUpdate

router = APIRouter(prefix="/sprachen", tags=["sprachen"])


def commit_unique(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Sprache oder Sprachcode bereits vorhanden")


@router.get("", response_model=list[SpracheOut], dependencies=[Depends(read_access)])
def list_sprachen(db: Session = Depends(get_db)):
    return db.scalars(select(Sprache).where(Sprache.active).order_by(Sprache.sprache)).all()


@router.get("/{sprache_id}", response_model=SpracheOut, dependencies=[Depends(read_access)])
def get_sprache(sprache_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_active(db, Sprache, sprache_id, "Sprache")


@router.post("", response_model=SpracheOut, status_code=201)
def create_sprache(data: SpracheIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    sprache = Sprache(**data.model_dump(), created_by=admin.id)
    db.add(sprache)
    commit_unique(db)
    return sprache


@router.patch("/{sprache_id}", response_model=SpracheOut)
def update_sprache(
    sprache_id: uuid.UUID,
    data: SpracheUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    sprache = get_active(db, Sprache, sprache_id, "Sprache")
    apply_changes(sprache, data.model_dump(exclude_unset=True, exclude_none=True), admin.id)
    commit_unique(db)
    return sprache


@router.delete("/{sprache_id}", status_code=204)
def delete_sprache(sprache_id: uuid.UUID, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    sprache = get_active(db, Sprache, sprache_id, "Sprache")
    apply_changes(sprache, {"active": False}, admin.id)
    db.commit()
    return Response(status_code=204)
