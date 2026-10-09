from dataclasses import dataclass
from typing import Callable

from app.imports import lueck


@dataclass(frozen=True)
class ImportDef:
    key: str
    columns: list[str]
    run: Callable


# Weitere Importe hier eintragen.
IMPORTS: dict[str, ImportDef] = {
    lueck.KEY: ImportDef(lueck.KEY, lueck.COLUMNS, lueck.run),
}
