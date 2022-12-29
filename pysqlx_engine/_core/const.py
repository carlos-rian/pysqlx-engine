from datetime import date, datetime, time
from decimal import Decimal
from os import getenv
from uuid import UUID
from pydantic.types import Json
from pydantic import BaseConfig
from typing_extensions import Literal


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
CODE_ParameterInvalidJsonValueError = "PYSQLX005"


class _Config(BaseConfig):
    """
    CONFIG class for PySQLXEngine.

    You can set the following environment variables: ``PYSQLX_SQL_LOG``, ``PYSQLX_MSG_COLORIZE``, ``PYSQLX_ERROR_JSON_FMT``

    * ``PYSQLX_SQL_LOG``: bool = False
        If True, the SQL statements will be printed in the console.
    * ``PYSQLX_MSG_COLORIZE``: bool = False
        If True, the messages will be printed in color.
    * ``PYSQLX_ERROR_JSON_FMT``: bool = False
        If True, the error messages will be printed in JSON format.

    Or you can set the value of the variables in the code.

    Example:
    ```python
        from pysqlx_engine import LOG_CONFIG

        LOG_CONFIG.PYSQLX_SQL_LOG = True
        LOG_CONFIG.PYSQLX_MSG_COLORIZE = True
        LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True
    ```

    """

    PYSQLX_SQL_LOG: bool = getenv("PYSQLX_SQL_LOG", "0") != "0"
    PYSQLX_MSG_COLORIZE: bool = getenv("PYSQLX_MSG_COLORIZE", "0") != "0"
    PYSQLX_ERROR_JSON_FMT: bool = getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0"


CONFIG = _Config()
