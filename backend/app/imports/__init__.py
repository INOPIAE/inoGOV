from dataclasses import dataclass
from typing import Callable

from app.imports import lueck, lueck_koordinaten, stumpp, stumpp_koordinaten
from app.imports.common import read_csv_rows, read_table


@dataclass(frozen=True)
class ImportDef:
    key: str
    columns: list[str]
    accepts: list[str]
    parse: Callable  # (raw: bytes, filename: str | None) -> [(Zeilennummer, Zellen)]
    run: Callable  # (db, rows, actor_id) -> ImportResult


# Weitere Importe hier eintragen.
IMPORTS: dict[str, ImportDef] = {
    lueck.KEY: ImportDef(lueck.KEY, lueck.COLUMNS, [".csv"], read_csv_rows, lueck.run),
    stumpp.KEY: ImportDef(stumpp.KEY, stumpp.COLUMNS, [".csv"], read_csv_rows, stumpp.run),
    lueck_koordinaten.KEY: ImportDef(
        lueck_koordinaten.KEY, lueck_koordinaten.COLUMNS, [".xlsx", ".csv"], read_table, lueck_koordinaten.run
    ),
    stumpp_koordinaten.KEY: ImportDef(
        stumpp_koordinaten.KEY, stumpp_koordinaten.COLUMNS, [".xlsx", ".csv"], read_table, stumpp_koordinaten.run
    ),
}
