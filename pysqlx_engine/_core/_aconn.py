from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import pysqlx_core
from pysqlx_engine._core.parser import BaseRow, Parser
from pysqlx_engine._error.errors import NotConnectedError, pysqlx_get_error

LiteralString = str


class PySQLXEngine:
    """
    PySQLXEngine is an engine to run pure sql, but you have flexibility to use how you want.

    All SQL that is executed using the PySQLXEngine is atomic; that is,
    only one statement is performed at a time. Only the first one will
    be completed if you send an Insert and a select.
    This is one of the ways to deal with SQL ingestion.

    By default the `BEGIN`, `COMMIT` and `ROLLBACK` is automatic, if the sql is valid, is committed, if not, is rolled back.
    But you can use the `BEGIN` and `COMMIT` or `ROLLBACK` to control the transaction.

    `providers(str)`: postgresql, mysql, sqlserver or sqlite
    `uri(str)`:  Connection values.
    `timeout(int)`: Default 10 sec, used to close the connection after this time. Or None to removed timeout.
    `improved_error_log(bool)`: Default True. Returns an error in json format with colors.

    Usage:
    ``` python
    >>> ##### PostgreSQL
    >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
    >>> conn = PySQLXEngine(uri=uri)
    #------------------------------------------
    >>> ##### MySQL
    >>> uri = "mysql://user:pass@host:port/db?schema=sample"
    >>> conn = PySQLXEngine( uri=uri)
    #------------------------------------------
    >>> ##### Microsoft SQL Server
    >>> uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
    >>> conn = PySQLXEngine(uri=uri)
    #------------------------------------------
    >>> ##### SQLite
    >>> uri = "sqlite:./dev.db"
    >>> conn = PySQLXEngine(uri=uri)
    ```
    """

    __slots__ = ("_conn", "_uri", "connected")

    def __init__(self, uri: str):
        _providers = ["postgresql", "mysql", "sqlserver", "sqlite"]

        if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
            raise ValueError(f"invalid uri: {uri}, check the usage uri, accepted providers: {', '.join(_providers)}")

        if uri.startswith("sqlite"):
            uri = uri.replace("sqlite", "file", 1)

        self._uri: str = uri
        self._conn: pysqlx_core.Connection = None
        self.connected: bool = False

    def __del__(self):
        if self.connected:
            self._conn = None
            self.connected = False

    def is_healthy(self) -> bool:
        """
        Check if the connection is healthy.
        Returns false, if connection is considered to not be in a working state.
        """
        self._check_connection()
        return self._conn.is_healthy()

    def requires_isolation_first(self) -> bool:
        """Returns `True` if the connection requires isolation first, `False` otherwise.
        This is used to determine if the connection should be isolated before executing a query.
        for example, sqlserver requires isolation before executing a query using begin.

        - Signals if the isolation level SET needs to happen before or after the BEGIN

        * [SQL Server documentation]: (https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15)
        * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
        * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
        * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        self._check_connection()
        return self._conn.requires_isolation_first()

    async def __aenter__(self) -> "PySQLXEngine":
        """Open a connection to the database. using `async with`"""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if self.connected():
            await self.close()

    async def connect(self) -> None:
        """
        Every connection instance is lazy, only after the .connect() is the
        database checked and a connection is created with it.
        """
        try:
            self._conn = await pysqlx_core.new(uri=self._uri)
            self.connected = True
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def close(self) -> None:
        """Is good always close the connection, but!
        Even if you don't close the connection, don't worry,
        when the process ends automatically the connections will
        be closed so the bank doesn't have an idle connection.
        """
        self._conn = None
        self.connected = False

    async def raw_cmd(self, sql: LiteralString) -> "str":
        """
        Run a command in the database, for queries that can't be run using prepared statements.
        """
        self._check_connection()
        try:
            return await self._conn.raw_cmd(sql=sql)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query(self, query: LiteralString) -> Union[List[BaseRow], List]:
        self._check_connection()
        try:
            result = await self._conn.query(sql=query)
            return Parser(result).parse()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_first(self, query: LiteralString) -> Union[BaseRow, None]:
        """Returns the first row of the query result with BaseRow or None."""
        self._check_connection()
        try:
            result = await self._conn.query(sql=query)
            return Parser(result).parse_first()
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_as_list(self, query: LiteralString) -> Union[List[Dict[str, Any]], List]:
        """Returns a list of dictionaries representing the rows of the query result."""
        self._check_connection()
        try:
            return await self._conn.query_as_list(sql=query)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def query_first_as_dict(self, query: LiteralString) -> Union[Dict[str, Any], None]:
        """Returns the first row as dict or None case not data."""
        self._check_connection()
        try:
            rows = await self._conn.query_as_list(sql=query)
            if rows:
                return rows[0]
            return None
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def execute(self, stmt: LiteralString) -> int:
        """Executes a query and returns the number of rows affected."""
        self._check_connection()
        try:
            return await self._conn.execute(sql=stmt)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def set_isolation_level(self, level: pysqlx_core.IsolationLevel) -> None:
        """
        Sets the isolation level of the connection.
        The isolation level is set before the transaction is started.
        Is used to separate the transaction per level.

        * [SQL Server documentation]: (https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15)
        * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
        * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
        * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        self._check_connection()
        try:
            await self._conn.set_isolation_level(level=level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    async def start_transaction(self, isolation_level: Union[pysqlx_core.IsolationLevel, None] = None) -> None:
        """Starts a transaction with BEGIN. by default, does not set the isolation level."""
        self._check_connection()
        try:
            await self._conn.start_transaction(isolation_level=isolation_level)
        except pysqlx_core.PySQLXError as e:
            raise pysqlx_get_error(err=e)

    def _check_connection(self):
        if not self.connected:
            raise NotConnectedError("Not connected")
