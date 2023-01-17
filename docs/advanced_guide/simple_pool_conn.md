# **Simple pool with concurrent connections**

The PySQLXEngine allows you to create a pool of connections to the database. 
This is useful when you need to make many queries at the same time. 
The PySQLXEngine not limit the number of connections, but it is recommended you set a limit.

This example will use the `PostgreSQL` database and `PySQLXEngine` class. 

Create a `main.py` file and add the code examples below.


## **Example**

``` py

import asyncio

from pysqlx_engine import PySQLXEngine, PySQLXEnginePool

uri = "postgresql://user:password@localhost:5432/db"

async def create_table():
    db = PySQLXEngine(uri=uri)
    await db.connect()
    sql = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, x_position FLOAT, y_position FLOAT)"
    await db.execute(sql=sql)
    await db.close()


async def main():
    # create users table
    await create_table()

    # create a pool of 10 connections
    pool = PySQLXEnginePool(uri=uri, max_connections=3)

    # create database connections
    db1 = await pool.new_connection() 
    db2 = await pool.new_connection() 
    db3 = await pool.new_connection() 

    sql = "INSERT INTO users(x_position, y_position) VALUES (:x, :y)"
    # these calls are lazy, not blocking.
    calls = [
        db1.execute(sql=sql, parameters={"x": 1.2, "y": 2.3}),
        db2.execute(sql=sql, parameters={"x": 4.3, "y": 5.6}),
        db3.execute(sql=sql, parameters={"x": 6.5, "y": 1.8}),

    ]
    
    # run the calls concurrently
    inserts = await asyncio.gather(*calls)
    print("inserts:", inserts, "affects rows")

    # query all users
    sql = "SELECT * FROM users"
    resp = await db1.query(sql=sql)

    print("rows:", resp)

    # close the connections
    await db1.close()
    await db2.close()
    await db3.close()

import asyncio
asyncio.run(main())

```

Running the code using the terminal

<div class="termy">

```console

$ python3 main.py

inserts: [1, 1, 1] affects rows 
rows: [
    BaseModel(id=1, x_position=1.2, y_position=2.3), 
    BaseModel(id=2, x_position=4.3, y_position=5.6), 
    BaseModel(id=3, x_position=6.5, y_position=1.8)
]

```

</div>