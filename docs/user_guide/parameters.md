# Parameters

The PySQLX-Engine supports the parameters. The parameters are passed as a dictionary to the functions below.

* `query`
* `query_first`
* `query_as_dict`
* `query_first_as_dict`
* `execute`

These functions are described in the [Documentation for methods](/pysqlx-engine/user_guide/extras/) section.

**Parameters** are built into SQL at the application level; that is, the SQL and separate parameters are not sent to the database;
although most databases support this operation, the PySQLXEngine does it before calling the database to avoid possible incompatibilities.
This allows you to show the precompiled queries and send only raw SQL while maintaining minimal consistency across types.

The PySQLXEngine supports many Python types with automatic conversion to SQL.


## **Parameters types**

**Key**: dict `key` must be a valid string.

**Value**: dict `value` can be one of the types bellow:

   - `bool`
   - `bytes`
   - `date`
   - `datetime`
   - `Decimal`
   - `dict`
   - `float`
   - `int`
   - `list`
   - `str`
   - `time`
   - `tuple`
   - `UUID`
   - `enum.Enum`
   - `None`

These types are converted to the corresponding SQL type. This applies to parameters chained in a list or dict that are [converted to json](/pysqlx-engine/advanced_guide/json_support/).

## **Example**

For this example, the table `users` will be used. The table `users` has the following structure:

``` sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER, 
    name TEXT, 
    age INTEGER,
    active BOOLEAN
);
```

Create a `main.py` file and add the code examples below.

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        db = PySQLXEngine(uri="sqlite:./db.db")
        await db.connect()

        param = {
            "i": 1,
            "n": "John",
            "ag": 20,
            "ac": True
        }
        sql = """
            INSERT INTO users (id, name, age, active) 
            VALUES (:i, :n, :ag, :ac);
        """
        
        resp = await db.execute(sql=sql, parameters=param)

        print("inserted: ", resp == 1)

    import asyncio
    asyncio.run(main())    
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync

    def main():
        db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db")
        db.connect()

        param = {
            "i": 1,
            "n": "John",
            "ag": 20,
            "ac": True
        }
        sql = """
            INSERT INTO users (id, name, age, active) 
            VALUES (:i, :n, :ag, :ac);
        """

        resp = db.execute(sql=sql, parameters=param)

        print("inserted: ", resp == 1)

    # runnig the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

inserted: True

```

</div>