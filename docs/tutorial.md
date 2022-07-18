# Tutorial - User Guide

PySQLXEngine exposes four methods, two that allow you to send raw queries and two to handle the connection.

## Methods
---

* `.connect()` create connection with db
* `.query()` to return actual records (for example, using SELECT)
* `.execute()` to return a count of affected rows (for example, after an UPDATE or DELETE)
* `.close()` disconnected from db

## PySQLXEngine arguments

---

Providers

* `sqlite`
* `postgresql`
* `mysql`
* `sqlserver`

URIs

* sqlite

```Python 
uri = "file:./dev.db"
```

* postgresql

```Python 
uri = "postgresql://user:pass@host:port/db?schema=sample"
```

* mysql

```Python 
uri = "mysql://user:pass@host:port/db?schema=sample"
```

* sqlserver

```Python 
uri = "sqlserver://host:port;initial catalog=sample;user=sa;password=pass;"
```


## Examples
---

### **`db.connect()`**

Create file `main.py`

<details markdown="1">
<summary>Complete code</summary>

```Python
{!./python/connect.py!}
```
</details>

* Create a file main.py with:

```Python
from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)
```

After you create an instance of SQLXEngine; This instance is `Lazy`, after calling the `await db.connect()` method, the connection to the database will be made.


* Modify the file main.py, add two lines:

!!! Note
    `PySQLXEngine` also supports `async with`, where the connection is automatically opened and closed.

    ```Python hl_lines="6"
    from sqlx_engine import SQLXEngine

    uri = "file:./db.db"

    async def main():
        async with SQLXEngine(provider="sqlite", uri=uri) as db:
            ...
    ```



```Python hl_lines="6-7"
from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def main():
    await db.connect()

```

With PySQLXEngine built for asynchronous programming, it is necessary to use the `async def` clause to `await` the coroutine termination.


* Modify the file main.py, import the `asyncio` module to run the coroutine:

```Python hl_lines="1 9-11 13"
{!./python/connect.py!}

```

* Run code using Python3

!!! warning
    **On first run**, `db.connect()` *can be slow* because the binary that executes the raw queries will be downloaded.

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
<summary>Complete code</summary>

```Python
{!./python/execute.py!}
```
</details>

* Modify the file main.py, add changes with highlighters to create a `user` table.


```Python hl_lines="7-20 28"
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
    # resp is zero because not have rows affect.
    print(f"created: {resp}")
    

async def main():
    print("connecting...")
    await db.connect()
    print(f"it`s connected: {db.connected}")

    # create table user
    await create_table(db)

asyncio.run(main())
```

* Modify the main.py file and add a function to insert a row into the user table.

```Python hl_lines="21-37 45"
{!./python/execute.py!}
```

* Run code using Python3

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

* Modify the main.py file, create select function and change main function.

`.query()` by default returns `None` or dynamically typed `BaseRow` list using pydantic, currently supported various types like `standard python types, UUID, JSON, decimal, list, DateTime, etc`.

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