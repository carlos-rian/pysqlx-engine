# JSON Support


PySQLX-Engine has support for converting various types to JSON dumps. This dump is accepted into your database as a string.

Some databases have native support for JSON, but some don't. When you send a `parameter` of type `list` or `dict` to the database, 
PySQLX-Engine will convert it into a JSON dump and send it to the database as a string.

## **JSON Encoding Types**

| Python Types | JSON Types                                 | IN                                               | OUT                                   |
|--------------|--------------------------------------------|--------------------------------------------------|---------------------------------------|
| bytes        | String(Hex)                                | b'super bytes'                                   | "7375706572206279746573"              |
| uuid         | String                                     | UUID('ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6')     | "ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6"|
| time         | String                                     | datetime.time(12, 20, 50)                        | "12:20:50"                            |
| date         | String                                     | datetime.date(2023, 1, 15)                       | "2023-01-15"                          |
| datetime     | String                                     | datetime.datetime(2023, 1, 15, 16, 7, 1, 441234) | "2023-01-15 16:07:01.441234"          |
| Decimal      | String                                     | Decimal('1.23')                                  | '1.23'                                |
| None         | Null                                       | None                                             | null                                  |
| bool         | Bool                                       | True                                             | true                                  |
| str          | String                                     | 'value'                                          | "value"                               |
| int          | Int                                        | 123                                              | 123                                   |
| float        | Float                                      | 32.33                                            | 32.33                                 |
| *            | Try converting using standard `JSON Dumps` |                                                  |                                       |


## **Example**



=== "**Async**"

    ``` py linenums="1" title="main.py"
    import datetime
    from uuid import UUID
    from decimal import Decimal

    from pysqlx_engine import PySQLXEngine

    async def main():
        db = PySQLXEngine(uri="postgresql://user:pass@host:port/db")
        await db.connect()

        data = {
            "json":{
                "id": 1,
                "name": "John",
                "age": 20,
                "data": {
                    "a": 1,
                    "b": 2,
                    "c": 3,
                },
                "list": [1, 2, 3],
                "bytes": b"super bytes",
                "uuid": UUID('ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6'),
                "time": datetime.time(12, 20, 50),
                "date": datetime.date(2023, 1, 15),
                "datetime": datetime.datetime(2023, 1, 15, 16, 7, 1, 441234),
                "decimal": Decimal('1.23'),
                "none": None,
                "bool": True,
            }
        }

        resp = await db.query_first(sql="SELECT :json AS json_value", parameters=data)

        print(resp)
    
    import asyncio
    asyncio.run(main())

    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    import datetime
    from uuid import UUID
    from decimal import Decimal

    from pysqlx_engine import PySQLXEngineSync

    def main():
        db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db")
        db.connect()

        data = {
            "json":{
                "id": 1,
                "name": "John",
                "age": 20,
                "data": {
                    "a": 1,
                    "b": 2,
                    "c": 3,
                },
                "list": [1, 2, 3],
                "bytes": b"super bytes",
                "uuid": UUID('ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6'),
                "time": datetime.time(12, 20, 50),
                "date": datetime.date(2023, 1, 15),
                "datetime": datetime.datetime(2023, 1, 15, 16, 7, 1, 441234),
                "decimal": Decimal('1.23'),
                "none": None,
                "bool": True,
            }
        }

        resp = db.query_first(sql="SELECT :json AS json_value", parameters=data)

        print(resp)
    
    # running the code
    main()

    ```

---

### **Running the code**

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

```
</div>

Output

``` json title="python print"

BaseRow(json='{
    "id": 1, 
    "name": "John", 
    "age": 20, 
    "data": {
        "a": 1, 
        "b": 2, 
        "c": 3
    }, 
    "list": [1, 2, 3], 
    "bytes": "7375706572206279746573", 
    "uuid": "ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6", 
    "time": "12:20:50", 
    "date": "2023-01-15", 
    "datetime": "2023-01-15 16:07:01.441234", 
    "decimal": "1.23", 
    "none": null, 
    "bool": true
    }'
)
    
```