"""seed roles and languages

Revision ID: 0002
Revises: 6b568c961d51
"""
import uuid

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "6b568c961d51"
branch_labels = None
depends_on = None

ROLES = [
    ("admin", "Administration"),
    ("user", "Normaler Benutzer"),
]

SPRACHEN = [
    ("Deutsch", "Deutsch", "de", "deu", "de-DE"),
    ("Englisch", "English", "en", "eng", "en-GB"),
    ("Polnisch", "Polski", "pl", "pol", "pl-PL"),
    ("Russisch", "Русский", "ru", "rus", "ru-RU"),
    ("Ukrainisch", "Українська", "uk", "ukr", "uk-UA"),
]

role = sa.table(
    "role", sa.column("id", sa.Uuid), sa.column("rolename", sa.String), sa.column("description", sa.String)
)
sprache = sa.table(
    "sprache",
    sa.column("id", sa.Uuid),
    sa.column("sprache", sa.String),
    sa.column("sprache_land", sa.String),
    sa.column("sprache2", sa.String),
    sa.column("sprache3", sa.String),
    sa.column("sprache5", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        role,
        [{"id": uuid.uuid4(), "rolename": n, "description": d} for n, d in ROLES],
    )
    op.bulk_insert(
        sprache,
        [
            {"id": uuid.uuid4(), "sprache": a, "sprache_land": b, "sprache2": c, "sprache3": d, "sprache5": e}
            for a, b, c, d, e in SPRACHEN
        ],
    )


def downgrade() -> None:
    op.execute(role.delete().where(role.c.rolename.in_([n for n, _ in ROLES])))
    op.execute(sprache.delete().where(sprache.c.sprache2.in_([s[2] for s in SPRACHEN])))
