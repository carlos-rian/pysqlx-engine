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

class BaseRow(BaseModel):
    """
    BaseRow class for a row returned by PySQLXEngine.
    
    BaseRow is a class that represents a row of the result of a query.

    BaseRow is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.
    """
    ...


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
        return parse_obj_as(List[self.create_model()], self.result.get_all())

    def parse_first(self) -> Union[BaseRow, None]:
        if len(self.result) == 0:
            return None
        return parse_obj_as(self.create_model(), self.result.get_first())
