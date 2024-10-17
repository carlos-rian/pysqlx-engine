from datetime import date, datetime, time
from decimal import Decimal
from os import getenv
from typing import Union
from uuid import UUID

from pydantic import VERSION as PYDANTIC_VERSION
from pydantic import BaseModel as BaseConfig
from pydantic.types import Json
from typing_extensions import Literal

PYDANTIC_IS_V1 = PYDANTIC_VERSION < "2.0.0"


TYPES_OUT = {
	"bool": bool,
	"str": str,
	"int": int,
	"list": tuple,
	"json": Union[dict, list, Json],
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
# CODE_PoolMaxConnectionsError = "PYSQLX002"
CODE_ParameterInvalidProviderError = "PYSQLX003"
CODE_ParameterInvalidValueError = "PYSQLX004"
CODE_ParameterInvalidJsonValueError = "PYSQLX005"


class LogConfig(BaseConfig):
	PYSQLX_DEV_MODE: bool = getenv("PYSQLX_DEV_MODE", "0") != "0"
	PYSQLX_SQL_LOG: bool = getenv("PYSQLX_SQL_LOG", "0") != "0"
	PYSQLX_USE_COLOR: bool = getenv("PYSQLX_USE_COLOR", "0") != "0"
	PYSQLX_ERROR_JSON_FMT: bool = getenv("PYSQLX_ERROR_JSON_FMT", "0") != "0"


LOG_CONFIG = LogConfig()
"""
## Description

CONFIG constant for PySQLXEngine, is used to configure the log and exception messages.

You can set the following ``environment variables``:
    - `PYSQLX_DEV_MODE`
    - `PYSQLX_SQL_LOG`
    - `PYSQLX_USE_COLOR`
    - `PYSQLX_ERROR_JSON_FMT`

---

### Helper
    * `PYSQLX_DEV_MODE`: bool = False
        If True, the development mode will be activated, showing the sql builded before executing.

    * `PYSQLX_SQL_LOG`: bool = False
        If True, the SQL statements will be printed in the console.
    * `PYSQLX_USE_COLOR`: bool = False
        If True, the messages will be printed in color.
    * `PYSQLX_ERROR_JSON_FMT`: bool = False
        If True, the error messages will be printed in JSON format.

Or you can set the value of the variables in the code.

---

### Example:
```python
    # config the pysqlx_engine log
    from pysqlx_engine import LOG_CONFIG

    LOG_CONFIG.PYSQLX_SQL_LOG = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    # set the log info level when the PYSQLX_SQL_LOG is True
    import logging
    logging.basicConfig(level=logging.INFO)

    # connect to the database
    from pysqlx_engine import PySQLXEngine

    db = PySQLXEngine(uri="postgresql://user:pass@host:port/db?schema=sample")
    db.connect()

    # run the query and see the log
    db.query("SELECT * FROM table")
    # output -> INFO:root:SELECT * FROM table

    # run the invalid query and see the error in JSON format
    db.query("SELECT * FROM invalid_table")
    # output ->  INFO:root:SELECT * FROM invalid_table
    
    # raise the error
    pysqlx_engine._core.errors.QueryError: 
    {
       "code": "42P01",
       "message": "relation 'invalid_table' does not exist",
       "error": "QueryError"
    }
```

"""
