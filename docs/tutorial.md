# Tutorial - User Guide

PySQLXEngine exposes four methods, two that allow you to send raw queries and two to handle the connection.

!!! Note
    **All examples are async, but you can usePySQLXEngineSync if you don't want to use asyncio.**

## Methods
---

* [`.connect()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbconnect) create connection with db.

* [`.close()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbclose) disconnected from db.

* [`.is_healthy()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbis_healthy) check if the connection is healthy.

* [`.requires_isolation_first()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbrequires_isolation_first) this is used to determine if the connection should be isolated before executing a sql.

* [`.raw_cmd()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbraw_cmd) run a command in the database, for queries that can't be run using prepared statements.

* [`.query() and .query_first()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbquery) to return actual records (for example, using SELECT).

* [`.execute()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbexecute) to return a count of affected rows (for example, after an UPDATE or DELETE).

* [`.set_isolation_level()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbset_isolation_level) the isolation level is set before the transaction is started. Is used to separate the transaction per level.

* [`.begin()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbbegin) starts a transaction.

* [`.commit()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbcommit) commits a transaction.

* [`.rollback()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbrollback) rollbacks a transaction.

* [`.start_transaction()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbstart_transaction) starts a transaction with BEGIN. by default, does not set the isolation level. But is possible to set the isolation level using the parameter `isolation_level`.

## PySQLXEngine arguments

---

Providers/Drivers | Initial URI

* [`sqlite`](https://www.sqlite.org/index.html)
* [`postgresql`](https://www.postgresql.org/)
* [`mysql`](https://www.mysql.com/)
* [`sqlserver`](https://www.microsoft.com/sql-server)

URIs

* [sqlite](https://www.sqlite.org/index.html)

```Python 
uri = "sqlite:./dev.db"
```

* [postgresql](https://www.postgresql.org/)

```Python 
uri = "postgresql://user:pass@host:port/db?schema=sample"
```

* [mysql](https://www.mysql.com/)

```Python 
uri = "mysql://user:pass@host:port/db?schema=sample"
```

* [sqlserver](https://www.microsoft.com/sql-server)

```Python 
uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
```


## Simple Examples
---

### **`db.connect()`**

Create file [`main.py`](./python/connect.py)

<details markdown="1">
<summary>Complete code</summary>

```Python
{!./python/connect.py!}
```
</details>

* Create a file [main.py](./python/connect.py) with:

```Python
from pysqlx_engine  import PySQLXEngine

uri = "sqlite:./db.db"
db =PySQLXEngine(uri=uri)
```

After you create an instance ofPySQLXEngine; This instance is [`Lazy`](https://www.oreilly.com/library/view/python-cookbook/0596001673/ch08s12.html), after calling the [`db.connect()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbconnect) method, the connection to the database will be made.


* Modify the file main.py, add two lines:

!!! Note
    [`PySQLXEngine`](https://pypi.org/project/pysqlx-engine/) also supports [`async with` and `with`](https://docs.python.org/pt-br/3/whatsnew/3.5.html?highlight=async%20with#whatsnew-pep-492), where the connection is automatically opened and closed.

    ```Python hl_lines="6"
    from pysqlx_engine  import PySQLXEngine

    uri = "sqlite:./db.db"

    async def main():
        async withPySQLXEngine(uri=uri) as db:
            ...
    ```

**Code**

```Python hl_lines="6-7"
from pysqlx_engine  import PySQLXEngine

uri = "sqlite:./db.db"
db =PySQLXEngine(uri=uri)

async def main():
    await db.connect()

```


With [`PySQLXEngine`](https://pypi.org/project/pysqlx-engine/) built for [*asynchronous programming*](https://docs.python.org/3/library/asyncio.html), it is necessary to use the `async def` clause to `await` the coroutine termination.


* Modify the file [main.py](./python/connect.py), import the [`asyncio`](https://docs.python.org/3/library/asyncio.html) module to run the [coroutine](https://en.wikipedia.org/wiki/Coroutine):

```Python hl_lines="1 9 11 13"
import asyncio

from pysqlx_engine  import PySQLXEngine

uri = "sqlite:./db.db"
db =PySQLXEngine(uri=uri)

async def main():
    print("connecting...")
    await db.connect()
    print(f"it`s connected: {db.connected}")

asyncio.run(main())
```

* Run code using [Python3](https://www.python.org/)

!!! warning
    **On first run**, [`db.connect()`](./python/connect.py) *can be slow* because the binary that executes the raw queries will be downloaded.

<div class="termy">

```console
$ python3 main.py

connecting...
it`s connected: True
```
</div>


---

### **`db.execute()`**

<details markdown="1">
<summary>Complete code - Async</summary>

```Python
{!./python/aexecute.py!}
```
</details>

<details markdown="1">
<summary>Complete code - Sync</summary>

```Python
{!./python/execute.py!}
```
</details>

* Modify the file [main.py](./python/execute.py), add changes with highlighters to create a `user` table.

```Python hl_lines="7-19 28"
import asyncio
from pysqlx_engine  import PySQLXEngine

uri = "sqlite:./db.db"
db =PySQLXEngine(uri=uri)

async def create_table(db:PySQLXEngine):
    stmt = """CREATE TABLE IF NOT EXISTS user (
        id          INTEGER   PRIMARY KEY,
        first_name  TEXT      not null,
        last_name   TEXT      null,
        created_at  TEXT      not null,
        updated_at  TEXT      not null
    );
    """
    print("creating...")
    resp = await db.execute(stmt)
    # resp is zero because it has no rows affected
    print(f"created: {resp}")
    

async def main():
    print("connecting...")
    await db.connect()
    print(f"it`s connected: {db.connected}")

    # create table user
    await create_table(db)

asyncio.run(main())
```

* Modify the [main.py](./python/aexecute.py) file and add a function to insert a row into the user table.

```Python hl_lines="21-37 45"
{!./python/aexecute.py!}
```

* Run code using [Python3](https://www.python.org/)


<div class="termy">

```console
$ python3 main.py

connecting...
it`s connected: True
creating...
created: 0
inserting...
inserted: 1 affect
```
</div>


### **`db.query()`**

<details markdown="1">
<summary>Complete code</summary>

```Python
{!./python/query.py!}
```
</details>

* Modify the [main.py](./python/query.py) file, create select function and change main function.

`.query()` by default returns `None` or dynamically typed `BaseRow` list using [pydantic](https://pydantic-docs.helpmanual.io/), currently supported various types like [standard python types](https://docs.python.org/3/library/stdtypes.html), [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier), [JSON](https://www.json.org/json-en.html), [decimal](https://pydantic-docs.helpmanual.io/usage/types/), [DateTime](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types), etc.

<details markdown="1">
<summary>Help: Results</summary>

You might also want the result to come as a standard list of dict with python's scalar types.


=== "List of BaseRow"

    ```Python
    await db.query(sql=query)
    ```

=== "List of Dict"

    ```Python
    await db.query(sql=query, as_base_row=False)
    ```
</details>

```Python  hl_lines="8-11 14-16"
{!./python/query.py!}
```

* Run code using Python3

=== "List of BaseRow"

    <div class="termy">

    ```console
    $ python3 main.py

    [BaseRow(id=1, first_name='carlos', last_name='rian',created_at='2022-05-30 05:47:51', updated_at='2022-05-30 05:47:51')]
    ```
    </div>

=== "List of Dict"

    <div class="termy">

    ```console
    $ python3 main.py

    [{"id": 1, "first_name": "carlos", "last_name": "rian","created_at": "2022-05-30 05:47:51", "updated_at":"2022-05-30 05:47:51"}]
    ```
    </div>


### **`db.close()`**

<details markdown="1">
<summary>Complete code</summary>

```Python
{!./python/close.py!}
```
</details>

* Modify the main.py file, close connection.

!!! warning
    Skip this step if you are using `async with`, as the connection is automatically closed.

    ```Python hl_lines="6"
    from pysqlx_engine  import PySQLXEngine

    uri = "sqlite:./db.db"

    async def main():
        async withPySQLXEngine(uri=uri) as db:
            ...
    ```

```Python hl_lines="17"
{!./python/close.py!}
```