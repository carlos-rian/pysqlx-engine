from .errors import PoolMaxConnectionsError
from .aconn import PySQLXEngine

class PySQLXEnginePool:
    """
    The PySQLXEnginePool class is a simple connection pool for PySQLXEngine.
    It is thread-safe and can be used in async code to run multiple queries in parallel.

    Example:
        >>> from pysqlx_engine import PySQLXEnginePool
        >>> pool = PySQLXEnginePool("postgresql://user:pass@host:port/db?schema=sample", max_connections=3)
        >>> async def main():
        >>>     conn1 = await pool.new_connection()
        >>>     conn2 = await pool.new_connection()
        >>>     conn3 = await pool.new_connection()
        >>>     query = "SELECT * FROM table"



    """

    uri: str
    max_connections: int

    def __init__(self, uri: str, max_connections: int = None): ...
    async def new_connection(self) -> PySQLXEngine: ...
