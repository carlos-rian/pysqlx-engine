from typing import Optional
from .errors import PoolMaxConnectionsError
from .conn import PySQLXEngineSync


class PySQLXEnginePoolSync:
    __slots__ = ("uri", "max_connections", "_pool_len")

    def __init__(self, uri: str, max_connections: Optional[int] = None):
        PySQLXEngineSync(uri)
        self.uri = uri
        assert isinstance(max_connections, (int, None)), "max_connections must be an integer or None"
        self.max_connections: int = max_connections
        self._pool_len: int = 0

    def __enter__(self) -> PySQLXEngineSync:
        return self.new_connection()

    def __exit__(self, exc_type, exc, exc_tb):
        ...

    def new_connection(self) -> PySQLXEngineSync:
        if self.max_connections is not None and self._pool_len >= self.max_connections:
            raise PoolMaxConnectionsError()

        self._pool_len += 1
        conn = PySQLXEngineSync(self.uri)
        conn.connect()
        return conn
