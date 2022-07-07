from typing import Dict, List, Literal, Optional, Union

from typing_extensions import LiteralString

from ._core.builder import QueryBuilder
from ._core.common import BaseRow
from ._core.config import config
from ._core.engine import AsyncEngine as _AsyncEngine
from ._core.errors import AlreadyConnectedError, NotConnectedError
from ._core.parser import Deserialize


class SQLXEngine:
    """
    SQLXEngine is an engine to run pure sql with queries, inserts,
    deletes, updates, create/alter/drop tables etc.

    It is a CORE for pure SQL, NOT an engine to execute
    ROUTINES/PROCEDURES/FUNCTIONS in the database.


    `providers(str)`: postgresql, mysql, sqlserver or sqlite
    `uri(str)`:  Connection values.
    `improved_error_log(bool)`: Default True. Returns an error in json format with colors.

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

    # URI Reference: https://www.prisma.io/docs/reference/database-reference/connection-urls
    ```
    """

    __slots__ = ("provider", "uri", "connected", "_connection")

    def __init__(
        self,
        provider: Literal["postgresql", "mysql", "sqlserver", "sqlite"],
        uri: str,
        improved_error_log: bool = True,
    ) -> None:
        _providers = ["postgresql", "mysql", "sqlserver", "sqlite"]
        if provider not in _providers:
            raise ValueError(
                f"Invalid provider {provider} \n Providers available: {_providers}"
            )
        if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
            raise ValueError(f"Invalid uri: {uri}, check the usage uri.")

        self.uri = uri
        self.provider = provider
        self.connected: bool = False
        self._connection: _AsyncEngine = None

        config.improved_error_log = improved_error_log

    async def connect(self, timeout: int = 10) -> None:
        """
        Every connection instance is lazy, only after the connect is the
        database checked and a connection is created with it.

        Args:
            timeout in sec (int, optional):
            You can change the value if your database is slow to receive a new connection
            Defaults to 10.
        """
        if self._connection:
            raise AlreadyConnectedError("Already connected to the engine")
        self._connection = _AsyncEngine(
            db_uri=self.uri,
            db_provider=self.provider,
            db_timeout=timeout,
        )
        await self._connection.connect()
        self.connected = self._connection.connected

    async def close(self) -> None:
        """Is good always close the connection, but!
        Even if you don't close the connection, don't worry,
        when the process ends automatically the connections will
        be closed so the bank doesn't have an idle connection.
        """
        if not self._connection:
            raise NotConnectedError("Not connected")
        await self._connection.disconnect()
        self.connected = False
        self._connection = None

    async def execute(self, stmt: LiteralString) -> int:
        """Execute statement to change, add or delete etc.

        ROUTINES/PROCEDURES/FUNCTIONS 'Can execute without error' but has no returns.

        Always `COMMIT` and `ROLLBACK` is automatic!!! This is not changeable...
        if you transaction failed your receive a except with error.

        Exception example:
        ``` python
            sqlx_engine.core.errors.RawQueryError:
            {
                "is_panic": false,
                "error_code": "P2010",
                "error_message": "Raw query failed. Code: `23505`. Message: `Key (id)=(a7e382c9-8d6d-4233-b1be-be9ef6024bd5) already exists.`",
                "meta": {
                    "code": "23505",
                    "message": "Key (id)=(a7e382c9-8d6d-4233-b1be-be9ef6024bd5) already exists."
                },
                "helper": "https://www.prisma.io/docs/reference/api-reference/error-reference#error-codes",
                "description": "Raw query failed. Code: {code}. Message: {message}"
            }

        ```
        Args:
            stmt (LiteralString): Insert, Update, Delete, Drop etc. `Query NO`!

        Returns:
            int: Number of rows affected

        Raises:
            SQLXEngineError |
            UniqueViolationError |
            ForeignKeyViolationError |
            FieldNotFoundError |
            RawQueryError |
            MissingRequiredValueError |
            InputError |
            TableNotFoundError |
            RecordNotFoundError |
            GenericSQLXEngineError
        """
        if not self._connection:
            raise NotConnectedError("Not connected")
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
        Raises:
            SQLXEngineError
        """
        if not self._connection:
            raise NotConnectedError("Not connected")
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
