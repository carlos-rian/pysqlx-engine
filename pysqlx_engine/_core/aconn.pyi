from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union, overload

from typing_extensions import Literal

from .errors import (
    ConnectError,
    ExecuteError,
    IsoLevelError,
    QueryError,
    RawCmdError,
    StartTransactionError,
)
from .parser import BaseRow, Model

LiteralString = str

ISOLATION_LEVEL = Literal["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]

class PySQLXEngine:
    """
    ### Description
    PySQLXEngine is an engine to run pure sql, but you have flexibility to use how you want.

    All SQL that is executed using the PySQLXEngine is atomic; that is,
    only one statement is performed at a time. Only the first one will
    be completed if you send an Insert and a select.
    This is one of the ways to deal with SQL ingestion.

    By default the `BEGIN`, `COMMIT` and `ROLLBACK` is automatic (CASE DATABASE NOT NEED REQUIRES ISOLATION FIRST),
    if the sql is valid, is committed, if not, is rolled back.
    But you can use the `BEGIN` and `COMMIT` or `ROLLBACK` to control the transaction.

    ---

    #### Arguments:
        `uri(str)`:  uri of the database, example `postgresql://user:pass@host:port/db?schema=sample`

    ---

    #### URI Starts With:
        * `postgresql`
        * `mysql`
        * `sqlite`
        * `mssql`
    ---

    #### Usage:

    ##### PostgreSQL
    ```python
    uri = "postgresql://user:pass@host:port/db?schema=sample"
    conn = PySQLXEngine(uri=uri)
    await conn.connect()
    ```
    ---
    ##### MySQL
    ```python
    uri = "mysql://user:pass@host:port/db?schema=sample"
    conn = PySQLXEngine( uri=uri)
    await conn.connect()
    ```
    ---
    ##### Microsoft SQL Server
    ```python
    uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
    conn = PySQLXEngine(uri=uri)
    await conn.connect()
    ```
    ---
    ##### SQLite
    ```python
    uri = "sqlite:./dev.db"
    conn = PySQLXEngine(uri=uri)
    await conn.connect()
    ```
    """

    __slots__ = ["uri", "connected", "_conn", "_provider"]

    uri: str
    connected: bool

    def __init__(self, uri: str) -> "None": ...
    def __del__(self):
        """
        ## Description

        Automatically close the connection when the object is deleted.
        """
        ...
    def is_healthy(self) -> "bool":
        """
        ## Description

        Check if the connection is healthy.

        Returns false, if connection is considered to not be in a working state.

        * Arguments: `None`

        * Returns: `bool`

        * Raises: `None`

        """
        ...
    def requires_isolation_first(self) -> "bool":
        """
        ## Description
        Returns `True` if the connection requires isolation first, `False` otherwise.

        This is used to determine if the connection should be isolated before executing a query.

        For example, sqlserver requires isolation before executing a statement using begin in some cases.

        Signals if the isolation level SET needs to happen before or after the BEGIN.

        * Arguments: `None`

        * Returns: `bool`

        * Raises: `None`

        ---
        ### Extra documentation:
        * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
        * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
        * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
        * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
    async def __aenter__(self) -> "PySQLXEngine":
        """
        ## Description
        Open a connection to the database. using `async with`
        """
        ...
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    async def connect(self) -> "None":
        """
        ## Description
        Every connection instance is lazy, only after the .connect() is the
        database checked and a connection is created with it.

        .connect() establishes a connection to the database.

        when you use `async with` the connection is automatically opened and closed.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `ConnectError`

        ---
        ### Example
        ```python
            db = PySQLXEngineSync(uri=uri)
            await db.connect()
        ```
        """
        raise ConnectError()
    async def close(self) -> "None":
        """
        ## Description
        Is good always close the connection, but!
        Even if you don't close the connection, don't worry,
        when the process ends automatically the connections will
        be closed so the bank doesn't have an idle connection.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `None`

        ---
        ### Example
        ```python
            db = PySQLXEngineSync(uri=uri)
            await db.connect()
            await db.close()
        ```
        """
        ...
    async def raw_cmd(self, sql: LiteralString) -> "None":
        """
        ## Description
        Run a command in the database, for queries that can't be run using prepared statements.

        * Arguments: `sql(str)`:  sql to be executed

        * Returns: `None`

        * Raises: `RawCmdError`

        ---
        ### Example
        `SET TRANSACTION ISOLATION LEVEL READ COMMITTED;`

        """
        raise RawCmdError()
    # all
    @overload
    async def query(self, sql: LiteralString) -> Union[List[BaseRow], List]:
        """
        ## Description
        Returns all rows of the query result with List of `BaseRow` or List of Dict or empty List.

        #### BaseRow
            Is a class that represents a row of the result of a query.
            Is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        #### Model
            Is a class that represents a row of the result of a query.
            This class is created by the user, it is a class that inherits from `BaseRow`.

        #### Dict
            Is a dict that represents a row of the result of a query.

        #### Helper
            * Arguments:

                `sql(str)`: sql query to be executed

                `as_dict(bool)`: (Default is False) if True, returns a list of dict, if False, returns a list of BaseRow

                `model(BaseRow)`: (Default is None) if not None, returns a list of your model

            * Returns: `Union[List[BaseRow], List[Dict], List]`: List of `BaseRow` or List of Dict or empty List

            * Raises: `QueryError`, `TypeError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            result = await conn.query("SELECT 1 as id, 'rian' as name")
            print(result)
            # output -> [BaseRow(id=1, name='rian')]

            result = await conn.query("SELECT 1 as id, 'rian' as name", as_dict=True)
            print(result)
            # output -> [{'id': 1, 'name': 'rian'}]

        ```
        """
        raise QueryError()
    @overload
    async def query(self, sql: LiteralString, model: Type["Model"] = None) -> Union[List[Type["Model"]], List]: ...
    @overload
    async def query(self, sql: LiteralString, as_dict: bool = False) -> Union[List[Dict[str, Any]], List]: ...
    # fisrt
    @overload
    async def query_first(self, sql: LiteralString) -> Union[BaseRow, None]:
        """
        ## Description
        Returns the first row of the query result with BaseRow or Dict(case as_dict=True) or None case result is empty.

        #### BaseRow
            Is a class that represents a row of the result of a query.
            Is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        #### Model
            Is a class that represents a row of the result of a query.
            This class is created by the user, it is a class that inherits from `BaseRow`.

        #### Dict
            Is a dict that represents a row of the result of a query.

        #### Helper

            * Arguments:

                `sql(str)`:  sql to be executed

                `as_dict(bool)`: (Default is False) if True, returns a dict, if False, returns a BaseRow

                `model(BaseRow)`: (Default is None) if not None, returns a row of your model

            * Returns: `Union[BaseRow, Dict, None]`: a `BaseRow` or Dict or None

            * Raises: `QueryError`, `TypeError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            result = await conn.query_first("SELECT 1 as id, 'rian' as name")
            print(result)
            # output -> BaseRow(id=1, name='rian')

            result = await conn.query_first("SELECT 1 as id, 'rian' as name", as_dict=True)
            print(result)
            # output -> {'id': 1, 'name': 'rian'}
        ```
        """
        raise QueryError()
    @overload
    async def query_first(self, sql: LiteralString, model: Type["Model"] = None) -> Union[Type["Model"], None]: ...
    @overload
    async def query_first(self, sql: LiteralString, as_dict: bool = False) -> Union[Dict[str, Any], None]: ...
    # --
    async def execute(self, sql: LiteralString) -> "int":
        """
        ## Description
        Executes a query/sql and returns the number of rows affected.

        * Arguments: `sql(str)`:  sql to be executed

        * Returns: `int`: number of rows affected

        * Raises: `ExecuteError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            result = await conn.execute("INSERT INTO users (name) VALUES ('rian')")
            print(f"rows_affected = {result}")
            # output -> rows_affected = 1
        ```
        """
        raise ExecuteError()
    async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL) -> "None":
        """
        ## Description
        Sets the isolation level of the connection.

        The isolation level is set before the transaction is started.
        Is used to separate the transaction per level.

        The `Snapshot` isolation level is supported by MS SQL Server.

        The Sqlite does not support the isolation level.

        * Arguments: `isolation_level(str)`:  isolation level to be set (`ReadUncommitted`,`ReadCommitted`,`RepeatableRead`,`Snapshot`,`Serializable`)

        * Returns: `None`

        * Raises: `IsolationLevelError`, `ValueError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()
            await conn.set_isolation_level(isolation_level="READ_COMMITTED")
        ```
        ---
        ### Isolation Level Help
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        IsoLevelError()
    async def begin(self) -> "None":
        """
        ## Description
        Starts a transaction using `BEGIN`.

        begin() is equivalent to start_transaction() without setting the isolation level.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `RawCmdError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()
            await conn.begin()
        ```
        """
        raise RawCmdError()
    async def commit(self) -> "None":
        """
        ## Description
        Commits the current transaction.

        The `begin()` method must be called before calling `commit()`.

        If the database not need set the isolation level, maybe you can not use `begin()` and `commit()`.

        The PySQLXEngine by default uses the `begin()` and `commit()` in all transactions.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `RawCmdError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            await conn.begin()
            await conn.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
            await conn.execute("INSERT INTO users (name) VALUES ('rian')")
            await conn.commit()
        ```
        """
        raise RawCmdError()
    async def rollback(self) -> "None":
        """
        ## Description
        Rollbacks the current transaction.

        Rollback is used to cancel the transaction, when you uses the rollback,
        the transaction is canceled and the changes are not saved.

        The `begin()` method must be called before calling `rollback()`.

        If the database not need set the isolation level, maybe you can not use `begin()` and `rollback()`.

        The PySQLXEngine by default try uses the `begin()` and `commit()` in all transactions.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `RawCmdError`

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            await conn.begin()
            await conn.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
            await conn.execute("INSERT INTO users (name) VALUES ('rian')")
            await conn.rollback()
        ```
        """
        raise RawCmdError()
    async def start_transaction(self, isolation_level: Union[ISOLATION_LEVEL, None] = None) -> "None":
        """
        ## Description
        Starts a transaction with BEGIN. by default, does not set the isolation level.

        The `Snapshot` isolation level is supported by MS SQL Server.

        The Sqlite does not support the isolation level.

        * Arguments: `isolation_level(str)`: by default is None. Isolation level to be set (ReadUncommitted, ReadCommitted, RepeatableRead, Snapshot, Serializable)

        * Returns: `None`

        * Raises: (`IsolationLevelError`, `StartTransactionError` `ValueError`)

        ---
        ### Example
        ```python
            uri = "postgresql://user:pass@host:port/db?schema=sample"
            conn = PySQLXEngine(uri=uri)
            await conn.connect()

            # with isolation level
            await conn.start_transaction(isolation_level="ReadCommitted")

            # without isolation level
            await conn.start_transaction()
        ```
        ---
        ### Isolation Level Help
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        raise StartTransactionError()
