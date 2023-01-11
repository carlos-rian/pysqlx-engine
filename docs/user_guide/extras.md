# More documentation

The PySQLXEngine has more some methods to you can use the database more easily. See the documentation below:


* `.connect()` create connection with db.

* `.close()` disconnected from db.

* `.is_healthy()` check if the connection is healthy.

* `.requires_isolation_first()` this is used to determine if the connection should be isolated before executing a sql.

* `.raw_cmd()` run a command in the database, for queries that can't be run using prepared statements.

* `.query*()` to return actual records (for example, using SELECT).

* `.execute()` to return a count of affected rows (for example, after an INSERT, UPDATE or DELETE).

* `.set_isolation_level()` the isolation level is set before the transaction is started. Is used to separate the transaction per level.

* `.begin()` starts a transaction.

* `.commit()` commits a transaction.

* `.rollback()` rollbacks a transaction.

* `.start_transaction()` starts a transaction with BEGIN/BEGIN TRANSACTION. By default, does not set the isolation level. But is possible to set the isolation level using the parameter `isolation_level`.

---

## **Parameters Helper**

The PySQLXEngine has five methods that accept the parameters with sql.

Parameters are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

#### SQL with parameters syntax

* SQL

```sql
SELECT * FROM table WHERE id = :id
```

* Parameters

```python
{"id": 1}
```

#### Parameters

* dict ``key`` must be a valid string.
* dict ``value`` can be one of the types:
    * ``bool``
    * ``bytes``
    * ``date``
    * ``datetime``
    * ``Decimal``
    * ``dict``
    * ``float``
    * ``int``
    * ``list``
    * ``str``
    * ``time``
    * ``tuple``
    * ``UUID``
    * ``None``

#### Python types vs SQL types

| Python   | Databases                                                              |
|----------|------------------------------------------------------------------------|
| bool     | bool/bit/boolean/tinyint/etc.                                          |
| bytes    | bytea/binary/varbinary/blob/etc.                                       |
| date     | date/nvarchar/varchar/string/etc.                                      |
| datetime | timestamp/timestamptz/datetime/datetime2/nvarchar/varchar/string/etc.  |
| Decimal  | decimal/numeric/etc.                                                   |
| dict     | json/jsonb/nvarchar/varchar/string/etc.                                |
| float    | float/real/numeric/etc.                                                |
| int      | int/integer/smallint/bigint/tinyint/etc.                               |
| list     | json/jsonb/nvarchar/varchar/string/etc.                                |
| str      | varchar/text/nvarchar/char/etc.                                        |
| time     | time/nvarchar/varchar/string/etc.                                      |
| tuple    | array(Postgres Native), error for other databases.                     |
| UUID     | uuid/varchar/text/nvarchar/etc.                                        |
| None     | null.                                                                  |


---

## **Methods**

## *connect*
#### Description

Each connection instance is lazy; only after ``.connect()`` is the database checked and the connection established.


When you use `with/async with`  the connection is automatically opened and closed.

!!! Note
    [`PySQLXEngine`](https://pypi.org/project/pysqlx-engine/) also supports [`with/async with`](https://docs.python.org/pt-br/3/whatsnew/3.5.html?highlight=async%20with#whatsnew-pep-492), where the connection is automatically opened and closed.

    === "**Async**"

        ```python hl_lines="6"
        from pysqlx_engine  import PySQLXEngine

        uri = "sqlite:./db.db"

        async def main():
            async with PySQLXEngine(uri=uri) as db:
                ...
        ```

    === "**Sync**"

        ```python hl_lines="6"
        from pysqlx_engine  import PySQLXEngineSync

        uri = "sqlite:./db.db"

        def main():
            with PySQLXEngineSync(uri=uri) as db:
                ...
        ```

#### Helper
* Arguments: ``None``

* Returns: ``None``

* Raises: ``ConnectError``

#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine
    uri = "sqlite:./db.db"
    db = PySQLXEngine(uri=uri)
    await db.connect()
    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync
    uri = "sqlite:./db.db"
    db = PySQLXEngineSync(uri=uri)
    db.connect()
    ```
---

## *close*

#### Description
It's a good idea to close the connection, but PySQLXEngine has the core in Rust;
closing is automatic when your code leaves the context.

Even if you don't close the connection, don't worry; when the process ends automatically,
the connections will be closed, so the database doesn't have an idle connection.

#### Helper
* Arguments: ``None``

* Returns: ``None``

* Raises: ``None``

#### Example

=== "**Async**"

    ```python
    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()
    await db.close()
    ```

=== "**Sync**"

    ```python
    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()
    db.close()
    ```
---

## *is_healthy*

#### Description
Check if the connection is healthy.

Returns `false`, if connection is considered to not be in a working state.

#### Helper

* Arguments: ``None``

* Returns: ``bool``

* Raises: ``None``

---

## *requires_isolation_first*

#### Description
Returns `True` if the connection requires isolation first, `False` otherwise.

This is used to determine if the connection should be isolated before executing a query.

For example, SQL Server requires isolation before executing a statement using begin in some cases.

Signals if the `isolation level` SET needs to happen before or after the `BEGIN`.


#### Helper
* Arguments: ``None``

* Returns: ``bool``

* Raises: ``None``


#### Extra documentation:
* [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
* [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
* [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
* [SQLite](https://www.sqlite.org/isolation.html)

---

## *raw_cmd*

#### Description
Run a command in the database, for queries that can't be run using prepared statements(queries/execute/etc).

#### Helper

* Arguments: 
    - ``sql(str)``: sql to be executed.

* Returns: ``None``

* Raises: ``RawCmdError``


#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()

    await db.raw_cmd(sql="SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    db.raw_cmd(sql="SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")
    ```

---

## *query*


#### Description
Returns all rows from query result as ``BaseRow list``, ``MyModel list`` or ``empty list``.


#### Helper
* Arguments:

    - ``sql(str)``: sql query to be executed.

    - ``parameters(dict)``: (default is None) dictionary with the name of the parameter and the value.

    - ``model(BaseRow)``: (default is None) is your model that inherits from BaseRow.

* Returns:

    - ``List[BaseRow]``: default if you don't pass a model.

    - ``List[MyModel]``: If you pass a model.

    - ``List``: If don't have rows.

* Raises: 

    - ``QueryError``
    - ``TypeError`` 
    - ``ParameterInvalidProviderError``
    - ``ParameterInvalidValueError``
    - ``ParameterInvalidJsonValueError``



=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()

    result1 = await db.query(sql="SELECT 1 as id, 'rian' as name")
    print(result1)
    # output: [BaseRow(id=1, name='rian')]

    result2 = await db.query(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result2)
    # output: [BaseRow(id=1, name='rian')]

    await db.close()

    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    result1 = db.query(sql="SELECT 1 as id, 'rian' as name")
    print(result1)
    # output: [BaseRow(id=1, name='rian')]

    result2 = db.query(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result2)
    # output: [BaseRow(id=1, name='rian')]

    db.close()

    ```

---

## *query_first*

#### Description
Returns first row from query result as ``BaseRow``, ``MyModel`` or ``None``.


#### Helper
* Arguments:

    - ``sql(str)``: sql query to be executed.

    - ``parameters(dict)``: (default is None) parameters must be a dictionary with the name of the parameter and the value.

    - ``model(BaseRow)``: (default is None) is your model that inherits from BaseRow.

* Returns:

    - ``BaseRow``: default if you don't pass a model.
    - ``MyModel``: If you pass a model.
    - ``None``: if no rows are found.

* Raises: 
    - ``QueryError``
    - ``TypeError``
    - ``ParameterInvalidProviderError``
    - ``ParameterInvalidValueError``
    - ``ParameterInvalidJsonValueError``

#### Example

=== "**Async**"

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

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    result = db.query_first("SELECT 1 as id, 'rian' as name")
    print(result)
    # output -> BaseRow(id=1, name='rian')

    result = db.query_first(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result)
    # output -> BaseRow(id=1, name='rian')

    db.close()
    ```

---

## *query_as_dict*

#### Description
Returns all rows from query result as ``dict list`` or ``empty list``.


#### Helper
* Arguments:

    - ``sql(str)``: sql query to be executed.

    - ``parameters(dict)``: (default is None) dictionary with the name of the parameter and the value.

* Returns:

    - ``List[Dict[str, Any]]``: dict list.

    - ``List``: empty list.

* Raises: 
    - ``QueryError``
    - ``TypeError``
    - ``ParameterInvalidProviderError``
    - ``ParameterInvalidValueError``
    - ``ParameterInvalidJsonValueError``


#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()

    result1 = await db.query_as_dict(sql="SELECT 1 as id, 'rian' as name")
    print(result1)
    # output -> [{'id': 1, 'name': 'rian'}]

    result2 = await db.query_as_dict(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result2)
    # output -> [{'id': 1, 'name': 'rian'}]

    await db.close()
    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    result1 = db.query_as_dict(sql="SELECT 1 as id, 'rian' as name")
    print(result1)
    # output -> [{'id': 1, 'name': 'rian'}]

    result2 = db.query_as_dict(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result2)
    # output -> [{'id': 1, 'name': 'rian'}]

    db.close()
    ```

---

## *query_first_as_dict*

#### Description
Returns first row from query result as ``dict`` or ``None``.


#### Helper
* Arguments:

    - ``sql(str)``: sql query to be executed.

    - ``parameters(dict)``: (default is None) parameters must be a dictionary with the name of the parameter and the value.

* Returns:

    - ``Dict[str, Any]``: row as dict.

    - ``None``: if no rows are found.

* Raises: 

    - ``QueryError``
    - ``TypeError`` 
    - ``ParameterInvalidProviderError``
    - ``ParameterInvalidValueError``
    - ``ParameterInvalidJsonValueError``


#### Example

=== "**Async**"

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

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    result = db.query_first_as_dict(sql="SELECT 1 as id, 'rian' as name")
    print(result)
    # output -> {'id': 1, 'name': 'rian'}

    result = db.query_first_as_dict(sql="SELECT 1 as :id, 'rian' as name", parameters={"id": 1})
    print(result)
    # output -> {'id': 1, 'name': 'rian'}

    db.close()
    ```

---

## *execute*

#### Description
Executes a query/sql and returns the number of rows affected.


#### Helper

* Arguments:

    - ``sql(str)``:  sql to be executed.

    - ``parameters(dict)``: (Default is None) dictionary with the name of the parameter and the value.

* Returns: 
    - ``int``: number of rows affected.

* Raises: 
    - ``ExecuteError``
    - ``TypeError``
    - ``ParameterInvalidProviderError``
    - ``ParameterInvalidValueError``
    - ``ParameterInvalidJsonValueError``


#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine
    
    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()

    result = await db.execute("INSERT INTO users (name) VALUES ('rian')")
    print(f"rows_affected = {result}")
    # output -> rows_affected = 1
    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync
    
    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    result db.execute("INSERT INTO users (name) VALUES ('rian')")
    print(f"rows_affected = {result}")
    # output -> rows_affected = 1
    ```

---

## *set_isolation_level*

#### Description
Sets the isolation level of the connection.

The isolation level is set before the transaction is started.
Is used to separate the transaction per level.

The `Snapshot` isolation level is supported by MS SQL Server.

The Sqlite does not support the isolation level.


#### Helper

* Arguments: 
    - ``isolation_level(str)``: isolation level to be set (
        ``ReadUncommitted``,
        ``ReadCommitted``,
        ``RepeatableRead``,
        ``Snapshot``,
        ``Serializable``
        )

* Returns: ``None``

* Raises: 
    - ``IsolationLevelError``
    - ``ValueError``


#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()
    await db.set_isolation_level(isolation_level="ReadUncommitted")
    ```

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()
    db.set_isolation_level(isolation_level="ReadUncommitted")
    ```

#### Isolation Level Help
* [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
* [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
* [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
* [SQLite](https://www.sqlite.org/isolation.html)


---

## *begin*

#### Description
Starts a transaction using ``BEGIN``. ``begin()`` is equivalent to `start_transaction()` without setting the isolation level.


#### Helper

* Arguments: ``None``

* Returns: ``None``

* Raises: ``RawCmdError``



#### Example

=== "**Async**"

    ```python
    from pysqlx_engine import PySQLXEngine

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngine(uri=uri)
    await db.connect()
    await db.begin()
    ```
=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()
    db.begin()
    ```

---

## *commit*

#### Description
Commits the current transaction.

The `begin()` method must be called before calling `commit()`.

If the database not need set the isolation level, maybe you can not use `begin()` and `commit()`.

The PySQLXEngine by default uses the `begin()` and `commit()` in all transactions.


#### Helper

    * Arguments: ``None`

    * Returns: ``None``

    * Raises: ``RawCmdError``


#### Example

=== "**Async**"

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

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    db.begin()
    db.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
    db.execute("INSERT INTO users (name) VALUES ('rian')")
    db.commit()
    ```

---

## *rollback*

#### Description
Rollbacks the current transaction.

Rollback is used to cancel the transaction, when you uses the rollback,
the transaction is canceled and the changes are not saved.

The ``begin()`` method must be called before calling ``rollback()``.

If the database not need set the isolation level, maybe you can not use ``begin()`` and ``rollback()``.

The PySQLXEngine by default try uses the ``begin()`` and ``commit()`` in all transactions.


#### Helper

* Arguments: ``None``

* Returns: ``None``

* Raises: ``RawCmdError``


#### Example

=== "**Async**"

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

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    db.begin()
    db.execute("CREATE TABLE users (id serial PRIMARY KEY, name varchar(255))")
    db.execute("INSERT INTO users (name) VALUES ('rian')")
    db.rollback()
    ```

---

## *start_transaction*

#### Description
Starts a transaction with ``BEGIN/BEGIN TRANSACTION``. by default, does not set the isolation level.

The ``Snapshot`` isolation level is supported by MS SQL Server.

The Sqlite does not support the isolation level.

---

#### Helper

* Arguments: 

    - ``isolation_level(str)``: by default is None. Isolation level to be set (
    ``ReadUncommitted``,
    ``ReadCommitted``,
    ``RepeatableRead``,
    ``Snapshot``,
    ``Serializable``
    )

* Returns: `None`

* Raises: 
    - ``IsolationLevelError``
    - ``StartTransactionError``
    - ``ValueError``

---

#### Example

=== "**Async**"

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

=== "**Sync**"

    ```python
    from pysqlx_engine import PySQLXEngineSync

    uri = "postgresql://user:pass@host:port/db?schema=sample"
    db = PySQLXEngineSync(uri=uri)
    db.connect()

    # with isolation level
    db.start_transaction(isolation_level="ReadCommitted")

    # without isolation level
    db.start_transaction()
    ```

---

#### Isolation Level Help

* [MSSQL](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transaction-isolation-levels)
* [Postgres](https://www.postgresql.org/docs/current/sql-set-transaction.html)
* [MySQL](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)
* [SQLite](https://www.sqlite.org/isolation.html)