import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import read_access, require_editor
from app.models import Kreis, Kreisname, User
from app.routers.common import apply_changes, ensure_sprache, get_active
from app.schemas_geo import KreisCreate, KreisnameIn, KreisnameOut, KreisOut, KreisUpdate

router = APIRouter(prefix="/kreise", tags=["kreise"])


def to_out(db: Session, kreise: list[Kreis]) -> list[KreisOut]:
    names = db.scalars(
        select(Kreisname).where(Kreisname.kreis_id.in_([k.id for k in kreise]), Kreisname.active)
    ).all()
    result = []
    for kreis in kreise:
        out = KreisOut.model_validate(kreis)
        out.namen = [KreisnameOut.model_validate(n) for n in names if n.kreis_id == kreis.id]
        result.append(out)
    return result


@router.get("", response_model=list[KreisOut], dependencies=[Depends(read_access)])
def list_kreise(
    q: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Kreis).where(Kreis.active)
    if q:
        matching = select(Kreisname.kreis_id).where(
            Kreisname.active, Kreisname.kreisname.icontains(q, autoescape=True)
        )
        stmt = stmt.where(Kreis.id.in_(matching))
    kreise = db.scalars(stmt.order_by(Kreis.gov_id, Kreis.id).limit(limit).offset(offset)).all()
    return to_out(db, list(kreise))


@router.get("/{kreis_id}", response_model=KreisOut, dependencies=[Depends(read_access)])
def get_kreis(kreis_id: uuid.UUID, db: Session = Depends(get_db)):
    return to_out(db, [get_active(db, Kreis, kreis_id, "Kreis")])[0]


@router.post("", response_model=KreisOut, status_code=201)
def create_kreis(data: KreisCreate, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    for name in data.namen:
        ensure_sprache(db, name.sprache_id)
    kreis = Kreis(**data.model_dump(exclude={"namen"}), created_by=user.id)
    db.add(kreis)
    db.flush()
    db.add_all(Kreisname(kreis_id=kreis.id, created_by=user.id, **n.model_dump()) for n in data.namen)
    db.commit()
    return to_out(db, [kreis])[0]


@router.patch("/{kreis_id}", response_model=KreisOut)
def update_kreis(
    kreis_id: uuid.UUID,
    data: KreisUpdate,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    kreis = get_active(db, Kreis, kreis_id, "Kreis")
    apply_changes(kreis, data.model_dump(exclude_unset=True), user.id)
    db.commit()
    return to_out(db, [kreis])[0]


@router.delete("/{kreis_id}", status_code=204)
def delete_kreis(kreis_id: uuid.UUID, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    apply_changes(get_active(db, Kreis, kreis_id, "Kreis"), {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)


@router.post("/{kreis_id}/namen", response_model=KreisnameOut, status_code=201)
def add_name(
    kreis_id: uuid.UUID,
    data: KreisnameIn,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    get_active(db, Kreis, kreis_id, "Kreis")
    ensure_sprache(db, data.sprache_id)
    name = Kreisname(kreis_id=kreis_id, created_by=user.id, **data.model_dump())
    db.add(name)
    db.commit()
    return name


@router.delete("/{kreis_id}/namen/{name_id}", status_code=204)
def delete_name(
    kreis_id: uuid.UUID,
    name_id: uuid.UUID,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    name = get_active(db, Kreisname, name_id, "Kreisname")
    if name.kreis_id != kreis_id:
        raise HTTPException(status_code=404, detail="Kreisname nicht gefunden")
    apply_changes(name, {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)
