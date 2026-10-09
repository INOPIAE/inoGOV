import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    pass


class AuditMixin:
    """Gemeinsame Spalten aller Tabellen."""

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true"), nullable=False
    )
    last_modified_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    last_modified_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)


class User(AuditMixin, Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    otp_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    otp_secret: Mapped[str | None] = mapped_column(String(255))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    unsuccessful_logins: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0"), nullable=False
    )
    blocked: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Role(AuditMixin, Base):
    __tablename__ = "role"

    rolename: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


class UserRole(AuditMixin, Base):
    __tablename__ = "user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("role.id"), nullable=False)


class Sprache(AuditMixin, Base):
    __tablename__ = "sprache"

    sprache: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    sprache_land: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    sprache2: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    sprache3: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    sprache5: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)


class Kreis(AuditMixin, Base):
    __tablename__ = "kreis"

    gov_id: Mapped[str | None] = mapped_column(String(20))
    addition: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(String)


class Kreisname(AuditMixin, Base):
    __tablename__ = "kreisname"

    kreis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kreis.id"), nullable=False)
    sprache_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sprache.id"), nullable=False)
    kreisname: Mapped[str] = mapped_column(String(50), nullable=False)


class Ort(AuditMixin, Base):
    __tablename__ = "ort"

    kreis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("kreis.id"))
    gov_id: Mapped[str | None] = mapped_column(String(20))
    lon: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    addition: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(String)


class Ortsname(AuditMixin, Base):
    __tablename__ = "ortsname"

    ort_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ort.id"), nullable=False)
    sprache_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sprache.id"), nullable=False)
    ortsname: Mapped[str] = mapped_column(String(255), nullable=False)


class MapReference(AuditMixin, Base):
    __tablename__ = "map_reference"

    ort_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ort.id"), nullable=False)
    koordinate: Mapped[str | None] = mapped_column(String(2))
    karte: Mapped[str | None] = mapped_column(String(10))


class MapImage(AuditMixin, Base):
    """Eine Kartenabbildung; Bildgröße und Dateiname gelten für alle Planquadrate der Karte."""

    __tablename__ = "map_image"

    karte: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    width_px: Mapped[int] = mapped_column(Integer, nullable=False)
    height_px: Mapped[int] = mapped_column(Integer, nullable=False)


class MapGrid(AuditMixin, Base):
    """Planquadrat einer Karte; Verknüpfung zu map_reference über (karte, koordinate)."""

    __tablename__ = "map_grid"
    __table_args__ = (Index("ix_map_grid_karte_koordinate", "karte", "koordinate"),)

    karte: Mapped[str] = mapped_column(ForeignKey("map_image.karte"), nullable=False)
    koordinate: Mapped[str] = mapped_column(String(10), nullable=False)
    x1: Mapped[int] = mapped_column(Integer, nullable=False)
    y1: Mapped[int] = mapped_column(Integer, nullable=False)
    x2: Mapped[int] = mapped_column(Integer, nullable=False)
    y2: Mapped[int] = mapped_column(Integer, nullable=False)
    breite_px: Mapped[int] = mapped_column(Integer, nullable=False)
    hoehe_px: Mapped[int] = mapped_column(Integer, nullable=False)
    laenge_von: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    laenge_bis: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    breite_von: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    breite_bis: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
