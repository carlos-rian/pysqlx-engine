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

    def __init__(self, value: bool):
        assert isinstance(value, bool), "value must be a boolean."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_bool(provider, self.value)


class StringType(AbstractDatabaseType):
    """String type
    Database type: char|varchar|text|char|varchar|text|etc
    """

    def __init__(self, value: str):
        assert isinstance(value, str), "value must be a string."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_str(provider, self.value)


class NStringType(StringType):
    """String type for unicode characters
    Database type: nchar|nvarchar|ntext|etc
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_nstr(provider, self.value)


class IntegerType(AbstractDatabaseType):
    """Integer type
    Database type: int|integer|smallint|bigint|tinyint|etc
    """

    def __init__(self, value: int):
        assert isinstance(value, int), "value must be an integer."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_int(provider, self.value)


class JsonType(AbstractDatabaseType):
    """Json type
    Database type: json|jsonb|nvarchar|varchar|string|etc
    """

    def __init__(self, value: Union[dict, list]):
        assert isinstance(value, (dict, list)), "value must be a dictionary or list."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_json(provider, self.value)


class NJsonType(JsonType):
    """Json type for unicode characters
    Database type: json|jsonb|nvarchar|varchar|string|etc
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_njson(provider, self.value)


class UUIDType(AbstractDatabaseType):
    """UUID type
    Database type: uuid|varchar|text|nvarchar|etc
    """

    def __init__(self, value: UUID):
        assert isinstance(value, UUID), "value must be an UUID"
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_uuid(provider, self.value)


class TimeType(AbstractDatabaseType):
    """Time type
    Database type: time|varchar|string|etc
    """

    def __init__(self, value: time):
        assert isinstance(value, time), "value must be a datetime.time."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_time(provider, self.value)


class DateType(AbstractDatabaseType):
    """Date type
    Database type: date|varchar|string|etc
    """

    def __init__(self, value: date):
        assert isinstance(value, date), "value must be a datetime.date."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_date(provider, self.value)


class DateTimeType(AbstractDatabaseType):
    """DateTime type
    Database type: datetime|timestamp|varchar|string|etc
    """

    def __init__(self, value: datetime):
        assert isinstance(value, datetime), "value must be a datetime.datetime."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_datetime(provider, self.value)


class FloatType(AbstractDatabaseType):
    """Float type
    Database type: float|double|decimal|numeric|real|etc
    """

    def __init__(self, value: float):
        assert isinstance(value, float), "value must be a float."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_float(provider, self.value)


class BytesType(AbstractDatabaseType):
    """Bytes type
    Database type: bytea|blob|varbinary|etc
    """

    def __init__(self, value: bytes):
        assert isinstance(value, bytes), "value must be a bytes."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_bytes(provider, self.value)


class DecimalType(AbstractDatabaseType):
    """Decimal type
    Database type: decimal|numeric|money|etc
    """

    def __init__(self, value: Decimal):
        assert isinstance(value, Decimal), "value must be a float."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_decimal(provider, self.value)


class EnumType(AbstractDatabaseType):
    """Enum type
    Database type: enum|varchar|text|nvarchar|etc
    """

    def __init__(self, value: Enum):
        assert isinstance(value, Enum), "value must be a enum.Enum."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_enum(provider, self.value, field)


class TupleType(AbstractDatabaseType):
    """Tuple type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def __init__(self, value: tuple):
        assert isinstance(value, tuple), "value must be a tuple."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_tuple(provider, self.value, field)


class NTupleType(TupleType):
    """Tuple type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_ntuple(provider, self.value, field)


class TupleEnumType(AbstractDatabaseType):
    """Tuple Enum type - Only for PostgreSQL
    Database type: array(Postgres Native), another database: error.
    """

    def __init__(self, *value):
        assert isinstance(value, tuple), "value must be a tuple."
        assert all(isinstance(v, Enum) for v in value), "value must be a tuple of enum.Enum."
        self.value = value

    def convert(self, provider: PROVIDER, field: str = "") -> T:
        return param.try_tuple_enum(provider, self.value, field)
