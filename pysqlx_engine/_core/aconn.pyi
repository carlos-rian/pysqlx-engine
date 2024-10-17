from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union, overload

from .const import ISOLATION_LEVEL
from .parser import (  # import necessary using _core to not subscribe default parser
	BaseRow,
	DictParam,
	MyModel,
)

class PySQLXEngine:
	"""
	## Description

	PySQLXEngine is an engine to run pure sql, but you have flexibility to use how you want.

	All SQL that is executed using the PySQLXEngine is atomic; that is, only one statement is performed at a time.

	Only the first one will be completed if you send an Insert and a select.
	This is one of the ways to deal with SQL ingestion.

	By default the `BEGIN`, `COMMIT` and `ROLLBACK` is automatic (CASE DATABASE NOT NEED REQUIRES ISOLATION FIRST), if the sql is valid, is committed, if not, is rolled back.

	But you can use the `BEGIN` and `COMMIT` or `ROLLBACK` to control the transaction.

	---

	### Arguments:

	    `uri(str)`: uri of the database, example `postgresql://user:pass@host:port/db?schema=sample`

	---

	### Examples:


	##### PostgreSQL
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "postgresql://user:pass@host:port/db?schema=sample"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---
	##### MySQL
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "mysql://user:pass@host:port/db?schema=sample"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---
	##### Microsoft SQL Server
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---
	##### SQLite
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "sqlite:./dev.db"
	db = PySQLXEngine(uri=uri)
	await db.connect()
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

		---

		### Helper

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

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `bool`

		    * Raises: `None`

		---

		### Extra documentation:
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)
		"""
		...
	async def __aenter__(self) -> "PySQLXEngine":
		"""
		## Description

		Open a connection to the database. using `async with`.
		"""
		...
	async def __aexit__(
		self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
	): ...
	async def connect(self) -> "None":
		"""
		## Description

		Each connection instance is lazy; only after `.connect()` is the database checked and the connection established.

		When you use `async with` the connection is automatically opened and closed.

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `None`

		    * Raises: `ConnectError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngineSync(uri=uri)
		    await db.connect()
		```
		"""
		...
	async def close(self) -> "None":
		"""
		## Description

		It's a good idea to close the connection, but PySQLXEngine has the core in Rust;
		closing is automatic when your code leaves the context.

		Even if you don't close the connection, don't worry; when the process ends automatically,
		the connections will be closed, so the database doesn't have an idle connection.

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `None`

		    * Raises: `None`

		---

		### Example
		``python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()
		    await db.close()
		``
		"""
		...
	async def raw_cmd(self, sql: str) -> "None":
		"""
		## Description

		Run a command in the database, for queries that can't be run using prepared statements(queries/execute).

		---

		### Helper

		    * Arguments:

		        `sql(str)`: sql to be executed.

		    * Returns: `None`

		    * Raises: `RawCmdError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    await db.raw_cmd(sql="SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

		```
		"""
		...
	# all
	@overload
	async def query(self, sql: str) -> Union[List[BaseRow], List]: ...
	@overload
	async def query(self, sql: str, parameters: Optional[DictParam] = None) -> Union[List[BaseRow], List]: ...
	async def query(
		self, sql: str, parameters: Optional[DictParam] = None, model: Optional[Type["MyModel"]] = None
	) -> Union[List[Type["MyModel"]], List]:
		"""
		## Description

		Returns all rows from query result as`BaseRow list`, `MyModel list` or `empty list`.

		---

		### Helper
		    * Arguments:

		        `sql(str)`: sql query to be executed.

		        `parameters(dict)`: (default is None) parameters must be a dictionary with the name of the parameter and the value.

		        `model(BaseRow)`: (default is None) is your model that inherits from BaseRow.

		    * Returns:

		        `List[BaseRow] | List[MyModel] | List`: BaseRow list, MyModel list or empty list.

		    * Raises: `QueryError`|`TypeError` | `ParameterInvalidProviderError`|`ParameterInvalidValueError`|`ParameterInvalidJsonValueError`

		---

		### Parameters Helper

		Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
		although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
		This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

		#### SQL with parameters syntax
		    * SQL: `SELECT * FROM table WHERE id = :id`
		    * Parameters: `{"id": 1}`

		#### Parameters(dict):

		    * dict `key` must be a valid string.
		    * dict `value` can be one of the types: (
		        `bool`,
		        `bytes`,
		        `date`,
		        `datetime`,
		        `Decimal`,
		        `dict`,
		        `Enum`, # Enum must be a subclass of enum.Enum
		        `float`,
		        `int`,
		        `list`,
		        `str`,
		        `time`,
		        `tuple`,
		        `UUID`,
		        `None`
		    )

		#### Python types vs SQL types:

		    [Documentation](https://carlos-rian.github.io/pysqlx-engine/type_mappings/)

		``
		    * bool     -> bool|bit|boolean|tinyint|etc
		    * bytes    -> bytea|binary|varbinary|etc
		    * date     -> date|nvarchar|varchar|string|etc
		    * datetime -> timestamp|timestamptz|datetime|datetime2|nvarchar|varchar|string|etc
		    * Decimal  -> decimal|numeric|etc
		    * dict     -> json|jsonb|nvarchar|varchar|string|etc
		    * float    -> float|real|numeric|etc
		    * int      -> int|integer|smallint|bigint|tinyint|etc
		    * list     -> json|jsonb|nvarchar|varchar|string|etc
		    * str      -> varchar|text|nvarchar|char|etc
		    * time     -> time|nvarchar|varchar|string|etc
		    * tuple    -> array(Postgres Native), another database: error.
		    * UUID     -> uuid|varchar|text|nvarchar|etc
		    * Enum     -> varchar|text|nvarchar|etc
		    * None     -> null
		``

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    result = await db.query("SELECT 1 as id, 'rian' as name")
		    print(result)
		    # output -> [BaseRow(id=1, name='rian')]

		    result = await db.query(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
		    print(result)
		    # output -> [BaseRow(id=1, name='rian')]

		    await db.close()

		```
		"""
		...
	# dict
	@overload
	async def query_as_dict(self, sql: str) -> Union[List[Dict[str, Any]], List]: ...
	async def query_as_dict(
		self, sql: str, parameters: Optional[DictParam] = None
	) -> Union[List[Dict[str, Any]], List]:
		"""
		## Description

		Returns all rows from query result as `dict list` or `empty list`.

		---

		### Helper
		    * Arguments:

		        `sql(str)`: sql query to be executed

		        `parameters(dict)`: (default is None) parameters must be a dictionary with the name of the parameter and the value.

		    * Returns:

		        `List[Dict[str, Any]] | List`: dict list or empty list.

		    * Raises: `QueryError`|`TypeError` | `ParameterInvalidProviderError`|`ParameterInvalidValueError`|`ParameterInvalidJsonValueError`

		---

		### Parameters Helper

		Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
		although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
		This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

		#### SQL with parameters syntax
		    * SQL: `SELECT * FROM table WHERE id = :id`
		    * Parameters: `{"id": 1}`

		#### Parameters(dict):

		    * dict `key` must be a valid string.
		    * dict `value` can be one of the types: (
		        `bool`,
		        `bytes`,
		        `date`,
		        `datetime`,
		        `Decimal`,
		        `dict`,
		        `Enum`, # Enum must be a subclass of enum.Enum
		        `float`,
		        `int`,
		        `list`,
		        `str`,
		        `time`,
		        `tuple`,
		        `UUID`,
		        `None`
		    )

		#### Python types vs SQL types:

		    [Documentation](https://carlos-rian.github.io/pysqlx-engine/type_mappings/)

		``
		    * bool     -> bool|bit|boolean|tinyint|etc
		    * bytes    -> bytea|binary|varbinary|etc
		    * date     -> date|nvarchar|varchar|string|etc
		    * datetime -> timestamp|timestamptz|datetime|datetime2|nvarchar|varchar|string|etc
		    * Decimal  -> decimal|numeric|etc
		    * dict     -> json|jsonb|nvarchar|varchar|string|etc
		    * float    -> float|real|numeric|etc
		    * int      -> int|integer|smallint|bigint|tinyint|etc
		    * list     -> json|jsonb|nvarchar|varchar|string|etc
		    * str      -> varchar|text|nvarchar|char|etc
		    * time     -> time|nvarchar|varchar|string|etc
		    * tuple    -> array(Postgres Native), another database: error.
		    * UUID     -> uuid|varchar|text|nvarchar|etc
		    * Enum     -> varchar|text|nvarchar|etc
		    * None     -> null
		``

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    result = await db.query_as_dict(sql="SELECT 1 as id, 'rian' as name")
		    print(result)
		    # output -> [{'id': 1, 'name': 'rian'}]

		    result = await db.query_as_dict(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
		    print(result)
		    # output -> [{'id': 1, 'name': 'rian'}]

		    await db.close()
		```
		"""
		...
	# fisrt
	@overload
	async def query_first(self, sql: str) -> Union[BaseRow, None]: ...
	@overload
	async def query_first(self, sql: str, parameters: DictParam = None) -> Union[BaseRow, None]: ...
	async def query_first(
		self, sql: str, parameters: DictParam = None, model: Type["MyModel"] = None
	) -> Union[Type["MyModel"], None]:
		"""
		## Description

		Returns first row from query result as `BaseRow`, `MyModel` or `None`.

		---

		### Helper
		    * Arguments:

		        `sql(str)`: sql query to be executed.

		        `parameters(dict)`: (default is None) parameters must be a dictionary with the name of the parameter and the value.

		        `model(BaseRow)`: (default is None) is your model that inherits from BaseRow.

		    * Returns:

		        `BaseRow | MyModel | None`: BaseRow, MyModel or None if no rows are found.

		    * Raises: `QueryError`|`TypeError` | `ParameterInvalidProviderError`|`ParameterInvalidValueError`|`ParameterInvalidJsonValueError`

		---

		### Parameters Helper

		Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
		although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
		This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

		#### SQL with parameters syntax
		    * SQL: `SELECT * FROM table WHERE id = :id`
		    * Parameters: `{"id": 1}`

		#### Parameters(dict):

		    * dict `key` must be a valid string.
		    * dict `value` can be one of the types: (
		        `bool`,
		        `bytes`,
		        `date`,
		        `datetime`,
		        `Decimal`,
		        `dict`,
		        `Enum`, # Enum must be a subclass of enum.Enum
		        `float`,
		        `int`,
		        `list`,
		        `str`,
		        `time`,
		        `tuple`,
		        `UUID`,
		        `None`
		    )

		#### Python types vs SQL types:

		    [Documentation](https://carlos-rian.github.io/pysqlx-engine/type_mappings/)

		``
		    * bool     -> bool|bit|boolean|tinyint|etc
		    * bytes    -> bytea|binary|varbinary|etc
		    * date     -> date|nvarchar|varchar|string|etc
		    * datetime -> timestamp|timestamptz|datetime|datetime2|nvarchar|varchar|string|etc
		    * Decimal  -> decimal|numeric|etc
		    * dict     -> json|jsonb|nvarchar|varchar|string|etc
		    * float    -> float|real|numeric|etc
		    * int      -> int|integer|smallint|bigint|tinyint|etc
		    * list     -> json|jsonb|nvarchar|varchar|string|etc
		    * str      -> varchar|text|nvarchar|char|etc
		    * time     -> time|nvarchar|varchar|string|etc
		    * tuple    -> array(Postgres Native), another database: error.
		    * UUID     -> uuid|varchar|text|nvarchar|etc
		    * Enum     -> varchar|text|nvarchar|etc
		    * None     -> null
		``

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    result = await db.query_first("SELECT 1 as id, 'rian' as name")
		    print(result)
		    # output -> BaseRow(id=1, name='rian')

		    result = await db.query_first(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
		    print(result)
		    # output -> BaseRow(id=1, name='rian')

		    await db.close()

		```
		"""
		...
	# dict
	@overload
	async def query_first_as_dict(self, sql: str) -> Optional[Dict[str, Any]]: ...
	async def query_first_as_dict(self, sql: str, parameters: Optional[DictParam] = None) -> Optional[Dict[str, Any]]:
		"""
		## Description

		Returns first row from query result as `dict` or `None`.

		---

		### Helper
		    * Arguments:

		        `sql(str)`: sql query to be executed.

		        `parameters(dict)`: (default is None) parameters must be a dictionary with the name of the parameter and the value.

		    * Returns:

		        `Dict[str, Any] | None`: dict or None.

		    * Raises: `QueryError`|`TypeError` | `ParameterInvalidProviderError`|`ParameterInvalidValueError`|`ParameterInvalidJsonValueError`

		---

		### Parameters Helper

		Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
		although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
		This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

		#### SQL with parameters syntax
		    * SQL: `SELECT * FROM table WHERE id = :id`
		    * Parameters: `{"id": 1}`

		#### Parameters(dict):

		    * dict `key` must be a valid string.
		    * dict `value` can be one of the types: (
		        `bool`,
		        `bytes`,
		        `date`,
		        `datetime`,
		        `Decimal`,
		        `dict`,
		        `Enum`, # Enum must be a subclass of enum.Enum
		        `float`,
		        `int`,
		        `list`,
		        `str`,
		        `time`,
		        `tuple`,
		        `UUID`,
		        `None`
		    )

		#### Python types vs SQL types:

		    [Documentation](https://carlos-rian.github.io/pysqlx-engine/type_mappings/)

		``
		    * bool     -> bool|bit|boolean|tinyint|etc
		    * bytes    -> bytea|binary|varbinary|etc
		    * date     -> date|nvarchar|varchar|string|etc
		    * datetime -> timestamp|timestamptz|datetime|datetime2|nvarchar|varchar|string|etc
		    * Decimal  -> decimal|numeric|etc
		    * dict     -> json|jsonb|nvarchar|varchar|string|etc
		    * float    -> float|real|numeric|etc
		    * int      -> int|integer|smallint|bigint|tinyint|etc
		    * list     -> json|jsonb|nvarchar|varchar|string|etc
		    * str      -> varchar|text|nvarchar|char|etc
		    * time     -> time|nvarchar|varchar|string|etc
		    * tuple    -> array(Postgres Native), another database: error.
		    * UUID     -> uuid|varchar|text|nvarchar|etc
		    * Enum     -> varchar|text|nvarchar|etc
		    * None     -> null
		``

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    result = await db.query_first_as_dict(sql="SELECT 1 as id, 'rian' as name")
		    print(result)
		    # output -> {'id': 1, 'name': 'rian'}

		    result = await db.query_first_as_dict(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
		    print(result)
		    # output -> {'id': 1, 'name': 'rian'}

		    await db.close()
		```
		"""
		...
	# --
	@overload
	async def execute(self, sql: str) -> "int": ...
	async def execute(self, sql: str, parameters: Optional[DictParam] = None) -> "int":
		"""
		## Description

		Executes a query/sql and returns the number of rows affected.

		---

		### Helper

		    * Arguments:

		        `sql(str)`:  sql to be executed.

		        `parameters(dict)`: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		    * Returns: `int`: number of rows affected.

		    * Raises: `ExecuteError`|`TypeError` | `ParameterInvalidProviderError`|`ParameterInvalidValueError`|`ParameterInvalidJsonValueError`

		### Parameters Helper

		Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
		although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
		This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

		#### SQL with parameters syntax
		    * SQL: `SELECT * FROM table WHERE id = :id`
		    * Parameters: `{"id": 1}`

		#### Parameters(dict):

		    * dict `key` must be a valid string.
		    * dict `value` can be one of the types: (
		        `bool`,
		        `bytes`,
		        `date`,
		        `datetime`,
		        `Decimal`,
		        `dict`,
		        `Enum`, # Enum must be a subclass of enum.Enum
		        `float`,
		        `int`,
		        `list`,
		        `str`,
		        `time`,
		        `tuple`,
		        `UUID`,
		        `None`
		    )

		#### Python types vs SQL types:

		    [Documentation](https://carlos-rian.github.io/pysqlx-engine/type_mappings/)

		``
		    * bool     -> bool|bit|boolean|tinyint|etc
		    * bytes    -> bytea|binary|varbinary|etc
		    * date     -> date|nvarchar|varchar|string|etc
		    * datetime -> timestamp|timestamptz|datetime|datetime2|nvarchar|varchar|string|etc
		    * Decimal  -> decimal|numeric|etc
		    * dict     -> json|jsonb|nvarchar|varchar|string|etc
		    * float    -> float|real|numeric|etc
		    * int      -> int|integer|smallint|bigint|tinyint|etc
		    * list     -> json|jsonb|nvarchar|varchar|string|etc
		    * str      -> varchar|text|nvarchar|char|etc
		    * time     -> time|nvarchar|varchar|string|etc
		    * tuple    -> array(Postgres Native), another database: error.
		    * UUID     -> uuid|varchar|text|nvarchar|etc
		    * Enum     -> varchar|text|nvarchar|etc
		    * None     -> null
		``

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    result = await db.execute("INSERT INTO users (name) VALUES ('rian')")
		    print(f"rows_affected = {result}")
		    # output -> rows_affected = 1
		```
		"""
		...
	async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL) -> "None":
		"""
		## Description

		Sets the isolation level of the connection.

		The isolation level is set before the transaction is started.
		Is used to separate the transaction per level.

		The `Snapshot` isolation level is supported by MS SQL Server.

		The Sqlite does not support the isolation level.

		---

		### Helper

		    * Arguments: `isolation_level(str)`: isolation level to be set (
		        ReadUncommitted,
		        ReadCommitted,
		        RepeatableRead,
		        Snapshot,
		        Serializable
		    )

		    * Returns: `None`

		    * Raises: `IsolationLevelError`, `ValueError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()
		    await db.set_isolation_level(isolation_level="ReadUncommitted")
		```
		---

		### Isolation Level Help
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)
		"""
		...
	async def begin(self) -> "None":
		"""
		## Description

		Starts a transaction using `BEGIN`.

		`begin()` is equivalent to `start_transaction()` without setting the isolation level.

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `None`

		    * Raises: `RawCmdError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()
		    await db.begin()
		```
		"""
		...
	async def commit(self) -> "None":
		"""
		## Description

		Commits the current transaction.

		The `begin()` method must be called before calling `commit()`.

		If the database not need set the isolation level, maybe you can not use `begin()` and `commit()`.

		The PySQLXEngine by default uses the `begin()` and `commit()` in all transactions.

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `None`

		    * Raises: `RawCmdError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    await db.begin()
		    await db.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
		    await db.execute("INSERT INTO users (name) VALUES ('rian')")
		    await db.commit()
		```
		"""
		...
	async def rollback(self) -> "None":
		"""
		## Description

		Rollbacks the current transaction.

		Rollback is used to cancel the transaction, when you uses the rollback,
		the transaction is canceled and the changes are not saved.

		The `begin()` method must be called before calling `rollback()`.

		If the database not need set the isolation level, maybe you can not use `begin()` and `rollback()`.

		The PySQLXEngine by default try uses the `begin()` and `commit()` in all transactions.

		---

		### Helper

		    * Arguments: `None`

		    * Returns: `None`

		    * Raises: `RawCmdError`

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    await db.begin()
		    await db.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
		    await db.execute("INSERT INTO users (name) VALUES ('rian')")
		    await db.rollback()
		```
		"""
		...
	async def start_transaction(self, isolation_level: Union[ISOLATION_LEVEL, None] = None) -> "None":
		"""
		## Description

		Starts a transaction with `BEGIN/BEGIN TRANSACTION`. by default, does not set the isolation level.

		The `Snapshot` isolation level is supported by MS SQL Server.

		The Sqlite does not support the isolation level.

		---

		### Helper

		    * Arguments: `isolation_level(str)`: by default is None. Isolation level to be set (
		        ReadUncommitted,
		        ReadCommitted,
		        RepeatableRead,
		        Snapshot,
		        Serializable
		    )

		    * Returns: `None`

		    * Raises: (`IsolationLevelError`, `StartTransactionError` `ValueError`)

		---

		### Example
		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "postgresql://user:pass@host:port/db?schema=sample"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()

		    # with isolation level
		    await db.start_transaction(isolation_level="ReadCommitted")

		    # without isolation level
		    await db.start_transaction()
		```

		---

		### Isolation Level Help
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)
		"""
		...
