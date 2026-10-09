import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import require_admin
from app.imports import IMPORTS
from app.imports.common import ImportAborted, archive, decode, parse_csv, protocol_text
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/imports", tags=["imports"])


class ImportInfo(BaseModel):
    key: str
    columns: list[str]


class RowErrorOut(BaseModel):
    line: int
    code: str
    message: str
    values: list[str]


class CreatedKreis(BaseModel):
    id: str
    name: str


class ImportReport(BaseModel):
    key: str
    filename: str | None
    total: int
    imported: int
    failed: int
    errors: list[RowErrorOut]
    created_kreise: list[CreatedKreis]
    archived_as: str | None
    archive_failed: bool


@router.get("", response_model=list[ImportInfo])
def list_imports(_: User = Depends(require_admin)):
    return [ImportInfo(key=i.key, columns=i.columns) for i in IMPORTS.values()]


@router.post("/{key}", response_model=ImportReport)
def run_import(
    key: str,
    file: UploadFile,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    importer = IMPORTS.get(key)
    if importer is None:
        raise HTTPException(status_code=404, detail="Import nicht gefunden")

    limit = settings.import_max_mb * 1024 * 1024
    raw = file.file.read(limit + 1)
    if len(raw) > limit:
        raise HTTPException(status_code=413, detail="Datei zu groß")
    try:
        rows = parse_csv(decode(raw))
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="Datei kann nicht gelesen werden")

    try:
        result = importer.run(db, rows, admin.id)
    except ImportAborted as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=exc.code)
    db.commit()

    archived_as, archive_failed = None, False
    try:
        archived_as = archive(raw, key, file.filename, protocol_text(key, file.filename or "", result))
    except OSError:
        logger.exception("Import %s: Datei konnte nicht abgelegt werden", key)
        archive_failed = True

    return ImportReport(
        key=key,
        filename=file.filename,
        total=result.total,
        imported=result.imported,
        failed=len(result.errors),
        errors=result.errors,
        created_kreise=result.created_kreise,
        archived_as=archived_as,
        archive_failed=archive_failed,
    )
