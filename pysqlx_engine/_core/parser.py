from typing import Any, Dict, List, TypeVar, Union
from pydantic import BaseModel, create_model, parse_obj_as
from pysqlx_core import PySQLXResult
from .const import TYPES_OUT

Model = TypeVar("Model", bound="BaseRow")


class BaseRow(BaseModel):
    """
    BaseRow class for a row returned by PySQLXEngine.

    BaseRow is a class that represents a row of the result of a query.

    BaseRow is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.
    """

    _baserow_columns: Dict[str, Any] = None

    class Config:
        orm_mode = True
        ignore_extra = True
        allow_population_by_field_name = True

    def get_columns(self) -> Dict[str, Any]:
        """
        Return the columns of the row.


        Returns:
            Dict[str, Any]: The columns of the row.
        """
        if self._baserow_columns is None:
            values = self.dict()
            columns = {}
            for key, value in values.items():
                columns[key] = type(value)
            return columns
        return self._baserow_columns


class ParserIn:
    __slots__ = ("result", "model")

    def __init__(self, result: PySQLXResult, model: Model = None):
        self.result: PySQLXResult = result
        self.model: Model = model

    def create_model(self) -> BaseRow:
        fields = {}
        columns = {}
        for key, value in self.result.get_types().items():
            if value.startswith("list_"):
                _, v = value.split("_")
                type_ = TYPES_OUT.get(v, Any)
                fields[key] = (List[type_], None)
            else:
                type_ = TYPES_OUT.get(value, Any)
                fields[key] = (type_, None)
            columns[key] = type_

        fields["_baserow_columns"] = (Dict[str, Any], columns)
        model = create_model("BaseRow", **fields, __base__=BaseRow)
        return model

    def parse(self) -> List[BaseRow]:
        if len(self.result) == 0:
            return []
        model = self.model or self.create_model()
        return parse_obj_as(List[model], self.result.get_all())

    def parse_first(self) -> Union[BaseRow, None]:
        if len(self.result) == 0:
            return None
        model = self.model or self.create_model()
        return parse_obj_as(model, self.result.get_first())


class ParserOut:
    def __init__(self, sql: str, param: dict = None) -> None:
        self.sql: str = sql
        self.param: dict = param

    def get_sql_params(self) -> dict:
        data = {}
