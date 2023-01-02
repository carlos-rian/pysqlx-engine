# PySQLXEngine - learning

The PySQLXEngine is a library that allows you to connect to a database and execute queries in a simple way.

So you can use it to create, read, update and delete data in your database.

Since the beginning PySQLXEngine was created and thinking to be a totally async engine. 
Although Python has supported asynchronous programming since version 3.6 using **`async/await`**.
We currently don't have good async libraries to handle **SQL Server** asynchronously, for example.

Despite being designed to be async, **PySQLXEngine** has sync support as well. The classes ``PySQLXEngine`` and ``PySQLXEngineSync`` are made available.

Both async and sync classes have precisely the same methods.


## Example of use async and sync

In a way, the code's only change would be the word `async/await`.

Asynchronous programming is a broad subject, but our tutorial is intended to be objective. So, in summary, 
when you need a performance in the sense of doing concurrency "*at the same time*", use async. 
You can use the sync form something need to do things that don't need concurrency.


=== "Async"
    ```python hl_lines="3 5 7-8"
    from pysqlx_engine import PySQLXEngine

    async def main(): # need to be async, because of await
        db = PySQLXEngine(uri="sqlite:./db.db")
        await db.connect() # need to await
    ```

=== "Sync"
    ```python hl_lines="3 5 7"
    from pysqlx_engine import PySQLXEngineSync

    def main(): # don't need to be async
        db = PySQLXEngineSync(uri="sqlite:./db.db")
        db.connect() # don't need to await
    ```