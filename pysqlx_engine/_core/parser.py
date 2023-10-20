from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Sequence, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, create_model
from pysqlx_core import PySQLXResult

from .const import PYDANTIC_IS_V1, TYPES_OUT
from .until import build_sql, parse_obj_as

MyModel = TypeVar("MyModel", bound="BaseRow")

JsonParam = Union[
    Dict[str, Union[bool, str, int, UUID, time, date, datetime, float, bytes, Decimal, None]],
    List[Dict[str, Union[bool, str, int, UUID, time, date, datetime, float, bytes, Decimal, None]]],
    Dict,
    List,
]
DictParam = Dict[
    str,
    Union[bool, str, int, JsonParam, UUID, time, date, datetime, float, bytes, Decimal, None],
]


class BaseRow(BaseModel):
    """
    BaseRow class for a row returned by PySQLXEngine.

    BaseRow is a class that represents a row of the result of a query.

    BaseRow is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.
    """

    def get_columns(self) -> Dict[str, Any]:
        """
        Return the columns of the row.

        Returns:
            Dict[str, Any]: The columns of the row.
        """
        values = self.dict() if PYDANTIC_IS_V1 else self.model_dump()
        columns = {}
        for key, value in values.items():
            columns[key] = type(value)
        return columns

    def __str__(self) -> str:
        return super().__repr__()


class ParserIn:
    __slots__ = ("result", "model")

    def __init__(self, result: PySQLXResult, model: MyModel = None):
        self.result: PySQLXResult = result
        self.model: MyModel = model

    def create_model(self) -> BaseRow:
        fields = {}
        for key, value in self.result.get_types().items():
            if value.startswith("array_"):
                _, v = value.split("_")
                type_ = TYPES_OUT.get(v, Any)
                fields[key] = (Union[Sequence[type_], None], None)
            else:
                type_ = TYPES_OUT.get(value, Any)
                fields[key] = (Union[type_, None], None)

        model = create_model("BaseRow", **fields, __base__=BaseRow)
        return model

    def parse(self) -> List[BaseRow]:
        if len(self.result) == 0:
            return []
        model = self.model or self.create_model()
        return parse_obj_as(type_=List[model], obj=self.result.get_all())

    def parse_first(self) -> Union[BaseRow, None]:
        if len(self.result) == 0:
            return None
        model = self.model or self.create_model()
        return parse_obj_as(type_=model, obj=self.result.get_first())


class ParserSQL:
    def __init__(self, provider: str, sql: str, parameters: dict = None) -> None:
        self._sql: str = sql
        self.provider: str = provider
        self.parameters: dict = parameters

    def sql(self) -> str:
        return build_sql(provider=self.provider, sql=self._sql, parameters=self.parameters)
