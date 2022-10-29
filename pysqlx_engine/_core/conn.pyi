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

    #### Arguments:
        `uri(str)`:  uri of the database, Example `postgresql://user:pass@host:port/db?schema=sample`

    ---

    #### URI Starts With:
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
    def __enter__(self) -> "PySQLXEngine":
        """
        ## Description
        Open a connection to the database. using `with`
        """
        ...
    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
    ): ...
    def connect(self) -> "None":
        """
        ## Description
        Every connection instance is lazy, only after the .connect() is the
        database checked and a connection is created with it.

        .connect() establishes a connection to the database.

        when you use `with` the connection is automatically opened and closed.

        * Arguments: `None`

        * Returns: `None`

        * Raises: `ConnectError`

        ---
        ### Example
            >>> db = PySQLXEngineSync(uri=uri)
            >>> db.connect()
        """
        raise ConnectError()
    def close(self) -> "None":
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
            >>> db = PySQLXEngineSync(uri=uri)
            >>> db.connect()
            >>> db.close()

        """
        ...
    def raw_cmd(self, sql: LiteralString) -> "None":
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
        ...
    def query(self, query: LiteralString, as_dict: bool = False) -> "Union[List[BaseRow], List[Dict], List]":
        """
        ## Description
        Returns all rows of the query result with List of `BaseRow` or List of Dict or empty List.

        #### BaseRow
            Is a class that represents a row of the result of a query.
            Is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        #### Dict
            Is a dict that represents a row of the result of a query.

        #### Helper
            * Arguments:

                `query(str)`:  sql to be executed

                `as_dict(bool)`: (Default is False) if True, returns a list of dict, if False, returns a list of BaseRow

            * Returns: `Union[List[BaseRow], List[Dict], List]`: List of `BaseRow` or List of Dict or empty List

            * Raises: `QueryError`

        ---
        ### Example
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.query("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output -> [BaseRow(id=1, name='rian')]
            >>> result = conn.query("SELECT 1 as id, 'rian' as name", as_dict=True)
            >>> print(result)
            >>> # output -> [{'id': 1, 'name': 'rian'}]

        """
        raise QueryError()
    def query_first(self, query: LiteralString, as_dict: bool = False) -> "Union[BaseRow, Dict, None]":
        """
        ## Description
        Returns the first row of the query result with BaseRow or Dict(case as_dict=True) or None case result is empty.

        #### BaseRow
            Is a class that represents a row of the result of a query.
            Is a class created from `Pydantic`, then you have all the benefits of `Pydantic`.

        #### Dict
            Is a dict that represents a row of the result of a query.

        #### Helper

            * Arguments:

                `query(str)`:  sql to be executed

                `as_dict(bool)`: (Default is False) if True, returns a dict, if False, returns a BaseRow

            * Returns: `Union[BaseRow, Dict, None]`: a `BaseRow` or Dict or None

            * Raises: `QueryError`

        ---
        ### Example
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngine(uri=uri)
            >>> conn.connect()
            >>> result = conn.query_first("SELECT 1 as id, 'rian' as name")
            >>> print(result)
            >>> # output -> BaseRow(id=1, name='rian')
            >>> result = conn.query_first("SELECT 1 as id, 'rian' as name", as_dict=True)
            >>> print(result)
            >>> # output -> {'id': 1, 'name': 'rian'}

        """
        raise QueryError()
    def execute(self, stmt: LiteralString) -> "int":
        """
        ## Description
        Executes a query/sql and returns the number of rows affected.

        * Arguments: `stmt(str)`:  sql to be executed

        * Returns: `int`: number of rows affected

        * Raises: `ExecuteError`

        ---
        ### Example
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> result = conn.execute("INSERT INTO users (name) VALUES ('rian')")
            >>> print(f"rows_affected = {result}")
            >>> # output -> rows_affected = 1

        """
        raise ExecuteError()
    def set_isolation_level(self, isolation_level: ISOLATION_LEVEL) -> "None":
        """
        ## Description
        Sets the isolation level of the connection.

        The isolation level is set before the transaction is started.
        Is used to separate the transaction per level.

        * Arguments: `isolation_level(str)`:  isolation level to be set (ReadUncommitted, ReadCommitted, RepeatableRead, Snapshot, Serializable)

        * Returns: `None`

        * Raises: `IsolationLevelError`, `ValueError`

        ---
        ### Example
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> conn.set_isolation_level(isolation_level="READ_COMMITTED")

        ---
        ### Isolation Level Help
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
    def start_transaction(self, isolation_level: Union[ISOLATION_LEVEL, None] = None) -> "None":
        """
        ## Description
        Starts a transaction with BEGIN. by default, does not set the isolation level.

        * Arguments: `isolation_level(str)`: by default is None. Isolation level to be set (ReadUncommitted, ReadCommitted, RepeatableRead, Snapshot, Serializable)

        * Returns: `None`

        * Raises: (`IsolationLevelError`, `StartTransactionError` `ValueError`)

        ---
        ### Example
            >>> uri = "postgresql://user:pass@host:port/db?schema=sample"
            >>> conn = PySQLXEngineSync(uri=uri)
            >>> conn.connect()
            >>> # with isolation level
            >>> conn.start_transaction(isolation_level="ReadCommitted")
            >>> # without isolation level
            >>> conn.start_transaction()

        ---
        ### Isolation Level Help
            * [SQL Server documentation]: (https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
            * [Postgres documentation]: (https://www.postgresql.org/docs/current/sql-set-transaction.html)
            * [MySQL documentation]: (https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
            * [SQLite documentation]: (https://www.sqlite.org/isolation.html)
        """
        ...
