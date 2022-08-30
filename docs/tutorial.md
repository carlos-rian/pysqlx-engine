# Tutorial - User Guide

PySQLXEngine exposes four methods, two that allow you to send raw queries and two to handle the connection.

!!! Note
    **All examples are async, but you can use SQLXEngineSync if you don't want to use asyncio.**

## Methods
---

* [`.connect()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbconnect) create connection with db
* [`.query()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbquery) to return actual records (for example, using SELECT)
* [`.execute()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbexecute) to return a count of affected rows (for example, after an UPDATE or DELETE)
* [`.close()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbclose) disconnected from db

## PySQLXEngine arguments

---

Providers

* [`sqlite`](https://www.sqlite.org/index.html)
* [`postgresql`](https://www.postgresql.org/)
* [`mysql`](https://www.mysql.com/)
* [`sqlserver`](https://www.microsoft.com/sql-server)

URIs

* [sqlite](https://www.sqlite.org/index.html)

```Python 
uri = "file:./dev.db"
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


## Examples
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
from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)
```

After you create an instance of SQLXEngine; This instance is [`Lazy`](https://www.oreilly.com/library/view/python-cookbook/0596001673/ch08s12.html), after calling the [`db.connect()`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbconnect) method, the connection to the database will be made.


* Modify the file main.py, add two lines:

!!! Note
    [`PySQLXEngine`](https://pypi.org/project/pysqlx-engine/) also supports [`async with` and `with`](https://docs.python.org/pt-br/3/whatsnew/3.5.html?highlight=async%20with#whatsnew-pep-492), where the connection is automatically opened and closed.

    ```Python hl_lines="6"
    from sqlx_engine import SQLXEngine

    uri = "file:./db.db"

    async def main():
        async with SQLXEngine(provider="sqlite", uri=uri) as db:
            ...
    ```

**Code**

```Python hl_lines="6-7"
from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def main():
    await db.connect()

```


With [`PySQLXEngine`](https://pypi.org/project/pysqlx-engine/) built for [*asynchronous programming*](https://docs.python.org/3/library/asyncio.html), it is necessary to use the `async def` clause to `await` the coroutine termination.


* Modify the file [main.py](./python/connect.py), import the [`asyncio`](https://docs.python.org/3/library/asyncio.html) module to run the [coroutine](https://en.wikipedia.org/wiki/Coroutine):

```Python hl_lines="2 10 12 14"
import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

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
from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def create_table(db: SQLXEngine):
    stmt = """CREATE TABLE user (
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

* Modify the [main.py](./python/execute.py) file and add a function to insert a row into the user table.

```Python hl_lines="21-37 45"
{!./python/execute.py!}
```

* Run code using [Python3](https://www.python.org/)

!!! warning
    Delete the `db.db` file created before.

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

`.query()` by default returns `None` or dynamically typed `BaseRow` list using [pydantic](https://pydantic-docs.helpmanual.io/), currently supported various types like `[standard python types](https://docs.python.org/3/library/stdtypes.html), [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier), [JSON](https://www.json.org/json-en.html), [decimal](https://pydantic-docs.helpmanual.io/usage/types/), [DateTime](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types), etc`.

<details markdown="1">
<summary>Help: Results</summary>

You might also want the result to come as a standard list of dict with python's scalar types.


=== "List of BaseRow"

    ```Python
    await db.query(query=query)
    ```

=== "List of Dict"

    ```Python
    await db.query(query=query, as_base_row=False)
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
    from sqlx_engine import SQLXEngine

    uri = "file:./db.db"

    async def main():
        async with SQLXEngine(provider="sqlite", uri=uri) as db:
            ...
    ```

```Python hl_lines="17"
{!./python/close.py!}
```