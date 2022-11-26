from .errors import PoolMaxConnectionsError
from .aconn import PySQLXEngine


class PySQLXEnginePool:
    __slots__ = ("uri", "max_connections", "_pool_len")

    def __init__(self, uri: str, max_connections: int = None):
        PySQLXEngine(uri)
        self.uri = uri
        assert isinstance(max_connections, (int, None)), "max_connections must be an integer or None"
        self.max_connections: int = max_connections
        self._pool_len: int = 0

    async def __aenter__(self) -> PySQLXEngine:
        return await self.new_connection()

    async def __aexit__(self, exc_type, exc, exc_tb):
        ...

    async def new_connection(self) -> PySQLXEngine:
        if self.max_connections is not None and self._pool_len >= self.max_connections:
            raise PoolMaxConnectionsError()

        self._pool_len += 1
        conn = PySQLXEngine(self.uri)
        await conn.connect()
        return conn
