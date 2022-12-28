import pysqlx_core
from typing import Optional

from .errors import AlreadyConnectedError, NotConnectedError
from .helper import model_parameter_error_message, not_connected_error_message
from .._core.parser import (
    BaseRow,
    MyModel,
    ParserIn,
    ParserSQL,
)  # import necessary using _core to not subscribe default parser
from .const import ISOLATION_LEVEL
from .until import check_isolation_level, check_sql_and_parameters, pysqlx_get_error


class PySQLXEngine:
    __slots__ = ["uri", "connected", "_conn", "_provider"]

    uri: str
    connected: bool

    def __init__(self, uri: str):
        _providers = ["postgresql", "mysql", "sqlserver", "sqlite"]
        if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
            raise ValueError(f"invalid uri: {uri}, check the usage uri, accepted providers: {', '.join(_providers)}")

        if uri.startswith("sqlite"):
            uri = uri.replace("sqlite", "file", 1)

        self.uri: str = uri
        self.connected: bool = False
        self._conn: Optional[pysqlx_core.Connection] = None

        self._provider = "sqlite"

        for prov in _providers:
            if self.uri.startswith(prov):
                self._provider = prov

    def __del__(self):
        if self.connected:
            del self._conn
            self._conn = None
            self.connected = False

    def is_healthy(self):
        self._pre_validate()
        return self._conn.is_healthy()

    def requires_isolation_first(self):
        self._pre_validate()
        return self._conn.requires_isolation_first()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, exc_tb):
        await self.close()

    async def connect(self):
        if self.connected:
            raise AlreadyConnectedError()
        try:
            self._conn = await pysqlx_core.new(uri=self.uri)
            self.connected = True
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def close(self):
        if self.connected:
            del self._conn
            self._conn = None
            self.connected = False

    async def raw_cmd(self, sql: str):
        self._pre_validate(sql=sql)
        try:
            return await self._conn.raw_cmd(sql=sql)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
        self._pre_validate(sql=sql, parameters=parameters)
        try:
            if model is not None and not issubclass(model, BaseRow):
                raise TypeError(model_parameter_error_message())

            parse = ParserSQL(provider=self._provider, sql=sql, parameters=parameters)
            result = await self._conn.query(sql=parse.sql())
            return ParserIn(result=result, model=model).parse()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_as_dict(self, sql: str, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)
        try:
            parse = ParserSQL(provider=self._provider, sql=sql, parameters=parameters)
            return await self._conn.query_as_list(sql=parse.sql())
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_first(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
        self._pre_validate(sql=sql, parameters=parameters)
        try:
            if model is not None and not issubclass(model, BaseRow):
                raise TypeError(model_parameter_error_message())

            parse = ParserSQL(provider=self._provider, sql=sql, parameters=parameters)
            result = await self._conn.query(sql=parse.sql())
            return ParserIn(result=result, model=model).parse_first()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_first_as_dict(self, sql: str, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)
        try:
            parse = ParserSQL(provider=self._provider, sql=sql, parameters=parameters)
            row = await self._conn.query_first_as_dict(sql=parse.sql())
            return row if row else None
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def execute(self, sql: str, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)
        try:
            parse = ParserSQL(provider=self._provider, sql=sql, parameters=parameters)
            return await self._conn.execute(sql=parse.sql())
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        self._pre_validate(isolation_level=isolation_level)
        try:
            await self._conn.set_isolation_level(isolation_level=isolation_level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def begin(self):
        await self.start_transaction()

    async def commit(self):
        self._pre_validate()
        if self._provider == "sqlserver":
            await self.raw_cmd(sql="COMMIT TRANSACTION;")
        else:
            await self.raw_cmd(sql="COMMIT;")

    async def rollback(self):
        self._pre_validate()
        if self._provider == "sqlserver":
            await self.raw_cmd(sql="ROLLBACK TRANSACTION;")
        else:
            await self.raw_cmd(sql="ROLLBACK;")

    async def start_transaction(self, isolation_level: Optional[ISOLATION_LEVEL] = None):
        self._pre_validate(isolation_level=isolation_level)
        try:
            await self._conn.start_transaction(isolation_level=isolation_level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    def _pre_validate(
        self,
        sql: str = None,
        parameters: Optional[dict] = None,
        isolation_level: Optional[ISOLATION_LEVEL] = None,
    ):
        if not self.connected:
            raise NotConnectedError(not_connected_error_message())

        if sql is not None:
            check_sql_and_parameters(sql=sql, parameters=parameters)

        if isolation_level is not None:
            check_isolation_level(isolation_level=isolation_level)
