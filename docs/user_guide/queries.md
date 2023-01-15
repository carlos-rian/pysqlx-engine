# Queries

The PySQLXEngine has four methods to execute queries:

* ``.query()``: Returns *all rows* of the query. The results are returned as a *list of BaseRow*.
* ``.query_first()``: Returns the *first row* of the query. The result is returned as a *BaseRow*.
* ``.query_as_dict()``: Returns *all rows* of the query. The results are returned as a *list of dict*.
* ``.query_first_as_dict()``: Returns the *first row* of the query. The result is returned as a *dict*.


You can use the same methods for both `sync` and `async`. All the methods accept the ``sql`` and ``parameters`` arguments.

Create a ``main.py`` file and add the code examples below.

## **Query result as dict**

The ``.query_as_dict()`` and ``.query_first_as_dict()`` methods are useful when you want to get the results as a *`list of dict`* or a *`dict`*.

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = await db.query_as_dict(sql=sql)
        resp2 = await db.query_first_as_dict(sql=sql)

        print("returned:", resp1, "as a list of dicts")
        print("returned:", resp2, "as a dict")

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

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = db.query_as_dict(sql=sql)
        resp2 = db.query_first_as_dict(sql=sql)

        print("returned:", resp1, "as a list of dicts")
        print("returned:", resp2, "as a dict")
    
    # running the code
    main()

    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

returned: [{'id': 1, 'name': 'Rian'}] as a list of dict 
returned: {'id': 1, 'name': 'Rian'} as a dict

```

</div>


## **Query result as BaseRow**

The ``.query()`` and ``.query_first()`` methods are useful when you want to get the results as a *`list of BaseRow`* or a *`BaseRow`*.

BaseRow is a class that represents a row of the query result. It has the same attributes as the columns of the query result. 
The BaseRow is an inheritance from ``Pydantic BaseModel``.

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = await db.query(sql=sql)
        resp2 = await db.query_first(sql=sql)

        print("returned:", resp1, "as a list of BaseRow")
        print("returned:", resp2, "as a BaseRow")
    
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

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = db.query(sql=sql)
        resp2 = db.query_first(sql=sql)

        print("returned:", resp1, "as a list of BaseRow")
        print("returned:", resp2, "as a BaseRow")
    
    # running the code
    main()
    ```

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

returned: [BaseRow(id=1, name='Rian')] as a list of BaseRow
returned: BaseRow(id=1, name='Rian') as a BaseRow

```

</div>


## **Query result as MyModel**

The ``.query()`` and ``.query_first()`` methods are useful when you want to get the results as a *`list of MyModel`* or a *`MyModel`*.

The PySQLXEngine has a feature to convert the query result to a custom model. You can use the ``model`` argument to specify the model.

Using the ``model`` argument, you can have an autocomplete feature in your IDE, this brings more security and makes development easier.

!!! None
    The ``model`` argument is only available for the ``.query()`` and ``.query_first()`` methods.
    The ``model`` needs to inherit from ``BaseRow``, you can use **``from pysqlx_engine import BaseRow``** to import the ``BaseRow`` class.

---

Create a ``models.py`` file and add the code examples below.

``` py linenums="1" title="models.py"
from pysqlx_engine import BaseRow

class User(BaseRow):
    id: int
    name: str
```


Create a ``main.py`` file and add the code examples below.

=== "**Async**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngine
    from models import User

    async def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngine(uri=uri)
        await db.connect()

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = await db.query(sql=sql, model=User)
        resp2 = await db.query_first(sql=sql, model=User)

        print("returned:", resp1, "as a list of User")
        print("returned:", resp2, "as a User")
    
    import asyncio
    asyncio.run(main())
    ```

=== "**Sync**"

    ``` py linenums="1" title="main.py"
    from pysqlx_engine import PySQLXEngineSync
    from models import User

    def main():
        uri = "sqlite:./db.db"
        db = PySQLXEngineSync(uri=uri)
        db.connect()

        sql = "SELECT 1 AS id, 'Rian' AS name"
        
        resp1 = db.query(sql=sql, model=User)
        resp2 = db.query_first(sql=sql, model=User)

        print("returned:", resp1, "as a list of User")
        print("returned:", resp2, "as a User")
    
    # running the code
    main()
    ```

You can see the autocomple.

*Visual Studio Code*

<img src="../img/autocomplete_your_model_vscode.png" alt="VScode screen, show the autocomplete.">

*PyCharm*

<img src="../img/autocomplete_your_model_pycharm.png" alt="PyCharm screen, show the autocomplete.">


Running the code using the terminal

<div class="termy">

```console
$ python3 main.py

returned: [User(id=1, name='Rian')] as a list of User
returned: User(id=1, name='Rian') as a User

```

</div>
