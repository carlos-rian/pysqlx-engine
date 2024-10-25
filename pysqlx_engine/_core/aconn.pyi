from types import TracebackType
from typing import Dict, List, Optional, Type, Union, overload

from .const import ISOLATION_LEVEL

# import necessary using _core to not subscribe default parser
from .parser import BaseRow, DictParam, MyModel, SupportedTypes

class PySQLXEngine:
	"""

	PySQLXEngine is an engine to run pure sql, but you have flexibility to use how you want.

	All SQL that is executed using the PySQLXEngine is atomic; that is, only one statement is performed at a time.

	Usage docs: https://carlos-rian.github.io/pysqlx-engine

	---

	Attributes:
	    :uri: The connection string to the database.

	---

	Usage:

	- PostgreSQL
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "postgresql://user:pass@host:port/db?schema=sample"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---

	- MySQL
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "mysql://user:pass@host:port/db?schema=sample"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---

	- Microsoft SQL Server
	```python
	from pysqlx_engine import PySQLXEngine

	uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
	db = PySQLXEngine(uri=uri)
	await db.connect()
	```
	---

	- SQLite

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

	def __init__(self, uri: str) -> "None":
		"""
		:uri: The connection string to the database.
		"""
		...
	def __del__(self):
		"""
		Automatically close the connection when the object is deleted.
		"""
		...
	def is_healthy(self) -> "bool":
		"""
		Check if the connection is healthy.

		Returns false, if connection is considered to not be in a working state.

		---

		Returns:
		    A boolean value.
		"""
		...
	def requires_isolation_first(self) -> "bool":
		"""
		Returns `True` if the connection requires isolation first, `False` otherwise.

		This is used to determine if the connection should be isolated before executing a query.

		For example, sqlserver requires isolation before executing a statement using begin in some cases.

		Signals if the isolation level SET needs to happen before or after the BEGIN.

		---

		Returns:
			A boolean value.

		---

		Extra documentation:
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)
		"""
		...
	async def __aenter__(self) -> "PySQLXEngine":
		"""
		Open a connection to the database. using `async with`.
		"""
		...
	async def __aexit__(
		self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], exc_tb: Optional[TracebackType]
	):
		"""
		Close the connection to the database. using `async with`.
		"""
		...
	async def connect(self) -> "None":
		"""
		Each connection instance is lazy; only after `.connect()` is the database checked and the connection established.

		When you use `async with` the connection is automatically opened and closed.

		---

		Raises:
			ConnectError: Raised when the connection to the database fails.

		---

		Usage:

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
		It's a good idea to close the connection, but PySQLXEngine has the core in Rust;
		closing is automatic when your code leaves the context.

		Even if you don't close the connection, don't worry; when the process ends automatically,
		the connections will be closed, so the database doesn't have an idle connection.

		---

		Usage:

		```python
		from pysqlx_engine import PySQLXEngine

		uri = "postgresql://user:pass@host:port/db?schema=sample"
		db = PySQLXEngine(uri=uri)
		await db.connect()
		await db.close()
		```
		"""
		...
	async def raw_cmd(self, sql: str) -> "None":
		"""
		Run a command in the database, for queries that can't be run using prepared statements(queries/execute).

		---

		Args:
			sql: The sql command to be executed.

		Raises:
			RawCmdError: Raised when the command fails.

		---

		Usage:
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
	async def query(self, sql: str, parameters: DictParam) -> Union[List[BaseRow], List]: ...
	@overload
	async def query(self, sql: str, model: Type[MyModel]) -> Union[List[Type[MyModel]], List]: ...
	@overload
	async def query(self, sql: str, parameters: DictParam, model: Type[MyModel]) -> Union[List[Type[MyModel]], List]:
		"""
		Returns all rows from query result as`BaseRow list`, `MyModel list` or `empty list`.

		You can use `:parameter_pattern` in the sql query to use parameters.

		---

		Args:

		    sql: The sql query to be executed.

		    parameters: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		    model: (Default is None) is your model that inherits from BaseRow.

		Returns:
			List of Pydantic BaseModel instances or empty list.

		Raises:
			QueryError: Raised when the query fails.
			TypeError: Raised when some parameter is invalid.
			ParameterInvalidProviderError: Raised when is sent a invalid parameter to the provider.
			ParameterInvalidValueError:	Raised when is sent a invalid value to the parameter.
			ParameterInvalidJsonValueError: Raised when is sent a invalid json value to the parameter.

		---

		Usage:

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
	async def query_as_dict(self, sql: str) -> Union[List[Dict[str, SupportedTypes]], List]: ...
	@overload
	async def query_as_dict(self, sql: str, parameters: DictParam) -> Union[List[Dict[str, SupportedTypes]], List]:
		"""
		Returns all rows from query result as `dict list` or `empty list`.

		You can use `:parameter_pattern` in the sql query to use parameters.

		---

		Args:

		    sql: sql query to be executed.

		    parameters: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		Returns:
			List of dict or empty list.

		Raises:
			QueryError: Raised when the query fails.
			TypeError: Raised when some parameter is invalid.
			ParameterInvalidProviderError: Raised when is sent a invalid parameter to the provider.
			ParameterInvalidValueError:	Raised when is sent a invalid value to the parameter.
			ParameterInvalidJsonValueError: Raised when is sent a invalid json value to the parameter.

		---

		Usage:

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
	async def query_first(self, sql: str, parameters: DictParam) -> Union[BaseRow, None]: ...
	@overload
	async def query_first(self, sql: str, model: Type[MyModel]) -> Union[Type[MyModel], None]: ...
	@overload
	async def query_first(self, sql: str, parameters: DictParam, model: Type[MyModel]) -> Union[Type[MyModel], None]:
		"""
		Returns first row from query result as `BaseRow`, `MyModel` or `None`.

		You can use `:parameter_pattern` in the sql query to use parameters.

		---

		Args:

		    sql: The sql query to be executed.

		    parameters: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		    model: (Default is None) is your model that inherits from BaseRow.

		Returns:
			A Pydantic BaseModel instance or None.

		Raises:
			QueryError: Raised when the query fails.
			TypeError: Raised when some parameter is invalid.
			ParameterInvalidProviderError: Raised when is sent a invalid parameter to the provider.
			ParameterInvalidValueError:	Raised when is sent a invalid value to the parameter.
			ParameterInvalidJsonValueError: Raised when is sent a invalid json value to the parameter.

		---

		Usage:

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
	async def query_first_as_dict(self, sql: str) -> Optional[Dict[str, SupportedTypes]]: ...
	@overload
	async def query_first_as_dict(self, sql: str, parameters: DictParam) -> Optional[Dict[str, SupportedTypes]]:
		"""
		Returns first row from query result as `dict` or `None`.

		---

		Args:

		    sql: The sql query to be executed.

		    parameters: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		Returns:
			A Pydantic BaseModel instance or None.

		Raises:
			QueryError: Raised when the query fails.
			TypeError: Raised when some parameter is invalid.
			ParameterInvalidProviderError: Raised when is sent a invalid parameter to the provider.
			ParameterInvalidValueError:	Raised when is sent a invalid value to the parameter.
			ParameterInvalidJsonValueError: Raised when is sent a invalid json value to the parameter.

		---

		Usage:

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
	async def execute(self, sql: str) -> int: ...
	@overload
	async def execute(self, sql: str, parameters: DictParam) -> int:
		"""
		Executes a query/sql and returns the number of rows affected.

		---

		Args:

		    sql: The sql query to be executed.

		    parameters: (Default is None) parameters must be a dictionary with the name of the parameter and the value.

		Returns:
			A int value with the number of rows affected.

		Raises:
			ExecuteError: Raised when the query fails.
			TypeError: Raised when some parameter is invalid.
			ParameterInvalidProviderError: Raised when is sent a invalid parameter to the provider.
			ParameterInvalidValueError:	Raised when is sent a invalid value to the parameter.
			ParameterInvalidJsonValueError: Raised when is sent a invalid json value to the parameter.

		---

		Usage:

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
	async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL) -> None:
		"""
		Sets the isolation level of the connection.

		The isolation level is set before the transaction is started.
		Is used to separate the transaction per level.

		The `Snapshot` isolation level is supported by MS SQL Server.

		The Sqlite does not support the isolation level.

		---

		Args:
			isolation_level: The isolation level must be a Level of isolation.

		Raises:
			IsolationLevelError: Raised when the isolation level is not supported by the database.
			ValueError: Raised when the isolation level is invalid.

		---

		Usage:

		```python
		    from pysqlx_engine import PySQLXEngine

		    uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
		    db = PySQLXEngine(uri=uri)
		    await db.connect()
		    await db.set_isolation_level(isolation_level="ReadUncommitted")
		```

		---

		Extra documentation:
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)

		"""
		...
	async def begin(self) -> None:
		"""
		Starts a transaction using `BEGIN`.

		`.begin()` is equivalent to `.start_transaction()` without setting the isolation level.

		---

		Raises:
			RawCmdError: Raised when the command fails.

		---

		Usage:

		```python
		from pysqlx_engine import PySQLXEngine

		uri = "postgresql://user:pass@host:port/db?schema=sample"
		db = PySQLXEngine(uri=uri)
		await db.connect()
		await db.begin()
		```
		"""
		...
	async def commit(self) -> None:
		"""
		Commits the current transaction.

		The `.begin()` method must be called before calling `.commit()`.

		If the database not need set the isolation level, maybe you can not use `.begin()` and `.commit()`.

		The PySQLXEngine by default uses the `.begin()` and `.commit()` in all transactions.

		---

		Raises:
			RawCmdError: Raised when the command fails.

		---

		Usage:

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
	async def rollback(self) -> None:
		"""
		Rollbacks the current transaction.

		Rollback is used to cancel the transaction, when you uses the rollback,
		the transaction is canceled and the changes are not saved.

		The `.begin()` method must be called before calling `.rollback()`.

		If the database not need set the isolation level, maybe you can not use `.begin()` and `.rollback()`.

		The PySQLXEngine by default try uses the `.begin()` and `.commit()` in all transactions.

		---

		Raises:
			RawCmdError: Raised when the command fails.

		---

		Usage:

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
	async def start_transaction(self, isolation_level: Union[ISOLATION_LEVEL, None] = None) -> None:
		"""
		Starts a transaction with `BEGIN/BEGIN TRANSACTION`. by default, does not set the isolation level.

		The `Snapshot` isolation level is supported by MS SQL Server.

		The Sqlite does not support the isolation level.

		---

		Args:
			isolation_level(str)`: (Default is None) The isolation level must be a Level of isolation.

		Raises:
			IsolationLevelError: Raised when the isolation level is not supported by the database.
			StartTransactionError: Raised when the transaction fails.
			ValueError: Raised when the isolation level is invalid.

		---

		Usage:

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

		Extra documentation:
		    * [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
		    * [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
		    * [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
		    * [SQLite](https://www.sqlite.org/isolation.html)
		"""
		...
