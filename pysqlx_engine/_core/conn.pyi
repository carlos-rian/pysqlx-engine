from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

from typing_extensions import Literal

from .errors import ConnectError, ExecuteError, QueryError
from .parser import BaseRow

LiteralString = str

ISOLATION_LEVEL = Literal["ReadUncommitted", "ReadCommitted", "RepeatableRead", "Snapshot", "Serializable"]

class PySQLXEngine:
    """
    ### Description
    PySQLXEngineSync is an engine to run pure sql, but you have flexibility to use how you want.

    All SQL that is executed using the PySQLXEngineSync is atomic; that is,
    only one statement is performed at a time. Only the first one will
    be completed if you send an Insert and a select.
    This is one of the ways to deal with SQL ingestion.

    By default the `BEGIN`, `COMMIT` and `ROLLBACK` is automatic (CASE DATABASE NOT NEED REQUIRES ISOLATION FIRST),
    if the sql is valid, is committed, if not, is rolled back.
    But you can use the `BEGIN` and `COMMIT` or `ROLLBACK` to control the transaction.

    ---

    #### parameters:

    `uri(str)`:  uri of the database, example: `postgresql://user:pass@host:port/db?schema=sample`

    ---

    #### uri starts with:
        * `postgresql`
        * `mysql`
        * `sqlite`
        * `mssql`
    ---

    #### Usage:

    ``` python
    >>> ##### PostgreSQL
    >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
    >>> conn = PySQLXEngineSync(uri=uri)
    >>> conn.connect()
    #------------------------------------------
    >>> ##### MySQL
    >>> uri = "mysql://user:pass@host:port/db?schema=sample"
    >>> conn = PySQLXEngineSync( uri=uri)
    >>> conn.connect()
    #------------------------------------------
    >>> ##### Microsoft SQL Server
    >>> uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
    >>> conn = PySQLXEngineSync(uri=uri)
    >>> conn.connect()
    #------------------------------------------
    >>> ##### SQLite
    >>> uri = "sqlite:./dev.db"
    >>> conn = PySQLXEngineSync(uri=uri)
    >>> conn.connect()
    ```
    """

    __slots__ = "_uri"

    uri: str

    def __init__(self, uri: str) -> "None": ...
    def __del__(self):
        """Automatically close the connection when the object is deleted."""
        ...
    def is_healthy(self) -> "bool":
        """
        Check if the connection is healthy.
        Returns false, if connection is considered to not be in a working state.
        """
        ...
    def requires_isolation_first(self) -> "bool":
        """Returns `True` if the connection requires isolation first, `False` otherwise.
        This is used to determine if the connection should be isolated before executing a query.
        for example, sqlserver requires isolation before executing a statement using begin in some cases.

        - Signals if the isolation level SET needs to happen before or after the BEGIN

        * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
        * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
        * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
        * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
    def __enter__(self) -> "PySQLXEngine":
        """Open a connection to the database. using `with`"""
        ...
    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    def connect(self) -> "None":
        """
        Every connection instance is lazy, only after the .connect() is the
        database checked and a connection is created with it.

        .connect() establishes a connection to the database.

        when you use `with` the connection is automatically opened and closed.

        example:
            >>> db = PySQLXEngineSync(uri=uri)
            >>> db.connect()
        """
        raise ConnectError()
    def close(self) -> "None":
        """Is good always close the connection, but!
        Even if you don't close the connection, don't worry,
        when the process ends automatically the connections will
        be closed so the bank doesn't have an idle connection.

        example:
            >>> db = PySQLXEngineSync(uri=uri)
            >>> db.connect()
            >>> db.close()

        """
        ...
    def raw_cmd(self, sql: LiteralString) -> "None":
        """
        Run a command in the database, for queries that can't be run using prepared statements.

        Example: `SET TRANSACTION ISOLATION LEVEL READ COMMITTED;`
        """
        ...
    def query(self, query: LiteralString) -> "Union[List[BaseRow], List]":
        """
        Returns all rows of the query result with List of `BaseRow` or empty List.

        BaseRow is a class that represents a row of the result of a query.

        BaseRow is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.query("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output ->  [BaseRow(id=1, name='rian')]

        """
        raise QueryError()
    def query_first(self, query: LiteralString) -> "Union[BaseRow, None]":
        """
        Returns the first row of the query result with BaseRow or None case result is empty.

        BaseRow is a class that represents a row of the result of a query.

        BaseRow is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.query_first("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output -> BaseRow(id=1, name='rian')

        """
        raise QueryError()
    def query_as_list(self, query: LiteralString) -> "Union[List[Dict[str, Any]], List]":
        """
        Returns a list of dictionaries representing the rows of the query result.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.query_as_list("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output -> [{"id": 1, "name": "rian"}]
        """
        raise QueryError()
    def query_first_as_dict(self, query: LiteralString) -> "Union[Dict[str, Any], None]":
        """
        Returns the first row as dict or None case not data.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.query_first_as_dict("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output -> {"id": 1, "name": "rian"}
        """
        raise QueryError()
    def execute(self, stmt: LiteralString) -> "int":
        """
        Executes a query/sql and returns the number of rows affected.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.execute("INSERT INTO users (name) VALUES ("rian")")
            >>> print(f"rows_affected = {result}")
            >>> # output -> rows_affected = 1

        """
        raise ExecuteError()
    def set_isolation_level(self, isolation_level: ISOLATION_LEVEL) -> "None":
        """
        Sets the isolation level of the connection.

        The isolation level is set before the transaction is started.
        Is used to separate the transaction per level.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> conn.set_isolation_level(isolation_level="READ_COMMITTED")

        isolation_level help:
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
    def start_transaction(self, isolation_level: Union[ISOLATION_LEVEL, None] = None) -> "None":
        """
        Starts a transaction with BEGIN. by default, does not set the isolation level.

        example:
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> # with isolation level
            >>> conn.start_transaction(isolation_level="READ_COMMITTED")
            >>> # without isolation level
            >>> conn.start_transaction()

        isolation_level help:
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
