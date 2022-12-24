from types import TracebackType
from typing import Optional, Type
from .conn import PySQLXEngineSync

class PySQLXEnginePoolSync:
    """
    The PySQLXEnginePoolSync class is a simple connection pool for PySQLXEngine.
    It is thread-safe and can be used in thread or process to run multiple queries in parallel.

    Example:
    ```python
        import asyncio
        from pysqlx_engine import PySQLXEnginePoolSync

        pool = PySQLXEnginePoolSync("postgresql://user:pass@host:port/db?schema=sample", max_connections=3)

        def main():
            conn1 = pool.new_connection()
            conn2 = pool.new_connection()
            conn3 = pool.new_connection()

            # multiple queries can be run in parallel using threads or processes
            results = [
                    conn1.fetch("SELECT 1 AS one"),
                    conn2.fetch("SELECT 2 AS two"),
                    conn3.fetch("SELECT 3 AS three")
                ]
            print(results)
            # [[BaseRow(one=1)], [BaseRow(two=2)], [BaseRow(three=3)]]

            # try creating a connection when the pool is full
            conn4 = pool.new_connection() # raises PoolMaxConnectionsError

        main()
    ```
    """

    uri: str
    max_connections: int

    def __init__(self, uri: str, max_connections: Optional[int] = None): ...
    async def __aenter__(self) -> "PySQLXEngineSync":
        """
        ## Description
        Create a pool instance. using `with`
        """
        ...
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    async def new_connection(self) -> PySQLXEngineSync:
        """
        ## Description
        Create a new connection from the pool.
        this method tries to get a connection from the pool, if the pool is full to this instance, it will raise `PoolMaxConnectionsError`.

        If max_connections is None, the pool is "unlimited," stopped only by the database server's connection limit.

        * Arguments: `None`:

        * Returns: `PySQLXEngine`

        * Raises: `PoolMaxConnectionsError`, `ConnectError`

        ## Example
        ```python
        from pysqlx_engine import PySQLXEnginePoolSync

        pool = PySQLXEnginePoolSync("postgresql://user:pass@host:port/db?schema=sample", max_connections=3)

        def main():
            conn1 = pool.new_connection() # return a new PySQLXEngineSync instance
            conn2 = pool.new_connection() # return a new PySQLXEngineSync instance
            conn3 = pool.new_connection() # return a new PySQLXEngineSync instance
        ```
        """
        ...
