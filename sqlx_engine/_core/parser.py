from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from pydantic import Json, create_model

from .common import BaseRow

TYPES = {
    "int": int,
    "bigint": int,
    "float": float,
    "double": float,
    "string": str,
    "bool": bool,
    "char": str,
    "decimal": Decimal,
    "json": Json,
    "uuid": UUID,
    "datetime": datetime,
    "date": date,
    "time": time,
    "array": list,
    "xml": str,
    # not implement
    "bytes": Any,  # bytes
    "enum": Any,  # Enum
    "null": Any,
}


class Deserialize:
    __slots__ = ("rows", "as_base_row", "_model", "_base_model_type")

    def __init__(self, rows: List[Dict[str, Any]], as_base_row: bool = True) -> None:
        self.rows = rows
        self.as_base_row = as_base_row
        self._model: BaseRow = None
        self._base_model_type: dict = {}

    def deserialize(self):
        if self.as_base_row:
            self._create_base_types(self.rows[0])
        mapper = map(self._get_row, self.rows)
        if not self.as_base_row:
            return mapper
        return map(self._to_model, mapper)

    def _to_model(self, row: dict) -> BaseRow:
        return self._model(**row)

    def _create_base_types(self, first_row: dict):
        for key in first_row.keys():
            _type = TYPES.get(first_row[key]["prisma__type"], Any)
            self._base_model_type.update({key: (_type, None)})
        self._create_model()

    def _create_model(self) -> None:
        _model = create_model("BaseRow", **self._base_model_type)
        self._model = _model

    def _get_row(self, row: dict):
        mapper = {}
        for key in row.keys():
            mapper.update({key: row[key]["prisma__value"]})
        return mapper
