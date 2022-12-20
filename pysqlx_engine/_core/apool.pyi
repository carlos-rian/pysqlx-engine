from types import TracebackType
from typing import Optional, Type
from .aconn import PySQLXEngine

class PySQLXEnginePool:
    """
    The PySQLXEnginePool class is a simple connection pool for PySQLXEngine.
    It is thread-safe and can be used in async code to run multiple queries in parallel.

    Example:
    ```python
        import asyncio
        from pysqlx_engine import PySQLXEnginePool

        pool = PySQLXEnginePool("postgresql://user:pass@host:port/db?schema=sample", max_connections=3)

        async def main():
            conn1 = await pool.new_connection()
            conn2 = await pool.new_connection()
            conn3 = await pool.new_connection()

            # multiple queries can be run in parallel
            coro = [
                    await conn1.fetch("SELECT 1 AS one"),
                    await conn2.fetch("SELECT 2 AS two"),
                    await conn3.fetch("SELECT 3 AS three")
                ]
            # wait for all queries to finish
            results = await asyncio.gather(*coro)
            print(results)
            # [[BaseRow(one=1)], [BaseRow(two=2)], [BaseRow(three=3)]]

            # try creating a connection when the pool is full
            conn4 = await pool.new_connection() # raises PoolMaxConnectionsError

        asyncio.run(main())
    ```
    """

    uri: str
    max_connections: int

    def __init__(self, uri: str, max_connections: Optional[int] = None): ...
    async def __aenter__(self) -> "PySQLXEngine":
        """
        ## Description
        Create a pool instance. using `async with`
        """
        ...
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    async def new_connection(self) -> PySQLXEngine:
        """
        ## Description
        Create a new connection from the pool.
        this method tries to get a connection from the pool, if the pool is full to this instance,
        it will raise `PoolMaxConnectionsError`.

        If max_connections is None, the pool is "unlimited," stopped only by the database server's connection limit.

        * Arguments: `None`:

        * Returns: `PySQLXEngine`

        * Raises: `PoolMaxConnectionsError`, `ConnectError`

        ## Example
        ```python
        from pysqlx_engine import PySQLXEnginePool

        pool = PySQLXEnginePool("postgresql://user:pass@host:port/db?schema=sample", max_connections=3)

        async def main():
            conn1 = await pool.new_connection() # return a new PySQLXEngine instance
            conn2 = await pool.new_connection() # return a new PySQLXEngine instance
            conn3 = await pool.new_connection() # return a new PySQLXEngine instance
        ```
        """
        ...
