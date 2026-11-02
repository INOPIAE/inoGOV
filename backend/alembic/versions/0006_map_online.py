"""Add online maps and per-place regional map assignments.

Revision ID: 0006
Revises: 0005
"""
import uuid

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

U75_ID = uuid.UUID("00000000-0000-0000-0000-000000000075")
U100_ID = uuid.UUID("00000000-0000-0000-0000-000000000100")
OSM_ID = uuid.UUID("00000000-0000-0000-0000-0000000000a0")
GM_ID = uuid.UUID("00000000-0000-0000-0000-0000000000b0")
U75_EXCEPTIONS = {"a1", "b1", "c1", "f1", "f2", "e3", "g1", "g2", "g3", "g4", "g5", "f5", "g6", "d6", "d3"}

ONLINE_MAPS = [
    {
        "id": U75_ID,
        "mapname": "Ukraine 75000",
        "map_short": "U75",
        "map_url_basis": "https://etomesto.com/map-ukraine_spezialkarte-uk-750/",
        "map_url_pattern": "?y={lat}&x={lon}",
        "global": False,
    },
    {
        "id": U100_ID,
        "mapname": "Ukraine 100000",
        "map_short": "U100",
        "map_url_basis": "https://etomesto.com/map-ukraine_zapad/",
        "map_url_pattern": "?y={lat}&x={lon}",
        "global": False,
    },
    {
        "id": OSM_ID,
        "mapname": "OpenStreetMap",
        "map_short": "OSM",
        "map_url_basis": "https://www.openstreetmap.org/",
        "map_url_pattern": "?mlat={lat}&mlon={lon}#map=9/{lat}/{lon}",
        "global": True,
    },
    {
        "id": GM_ID,
        "mapname": "Google",
        "map_short": "GM",
        "map_url_basis": "https://google.com/maps",
        "map_url_pattern": "?q={lat},{lon}&ll={lat},{lon}&z=12",
        "global": True,
    },
]


def upgrade() -> None:
    op.create_table(
        "map_online",
        sa.Column("mapname", sa.String(length=50), nullable=False),
        sa.Column("map_short", sa.String(length=10), nullable=False),
        sa.Column("map_url_basis", sa.String(length=255), nullable=False),
        sa.Column("map_url_pattern", sa.String(length=255), nullable=False),
        sa.Column("global", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_modified_on", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_by", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mapname"),
        sa.UniqueConstraint("map_short"),
    )
    op.create_table(
        "regional_map",
        sa.Column("ort_id", sa.Uuid(), nullable=False),
        sa.Column("map_online_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_modified_on", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["ort_id"], ["ort.id"]),
        sa.ForeignKeyConstraint(["map_online_id"], ["map_online.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ort_id", "map_online_id", name="uq_regional_map_ort_map"),
    )
    op.create_index("ix_regional_map_ort_id", "regional_map", ["ort_id"], unique=False)

    map_online = sa.table(
        "map_online",
        sa.column("id", sa.Uuid()),
        sa.column("mapname", sa.String()),
        sa.column("map_short", sa.String()),
        sa.column("map_url_basis", sa.String()),
        sa.column("map_url_pattern", sa.String()),
        sa.column("global", sa.Boolean()),
    )
    op.bulk_insert(map_online, ONLINE_MAPS)

    map_reference = sa.table(
        "map_reference",
        sa.column("ort_id", sa.Uuid()),
        sa.column("karte", sa.String()),
        sa.column("koordinate", sa.String()),
        sa.column("active", sa.Boolean()),
    )
    ort = sa.table(
        "ort",
        sa.column("id", sa.Uuid()),
        sa.column("lat", sa.Numeric()),
        sa.column("lon", sa.Numeric()),
        sa.column("active", sa.Boolean()),
    )
    regional_map = sa.table(
        "regional_map",
        sa.column("id", sa.Uuid()),
        sa.column("ort_id", sa.Uuid()),
        sa.column("map_online_id", sa.Uuid()),
    )

    assignments: set[tuple[uuid.UUID, uuid.UUID]] = set()
    bind = op.get_bind()
    references = bind.execute(
        sa.select(map_reference.c.ort_id, map_reference.c.karte, map_reference.c.koordinate)
        .join(ort, ort.c.id == map_reference.c.ort_id)
        .where(map_reference.c.active.is_(True), ort.c.active.is_(True))
    )
    for ort_id, karte, koordinate in references:
        normalized_map = (karte or "").casefold()
        if normalized_map == "stumpp":
            assignments.add((ort_id, U100_ID))
        elif normalized_map == "lück":
            assignments.add((ort_id, U100_ID))
            if (koordinate or "").casefold() not in U75_EXCEPTIONS:
                assignments.add((ort_id, U75_ID))

    coordinate_places = bind.execute(
        sa.select(ort.c.id).where(ort.c.active.is_(True), ort.c.lat.is_not(None), ort.c.lon.is_not(None))
    )
    for (ort_id,) in coordinate_places:
        assignments.add((ort_id, OSM_ID))
        assignments.add((ort_id, GM_ID))

    if assignments:
        op.bulk_insert(
            regional_map,
            [
                {"id": uuid.uuid4(), "ort_id": ort_id, "map_online_id": map_id}
                for ort_id, map_id in sorted(assignments, key=lambda pair: (str(pair[0]), str(pair[1])))
            ],
        )


def downgrade() -> None:
    op.drop_index("ix_regional_map_ort_id", table_name="regional_map")
    op.drop_table("regional_map")
    op.drop_table("map_online")