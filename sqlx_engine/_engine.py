from typing import Dict, List, Literal, Optional, Union

from typing_extensions import LiteralString

from sqlx_engine.core.builder import QueryBuilder
from sqlx_engine.core.parser import Deserialize

from .core.common import BaseRow
from .core.engine import AsyncEngine as _AsyncEngine


class SQLXEngine:
    """
    ```md
    Providers -> postgresql, mysql, sqlserver or sqlite
    ```
    Usage:
    ``` python
    >>> ##### PostgreSQL
    >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
    >>> conn = SQLXEngine(provider="postgresql", uri=uri)

    #------------------------------------------

    >>> ##### MySQL
    >>> uri = "mysql://user:pass@host:port/db?schema=sample"
    >>> conn = SQLXEngine(provider="mysql", uri=uri)

    #------------------------------------------

    >>> ##### Microsoft SQL Server
    >>> uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
    >>> conn = SQLXEngine(provider="sqlserver", uri=uri)

    #------------------------------------------

    >>> ##### SQLite
    >>> uri = "file:./dev.db"
    >>> conn = SQLXEngine(provider="sqlite", uri=uri)

    ```

    ```md
    Reference: https://www.prisma.io/docs/reference/database-reference/connection-urls
    ```
    """

    __slots__ = ("provider", "uri", "connected", "_connection")

    def __init__(
        self,
        provider: Literal["postgresql", "mysql", "sqlserver", "sqlite", "_connection"],
        uri: str,
    ) -> None:
        self.uri = uri
        self.provider = provider
        self.connected: bool = False
        self._connection: _AsyncEngine = None

    async def connect(self, timeout: int = 10) -> None:
        self._connection = _AsyncEngine(
            db_uri=self.uri,
            db_provider=self.provider,
            db_timeout=timeout,
        )
        await self._connection.connect()
        self.connected = self._connection.connected

    async def close(self) -> None:
        await self._connection.disconnect()
        self.connected = False
        self._connection = None

    async def execute(self, stmt: LiteralString) -> int:
        """Execute statement

        Args:
            stmt (LiteralString): Insert, Update, Delete, Drop etc. Not Query!

        Returns:
            int: Affect row
        """
        builder = QueryBuilder(
            method="executeRaw",
            operation="mutation",
            arguments={
                "query": stmt,
                "parameters": [],
            },
        )
        content = builder.build()
        data = await self._connection.request(method="POST", path="/", content=content)

        return int(data["data"]["result"])

    async def query(
        self, query: LiteralString, as_base_row: bool = True
    ) -> Optional[Union[List[BaseRow], List[Dict]]]:
        """Query execute
        Args:
            query (LiteralString): Only query/select!
            as_dict (bool): By default is True, BaseRow is an object typing.

        Returns:
           List[BaseRow]: List of Pydantic Model
           List[Dict]: List of dict
           NoneType: None
        """
        builder = QueryBuilder(
            method="queryRaw",
            operation="mutation",
            arguments={
                "query": query,
                "parameters": [],
            },
        )
        content = builder.build()
        data = await self._connection.request(method="POST", path="/", content=content)

        resp = data["data"]["result"]
        if resp:
            rows = Deserialize(rows=resp, as_base_row=as_base_row)
            return list(rows.deserialize())
        return None
