# **DML with return**

Although PySQLXEngine has a method for DML `execute` which returns the number of rows affected.

It is possible to use the `query*` methods to get an output/returning from the database.

`execute` always returns the number of rows affected. 
Maybe this is not useful, because if you make an `insert` and want the `id` as a return, the `execute` will limit you.

Although sql statements are atomic, one execution at a time, most modern databases bring sensational features like [**`RETUNING`**](https://www.postgresql.org/docs/current/dml-returning.html) or [**`OUTPUT`**](https://docs.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql) in the case of [*SQL Server*](https://www.microsoft.com/sql-server) that can return a value after the insert .

So since we need something to be returned, we can use the `query*` methods.

## **Examples**

In this examples we use the `user` table, which has the structure below. 
Change the types to your database types. In this [`SQLite`](https://www.sqlite.org/index.html) is used.

```sql
CREATE TABLE IF NOT EXISTS user (
    id          INTEGER PRIMARY KEY,
    first_name  TEXT,
    last_name   TEXT,
    created_at  TEXT,
    updated_at  TEXT
)
```

!!! warning
    In this example, [**MySQL**](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) is not mentioned because it does not have reliable support for this type of execution.

    You can use [`SELECT LAST_INSERT_ID();`](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) after **inserting the row**, but it is not guaranteed to be the correct ID, given that in a concurrent DB, many inserts at the same time, and the [`LAST_INSERT_ID()`](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) function takes only the last one. *If possible, start using [MariaDB](https://mariadb.org/); in addition to being more reliable, it is also an up-to-date open source.*

### **PostgreSQL, SQLite and MariaDB**

Create a ``main.py`` file and add the code examples below.

=== "**Async**"

    ``` py linenums="1" hl_lines="21 24"
    from pysqlx_engine import PySQLXEngine

    uri = "sqlite:./db.db"
    db = PySQLXEngine(uri=uri)

    async def main():
        await db.connect()

        sql = """sql
            INSERT INTO user (
                first_name, 
                last_name, 
                created_at, 
                updated_at) 
            VALUES (
                'bob', 
                'test', 
                '2022-05-30 05:47:51', 
                '2022-05-30 05:47:51'
            )
            RETURNING id;
        """

        row = await db.query(sql)
        print(row)

    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" hl_lines="21 24"
    from pysqlx_engine import PySQLXEngineSync

    uri = "sqlite:./db.db"
    db = PySQLXEngineSync(uri=uri)

    def main():
        db.connect()

        sql = """sql
            INSERT INTO user (
                first_name, 
                last_name, 
                created_at, 
                updated_at) 
            VALUES (
                'bob', 
                'test', 
                '2022-05-30 05:47:51', 
                '2022-05-30 05:47:51'
            )
            RETURNING id;
        """

        row = db.query(sql)
        print(row)

    # running the code
    main()
    ```


Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

[BaseRow(id=1)]
```
</div>

### **Microsoft SQL Server** 

Create a ``main.py`` file and add the code examples below.

=== "**Async**"

    ``` py linenums="1" hl_lines="18 27"
    from pysqlx_engine import PySQLXEngine

    uri = "sqlite:./db.db"
    db = PySQLXEngine(uri=uri)

    async def main():
        await db.connect()

        sql = """sql
            INSERT INTO user (
                first_name, 
                last_name, 
                created_at, 
                updated_at)
            OUTPUT Inserted.id
            VALUES (
                'bob', 
                'test', 
                '2022-05-30 05:47:51', 
                '2022-05-30 05:47:51'
            );
        """

        row = await db.query(sql)
        print(row)


    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" hl_lines="18 27"
    from pysqlx_engine import PySQLXEngineSync

    uri = "sqlite:./db.db"
    db = PySQLXEngineSync(uri=uri)

    def main():
        db.connect()

        sql = """sql
            INSERT INTO user (
                first_name, 
                last_name, 
                created_at, 
                updated_at)
            OUTPUT Inserted.id
            VALUES (
                'bob', 
                'test', 
                '2022-05-30 05:47:51', 
                '2022-05-30 05:47:51'
            );
        """

        row = db.query(sql)
        print(row)


    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

[BaseRow(id=1)]
```
</div>