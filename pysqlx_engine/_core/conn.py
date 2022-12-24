from typing import Optional

from .._core.parser import Model  # import necessary using _core to not subscribe default parser
from .const import ISOLATION_LEVEL, LiteralString
from .until import force_sync
from .aconn import PySQLXEngine as _PySQLXEngine


class PySQLXEngineSync(_PySQLXEngine):
    uri: str
    connected: bool

    def __init__(self, uri: str):
        super().__init__(uri=uri)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()

    @force_sync
    async def connect(self):
        await (super()).connect()

    @force_sync
    async def close(self):
        await (super()).close()

    @force_sync
    async def raw_cmd(self, sql: LiteralString):
        return await (super()).raw_cmd(sql=sql)

    @force_sync
    async def query(self, sql: LiteralString, model: Model = None, parameters: Optional[dict] = None):
        return await (super()).query(sql=sql, parameters=parameters, model=model)

    @force_sync
    async def query_as_dict(self, sql: LiteralString, parameters: Optional[dict] = None):
        return await (super()).query_as_dict(sql=sql, parameters=parameters)

    @force_sync
    async def query_first(self, sql: LiteralString, model: Model = None, parameters: Optional[dict] = None):
        return await (super()).query_first(sql=sql, parameters=parameters, model=model)

    @force_sync
    async def query_first_as_dict(self, sql: LiteralString, parameters: Optional[dict] = None):
        return await (super()).query_first_as_dict(sql=sql, parameters=parameters)

    @force_sync
    async def execute(self, sql: LiteralString, parameters: Optional[dict] = None):
        return await (super()).execute(sql=sql, parameters=parameters)

    @force_sync
    async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        await (super()).set_isolation_level(isolation_level=isolation_level)

    def begin(self):
        self.start_transaction()

    def commit(self):
        self._pre_validate()
        if self._provider == "sqlserver":
            self.raw_cmd(sql="COMMIT TRANSACTION;")
        else:
            self.raw_cmd(sql="COMMIT;")

    def rollback(self):
        if self._provider == "sqlserver":
            self.raw_cmd(sql="ROLLBACK TRANSACTION;")
        else:
            self.raw_cmd(sql="ROLLBACK;")

    @force_sync
    async def start_transaction(self, isolation_level: Optional[ISOLATION_LEVEL] = None):
        await (super()).start_transaction(isolation_level=isolation_level)
