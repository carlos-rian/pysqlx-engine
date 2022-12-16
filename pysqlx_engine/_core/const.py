from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from pydantic.types import Json
from typing_extensions import Literal, LiteralString as ls

LiteralString = ls

TYPES_OUT = {
    "bool": bool,
    "str": str,
    "int": int,
    "list": tuple,
    "json": Json,
    "uuid": UUID,
    "time": time,
    "date": date,
    "datetime": datetime,
    "float": float,
    "bytes": bytes,
    "decimal": Decimal,
}

TYPES_IN = TYPES_OUT.copy()
TYPES_IN.update({"array": list, "dict": dict})
TYPES_IN.pop("json")

ISOLATION_LEVEL = Literal["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]

PROVIDER = Literal["postgresql", "mysql", "sqlserver", "sqlite"]


CODE_AlreadyConnectedError = "PYSQLX001"
CODE_PoolMaxConnectionsError = "PYSQLX002"
CODE_ParameterInvalidProviderError = "PYSQLX003"
CODE_ParameterInvalidValueError = "PYSQLX004"
