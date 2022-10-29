import pysqlx_core
from typing_extensions import Literal

from .errors import NotConnectedError
from .helper import isolation_error_message, not_connected_error_message
from .parser import Parser
from .until import pysqlx_get_error

LiteralString = str
ISOLATION_LEVEL = Literal["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]


class PySQLXEngine:
    __slots__ = ("_conn", "_uri", "connected")

    def __init__(self, uri: str):
        _providers = ["postgresql", "mysql", "sqlserver", "sqlite"]
        if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
            raise ValueError(f"invalid uri: {uri}, check the usage uri, accepted providers: {', '.join(_providers)}")

        if uri.startswith("sqlite"):
            uri = uri.replace("sqlite", "file", 1)

        self._uri: str = uri
        self._conn: pysqlx_core.Connection = None
        self.connected: bool = False

    def __del__(self):
        if self.connected:
            self._conn = None
            self.connected = False

    def is_healthy(self):
        self._check_connection()
        return self._conn.is_healthy()

    def requires_isolation_first(self):
        self._check_connection()
        return self._conn.requires_isolation_first()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, exc_tb):
        if self.connected():
            await self.close()

    async def connect(self):
        try:
            self._conn = await pysqlx_core.new(uri=self._uri)
            self.connected = True
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def close(self):
        self._conn = None
        self.connected = False

    async def raw_cmd(self, sql: LiteralString):
        self._check_connection()
        try:
            return await self._conn.raw_cmd(sql=sql)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query(self, query: LiteralString, as_dict: bool = False):
        self._check_connection()
        try:
            if as_dict is True:
                return await self._conn.query_as_list(sql=query)
            result = await self._conn.query(sql=query)
            return Parser(result).parse()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_first(self, query: LiteralString, as_dict: bool = False):
        self._check_connection()
        try:
            if as_dict is True:
                row = await self._conn.query_first_as_dict(sql=query)
                return row if row else None

            result = await self._conn.query(sql=query)
            return Parser(result).parse_first()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def execute(self, stmt: LiteralString):
        self._check_connection()
        try:
            return await self._conn.execute(sql=stmt)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        self._check_connection()
        self._check_isolation_level(isolation_level=isolation_level)
        try:
            await self._conn.set_isolation_level(level=isolation_level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def start_transaction(self, isolation_level: ISOLATION_LEVEL = None):
        self._check_connection()
        if isolation_level is not None:
            self._check_isolation_level(isolation_level=isolation_level)
        try:
            await self._conn.start_transaction(isolation_level=isolation_level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    def _check_connection(self):
        if not self.connected:
            raise NotConnectedError(not_connected_error_message())

    def _check_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        levels = ["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]
        if isinstance(isolation_level, str) and any([isolation_level == level for level in levels]):
            return isolation_level
        raise ValueError(isolation_error_message())
