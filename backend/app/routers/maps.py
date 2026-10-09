from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import read_access
from app.models import MapGrid, MapImage

router = APIRouter(prefix="/maps", tags=["maps"], dependencies=[Depends(read_access)])


class ImageOut(BaseModel):
    filename: str
    width_px: int
    height_px: int


class AreaOut(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class ExtentOut(BaseModel):
    lon_from: float
    lon_to: float
    lat_from: float
    lat_to: float


class SquareOut(BaseModel):
    karte: str
    koordinate: str
    image: ImageOut
    area: AreaOut
    extent: ExtentOut


@router.get("/{karte}/{koordinate}", response_model=SquareOut)
def get_square(karte: str, koordinate: str, db: Session = Depends(get_db)):
    """Planquadrat samt Bildinformationen; Zuordnung zu map_reference über Karte und Koordinate."""
    image = db.scalar(
        select(MapImage).where(func.lower(MapImage.karte) == karte.lower(), MapImage.active)
    )
    grid = db.scalar(
        select(MapGrid)
        .where(
            func.lower(MapGrid.karte) == karte.lower(),
            func.lower(MapGrid.koordinate) == koordinate.lower(),
            MapGrid.active,
        )
        .order_by(MapGrid.created_on.desc())
        .limit(1)
    )
    if image is None or grid is None:
        raise HTTPException(status_code=404, detail="Planquadrat nicht gefunden")
    return SquareOut(
        karte=image.karte,
        koordinate=grid.koordinate,
        image=ImageOut(filename=image.filename, width_px=image.width_px, height_px=image.height_px),
        area=AreaOut(x1=grid.x1, y1=grid.y1, x2=grid.x2, y2=grid.y2),
        extent=ExtentOut(
            lon_from=float(grid.laenge_von),
            lon_to=float(grid.laenge_bis),
            lat_from=float(grid.breite_von),
            lat_to=float(grid.breite_bis),
        ),
    )
