from typing import Optional

from .._core.parser import MyModel  # import necessary using _core to not subscribe default parser
from .const import ISOLATION_LEVEL
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
    async def raw_cmd(self, sql: str):
        return await (super()).raw_cmd(sql=sql)

    @force_sync
    async def query(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
        return await (super()).query(sql=sql, parameters=parameters, model=model)

    @force_sync
    async def query_as_dict(self, sql: str, parameters: Optional[dict] = None):
        return await (super()).query_as_dict(sql=sql, parameters=parameters)

    @force_sync
    async def query_first(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
        return await (super()).query_first(sql=sql, parameters=parameters, model=model)

    @force_sync
    async def query_first_as_dict(self, sql: str, parameters: Optional[dict] = None):
        return await (super()).query_first_as_dict(sql=sql, parameters=parameters)

    @force_sync
    async def execute(self, sql: str, parameters: Optional[dict] = None):
        return await (super()).execute(sql=sql, parameters=parameters)

    @force_sync
    async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
        await (super()).set_isolation_level(isolation_level=isolation_level)

    @force_sync
    async def begin(self):
        await (super()).begin()

    @force_sync
    async def commit(self):
        await (super()).commit()

    @force_sync
    async def rollback(self):
        await (super()).rollback()

    @force_sync
    async def start_transaction(self, isolation_level: Optional[ISOLATION_LEVEL] = None):
        await (super()).start_transaction(isolation_level=isolation_level)
