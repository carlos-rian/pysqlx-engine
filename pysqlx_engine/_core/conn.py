import pysqlx_core
from typing import Optional

from .errors import AlreadyConnectedError, NotConnectedError
from .helper import model_parameter_error_message, not_connected_error_message
from .._core.parser import (
    BaseRow,
    Model,
    ParserIn,
    ParserSQL,
)  # import necessary using _core to not subscribe default parser
from .const import ISOLATION_LEVEL, LiteralString
from .until import check_isolation_level, check_sql_and_parameters, pysqlx_get_error, force_sync


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

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()

    def connect(self):
        @force_sync
        async def _connect():
            if self.connected:
                raise AlreadyConnectedError()
            try:
                self._conn = await pysqlx_core.new(uri=self.uri)
                self.connected = True
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _connect()

    def close(self):
        if self.connected:
            del self._conn
            self._conn = None
            self.connected = False

    def raw_cmd(self, sql: LiteralString):
        self._pre_validate(sql=sql)

        @force_sync
        async def _raw_cmd():
            try:
                return await self._conn.raw_cmd(sql=sql)
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _raw_cmd()

    def query(self, sql: LiteralString, model: Optional[Model] = None, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)

        @force_sync
        async def _query():
            try:
                if model is not None and not issubclass(model, BaseRow):
                    raise TypeError(model_parameter_error_message())

                result = await self._conn.query(sql=sql)
                return ParserIn(result=result, model=model).parse()
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _query()

    def query_as_dict(self, sql: LiteralString, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)

        @force_sync
        async def _query_as_dict():
            try:
                return await self._conn.query_as_list(sql=sql)
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _query_as_dict()

    def query_first(self, sql: LiteralString, model: Optional[Model] = None, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)

        @force_sync
        async def _query_first():
            try:
                if model is not None and not issubclass(model, BaseRow):
                    raise TypeError(model_parameter_error_message())

                result = await self._conn.query(sql=sql)
                return ParserIn(result=result, model=model).parse_first()
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _query_first()

    def query_first_as_dict(self, sql: LiteralString, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)

        @force_sync
        async def _query_first_as_dict():
            try:
                row = await self._conn.query_first_as_dict(sql=sql)
                return row if row else None
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _query_first_as_dict()

    def execute(self, sql: LiteralString, parameters: Optional[dict] = None):
        self._pre_validate(sql=sql, parameters=parameters)

        @force_sync
        async def _execute():
            try:
                return await self._conn.execute(sql=sql)
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _execute()

    def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        self._pre_validate(isolation_level=isolation_level)

        @force_sync
        async def _set_isolation_level():
            try:
                await self._conn.set_isolation_level(isolation_level=isolation_level)
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _set_isolation_level()

    def begin(self):
        self.start_transaction()

    def commit(self):
        self._pre_validate()
        if self._provider == "sqlserver":
            self.raw_cmd(sql="COMMIT TRANSACTION;")
        else:
            self.raw_cmd(sql="COMMIT;")

    def rollback(self):
        self._pre_validate()
        if self._provider == "sqlserver":
            self.raw_cmd(sql="ROLLBACK TRANSACTION;")
        else:
            self.raw_cmd(sql="ROLLBACK;")

    def start_transaction(self, isolation_level: Optional[ISOLATION_LEVEL] = None):
        self._pre_validate(isolation_level=isolation_level)

        @force_sync
        async def _start_transaction():
            try:
                await self._conn.start_transaction(isolation_level=isolation_level)
            except pysqlx_core.PySQLXError as e:
                raise pysqlx_get_error(err=e)

        return _start_transaction()

    def _pre_validate(
        self,
        sql: LiteralString = None,
        parameters: Optional[dict] = None,
        isolation_level: Optional[ISOLATION_LEVEL] = None,
    ):
        if not self.connected:
            raise NotConnectedError(not_connected_error_message())

        if sql is not None:
            check_sql_and_parameters(sql=sql, parameters=parameters)

        if isolation_level is not None:
            check_isolation_level(isolation_level=isolation_level)
