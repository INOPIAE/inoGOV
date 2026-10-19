import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Sprache
class SpracheIn(BaseModel):
    sprache: str = Field(min_length=1, max_length=30)
    sprache_land: str = Field(min_length=1, max_length=30)
    sprache2: str = Field(min_length=2, max_length=2)
    sprache3: str = Field(min_length=3, max_length=3)
    sprache5: str = Field(min_length=5, max_length=5)


class SpracheUpdate(BaseModel):
    sprache: str | None = Field(default=None, min_length=1, max_length=30)
    sprache_land: str | None = Field(default=None, min_length=1, max_length=30)
    sprache2: str | None = Field(default=None, min_length=2, max_length=2)
    sprache3: str | None = Field(default=None, min_length=3, max_length=3)
    sprache5: str | None = Field(default=None, min_length=5, max_length=5)


class SpracheOut(ORM, SpracheIn):
    id: uuid.UUID


# Kreis
class KreisnameIn(BaseModel):
    sprache_id: uuid.UUID
    kreisname: str = Field(min_length=1, max_length=50)


class KreisnameOut(ORM):
    id: uuid.UUID
    sprache_id: uuid.UUID
    kreisname: str


class KreisCreate(BaseModel):
    gov_id: str | None = Field(default=None, max_length=20)
    addition: str | None = Field(default=None, max_length=255)
    comment: str | None = None
    namen: list[KreisnameIn] = []


class KreisUpdate(BaseModel):
    gov_id: str | None = Field(default=None, max_length=20)
    addition: str | None = Field(default=None, max_length=255)
    comment: str | None = None


class KreisOut(ORM):
    id: uuid.UUID
    gov_id: str | None
    addition: str | None
    comment: str | None
    namen: list[KreisnameOut] = []


# Ort
class OrtsnameIn(BaseModel):
    sprache_id: uuid.UUID
    ortsname: str = Field(min_length=1, max_length=255)


class OrtsnameOut(ORM):
    id: uuid.UUID
    sprache_id: uuid.UUID
    ortsname: str


class KarteIn(BaseModel):
    koordinate: str | None = Field(default=None, max_length=2)
    karte: str | None = Field(default=None, max_length=10)


class KarteOut(ORM):
    id: uuid.UUID
    ort_id: uuid.UUID
    koordinate: str | None
    karte: str | None


class OrtCreate(BaseModel):
    kreis_id: uuid.UUID | None = None
    gov_id: str | None = Field(default=None, max_length=20)
    lon: Decimal | None = Field(default=None, ge=-180, le=180, max_digits=9, decimal_places=6)
    lat: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=9, decimal_places=6)
    addition: str | None = Field(default=None, max_length=255)
    comment: str | None = None
    namen: list[OrtsnameIn] = []
    karten: list[KarteIn] = []


class OrtUpdate(BaseModel):
    kreis_id: uuid.UUID | None = None
    gov_id: str | None = Field(default=None, max_length=20)
    lon: Decimal | None = Field(default=None, ge=-180, le=180, max_digits=9, decimal_places=6)
    lat: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=9, decimal_places=6)
    addition: str | None = Field(default=None, max_length=255)
    comment: str | None = None


class OrtOut(ORM):
    id: uuid.UUID
    kreis_id: uuid.UUID | None
    gov_id: str | None
    lon: Decimal | None
    lat: Decimal | None
    addition: str | None
    comment: str | None
    namen: list[OrtsnameOut] = []
    karten: list[KarteOut] = []

class OrtStatistics(ORM):
    total: int
    gov: int
    geo: int
