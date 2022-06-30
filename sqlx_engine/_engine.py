from typing import Dict, List, Literal, Optional, Union

from typing_extensions import LiteralString

from sqlx_engine.core.parser import Deserialize

from ._mount import mount_body
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

    def __init__(
        self,
        provider: Literal["postgresql", "mysql", "sqlserver", "sqlite"],
        uri: str,
    ) -> None:
        self.uri = uri
        self.provider = provider
        self._connection: _AsyncEngine = None
        self._connected: bool = False

    async def connect(self, timeout: int = 10) -> None:
        self._connection = _AsyncEngine(
            db_uri=self.uri,
            db_provider=self.provider,
            db_timeout=timeout,
        )
        await self._connection.connect()
        self._connected = self._connection.connected

    @property
    def connected(self) -> bool:
        return self._connected

    async def close(self) -> None:
        await self._connection.disconnect()
        self._connected = False
        self._connection = None

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

    async def query(
        self, query: LiteralString, as_base_row: bool = True
    ) -> Optional[Union[List[BaseRow], List[Dict]]]:
        """Execute select
        Args:
            query (LiteralString): Only query/select!
            as_dict (bool): By default is False, row

        Returns:
           Optional[List[BaseRow]]: Pydantic Model or None
        """
        body = mount_body(_type="queryRaw", _sql=query)
        data = await self._connection.request(method="POST", path="/", content=body)

        resp = data["data"]["result"]
        if resp:
            rows = Deserialize(rows=resp, as_base_row=as_base_row)
            return list(rows.deserialize())
        return None
