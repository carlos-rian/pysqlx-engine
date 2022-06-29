from datetime import date, datetime, time
from decimal import Decimal
from json import loads
from typing import Any, Dict, List, Tuple
from uuid import UUID

from pydantic import create_model
from sqlx_engine.core.common import BaseRow

TYPES = {
    "int": int,
    "bigint": int,
    "float": float,
    "double": float,
    "string": str,
    "bool": bool,
    "char": str,
    "decimal": Decimal,
    "json": loads,
    "uuid": UUID,
    "datetime": datetime,
    "date": date,
    "time": time,
    "array": list,
    # not implement
    "bytes": None,  # bytes
    "enum": None,  # Enum
    "null": None,
    "xml": None,  # str
}


class Deserialize:
    def __init__(self, rows: List[Dict[str, Any]]) -> None:
        self.rows = rows
        self._model: BaseRow = None
        self._base_model_type: dict = {}

    def deserialize(self):
        return map(self._get_row, self.rows)

    def _create_model(self) -> None:
        _model = create_model("BaseRow", **self._base_model_type)
        self._model = _model

    def _get_row(self, row: dict):
        mapper = {}
        for key in row.keys():
            value, _type = self._mapping_type(**row[key])
            if not self._model:
                self._base_model_type.update({key: (_type, None)})
            mapper.update({key: value})
        if not self._model:
            self._create_model()
        return self._model.parse_obj(mapper)

    def _mapping_type(self, prisma__type: TYPES, prisma__value: Any) -> Tuple:
        _type = TYPES.get(prisma__type, Any)
        return prisma__value, _type
