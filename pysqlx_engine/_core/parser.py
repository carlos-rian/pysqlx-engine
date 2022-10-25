from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Union
from uuid import UUID

from pydantic import BaseModel, create_model, parse_obj_as
from pydantic.types import Json
from pysqlx_core import PySQLXResult

TYPES = {
    "bool": bool,
    "str": str,
    "int": int,
    "list": list,
    "json": Json,
    "uuid": UUID,
    "time": time,
    "date": date,
    "datetime": datetime,
    "float": float,
    "bytes": bytes,
    "decimal": Decimal,
}

BaseRow = BaseModel


class Parser:
    __slots__ = "result"

    def __init__(self, result: PySQLXResult):
        self.result: PySQLXResult = result

    def create_model(self) -> BaseRow:
        fields = {}
        for key, value in self.result.get_types().items():
            fields[key] = (TYPES.get(value, Any), None)
        return create_model("BaseRow", **fields)

    def parse(self) -> List[BaseRow]:
        if len(self.result) == 0:
            return []
        return parse_obj_as(self.create_model(), self.result.get_all())

    def parse_first(self) -> Union[BaseRow, None]:
        if len(self.result) == 0:
            return None
        return parse_obj_as(self.create_model(), self.result.get_first())
