# Next steps

This section provides some next steps for you to continue learning about PySQLXEngine.

PySQLXEngine has some methods; among them, the ``query`` and ``execute`` methods are handy.

---

The methods ``.query*`` is used to execute a query that returns data, and ``.execute`` is used to execute a query that does not return data but only the number of rows affected.

Both methods have the same parameters:

* ``sql``: The SQL query to be executed.
* ``parameters``: The parameters to be passed to the query. This parameter is optional.
!!! Note
    **SQL** can be a str with or without named parameters. The PySQLXEngine builds the parameters into the SQL before sending it to the database.
    This is possible only when the types are accepted by the PySQLXEngine. If the type is not accepted, the PySQLXEngine will raise an exception.


!!! Note
    **Parameters** are built into SQL at the application level; that is, *the SQL and separate parameters are not sent to the database*;
    although most databases support this type of operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
    This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

---

## **Example of use**

To this example, we will use the ``sqlite`` database. Create a ``main.py`` file and add the code examples below.

### **Create a table**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                age INTEGER
            );
        """

        resp = await db.execute(sql=sql)

        print("table created: ", resp == 0)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                age INTEGER
            );
        """

        resp = db.execute(sql=sql)

        print("table created: ", resp == 0)
    
    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

table created: True

```
</div>

---

### **Insert data**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "INSERT INTO users (name, age) VALUES (:name, :age)"
        params = {"name": "John", "age": 20}
        resp = await db.execute(sql=sql, parameters=params)
    
        print("rows affected: ", resp)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "INSERT INTO users (name, age) VALUES (:name, :age)"
        params = {"name": "John", "age": 20}
        resp = db.execute(sql=sql, parameters=params)
    
        print("rows affected: ", resp)
    
    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

rows affected: 1

```
</div>

---

### **Select data**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "SELECT * FROM users"
        resp = await db.query(sql=sql)
    
        print("rows selected: ", resp)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "SELECT * FROM users"
        resp = db.query(sql=sql)
    
        print("rows selected: ", resp)
    
    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

rows selected: [BaseRow(id=1, name='John', age=20)]

```

</div>


---

### **Update data**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "UPDATE users SET age = :age WHERE id = :id"
        params = {"age": 21, "id": 1}
        resp = await db.execute(sql=sql, parameters=params)

        print("rows affected: ", resp)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "UPDATE users SET age = :age WHERE id = :id"
        params = {"age": 21, "id": 1}
        resp = db.execute(sql=sql, parameters=params)

        print("rows affected: ", resp)
    
    # running the code
    main()
    ```


Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

rows affected: 1

```

</div>

---

### **Delete data**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "DELETE FROM users WHERE id = :id"
        params = {"id": 1}
        resp = await db.execute(sql=sql, parameters=params)

        print("rows affected: ", resp)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "DELETE FROM users WHERE id = :id"
        params = {"id": 1}
        resp = db.execute(sql=sql, parameters=params)

        print("rows affected: ", resp)
    
    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console

$ python3 main.py

rows affected: 1

```

</div>


---

### **Drop table**

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "DROP TABLE users"
        resp = await db.execute(sql=sql)

        print("table dropped: ", resp == 0)
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync
    
    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "DROP TABLE users"
        resp = db.execute(sql=sql)

        print("table dropped: ", resp == 0)

    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

table dropped: True

```

</div>