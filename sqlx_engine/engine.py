from typing import Any, Dict, List, Optional

from pydantic import BaseModel, create_model
from typing_extensions import LiteralString

from ..core.engine import AsyncEngine as __AsyncEngine
from .mount import mount_body

PROVIDERS = ["postgresql", "mysql", "sqlserver", "sqlite"]


class BaseRow(BaseModel):
    ...


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

    def __init__(self, provider: PROVIDERS, uri: str) -> None:
        self.uri = uri
        self.provider = provider
        self._connection: __AsyncEngine = None
        self._connected: bool = False

    async def connect(self, timeout: int = 10) -> None:
        self._connection = __AsyncEngine(
            db_uri=self.uri,
            db_provider=self.provider,
            db_timeout=timeout,
        )
        await self._connection.connect()

    @property
    def connected(self) -> bool:
        return self._connection.connected

    async def close(self) -> None:
        await self._connection.disconnect()

    async def execute(self, stmt: LiteralString) -> int:
        """Execute statement

        Args:
            stmt (LiteralString): Insert, Update, Delete, Drop etc. Not Query!

        Returns:
            int: Affect row
        """
        body = mount_body(_type="executeRaw", _sql=stmt)
        data = await self._connection.request(method="POST", path="/", content=body)

        return int(data["data"]["result"])

    async def query(self, query: LiteralString) -> Optional[List[BaseRow]]:
        """Execute select
        Args:
            query (LiteralString): Only query/select!

        Returns:
           Optional[List[BaseRow]]: Pydantic Model or None
        """
        body = mount_body(_type="queryRaw", _sql=query)
        data = await self._connection.request(method="POST", path="/", content=body)

        resp = data["data"]["result"]
        if resp:
            fist_row = resp[0]
            model = create_model("BaseRow", **fist_row)
            return [model(**v) for v in resp]
        return None
