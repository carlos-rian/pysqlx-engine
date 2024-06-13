# sql types
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Union
from uuid import UUID

from typing_extensions import TypeVar

from pysqlx_engine._core.abc import AbstractDatabaseType
from pysqlx_engine._core.const import PROVIDER

from ._core import param

__all__ = [
    "BooleanType",
    "StringType",
    "NStringType",
    "IntegerType",
    "JsonType",
    "NJsonType",
    "UUIDType",
    "TimeType",
    "DateType",
    "DateTimeType",
    "FloatType",
    "BytesType",
    "DecimalType",
    "EnumType",
    "TupleType",
    "NTupleType",
    "TupleEnumType",
]

T = TypeVar("T")


class BooleanType(AbstractDatabaseType):
    """Boolean type

    Database type: bool|bit|boolean|tinyint

    """

    def __init__(self, value: Union[bool, None]):
        assert isinstance(value, (bool, type(None))), "value must be a boolean."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_bool(provider, self.value)


class StringType(AbstractDatabaseType):
    """String type
    Database type: char|varchar|text|char|varchar|text|etc
    """

    def __init__(self, value: Union[str, None]):
        assert isinstance(value, (str, type(None))), "value must be a string."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_str(provider, self.value)


class NStringType(StringType):
    """String type for unicode characters
    Database type: nchar|nvarchar|ntext|etc
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_nstr(provider, self.value)


class IntegerType(AbstractDatabaseType):
    """Integer type
    Database type: int|integer|smallint|bigint|tinyint|etc
    """

    def __init__(self, value: Union[int, None]):
        assert isinstance(value, (int, type(None))), "value must be an integer."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_int(provider, self.value)


class JsonType(AbstractDatabaseType):
    """Json type
    Database type: json|jsonb|nvarchar|varchar|string|etc
    """

    def __init__(self, value: Union[dict, list, None]):
        assert isinstance(value, (dict, list, type(None))), "value must be a dictionary or list."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_json(provider, self.value)


class NJsonType(JsonType):
    """Json type for unicode characters
    Database type: json|jsonb|nvarchar|varchar|string|etc
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_njson(provider, self.value)


class UUIDType(AbstractDatabaseType):
    """UUID type
    Database type: uuid|varchar|text|nvarchar|etc
    """

    def __init__(self, value: Union[UUID, None]):
        assert isinstance(value, (UUID, type(None))), "value must be an UUID"
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_uuid(provider, self.value)


class TimeType(AbstractDatabaseType):
    """Time type
    Database type: time|varchar|string|etc
    """

    def __init__(self, value: Union[time, None]):
        assert isinstance(value, (time, type(None))), "value must be a datetime.time."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_time(provider, self.value)


class DateType(AbstractDatabaseType):
    """Date type
    Database type: date|varchar|string|etc
    """

    def __init__(self, value: Union[date, None]):
        assert isinstance(value, (date, type(None))), "value must be a datetime.date."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_date(provider, self.value)


class DateTimeType(AbstractDatabaseType):
    """DateTime type
    Database type: datetime|timestamp|varchar|string|etc
    """

    def __init__(self, value: Union[datetime, None]):
        assert isinstance(value, (datetime, type(None))), "value must be a datetime.datetime."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_datetime(provider, self.value)


class FloatType(AbstractDatabaseType):
    """Float type
    Database type: float|double|decimal|numeric|real|etc
    """

    def __init__(self, value: Union[float, None]):
        assert isinstance(value, (float, type(None))), "value must be a float."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_float(provider, self.value)


class BytesType(AbstractDatabaseType):
    """Bytes type
    Database type: bytea|blob|varbinary|etc
    """

    def __init__(self, value: Union[bytes, None]):
        assert isinstance(value, (bytes, type(None))), "value must be a bytes."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_bytes(provider, self.value)


class DecimalType(AbstractDatabaseType):
    """Decimal type
    Database type: decimal|numeric|money|etc
    """

    def __init__(self, value: Union[Decimal, None]):
        assert isinstance(value, (Decimal, type(None))), "value must be a float."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_decimal(provider, self.value)


class EnumType(AbstractDatabaseType):
    """Enum type
    Database type: enum|varchar|text|nvarchar|etc
    """

    def __init__(self, value: Union[Enum, None]):
        assert isinstance(value, (Enum, type(None))), "value must be a enum.Enum."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_enum(provider, self.value, field)


class TupleType(AbstractDatabaseType):
    """Tuple type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def __init__(self, value: Union[tuple, None]):
        assert isinstance(value, (tuple, type(None))), "value must be a tuple."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_tuple(provider, self.value, field)


class NTupleType(TupleType):
    """Tuple type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_ntuple(provider, self.value, field)


class TupleEnumType(AbstractDatabaseType):
    """Tuple Enum type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def __init__(self, value: Union[tuple, None]):
        assert isinstance(value, (tuple, type(None))), "value must be a tuple."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return self.value if self.value is None else param.try_tuple_enum(provider, self.value, field)
