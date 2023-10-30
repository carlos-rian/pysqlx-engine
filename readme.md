# PySQLXEngine

<p align="center">
  <a href="/"><img src="https://carlos-rian.github.io/pysqlx-engine/img/logo-text3.png" alt="PySQLXEngine Logo"></a>
</p>
<p align="center">
    <em>PySQLXEngine, a fast and minimalist SQL engine</em>
</p>

<p align="center">
<a href="https://github.com/carlos-rian/pysqlx-engine/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/carlos-rian/pysqlx-engine/actions/workflows/ci.yml/badge.svg" alt="CI">
</a>
<a href="https://app.codecov.io/gh/carlos-rian/pysqlx-engine" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/carlos-rian/pysqlx-engine?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/pysqlx-engine" target="_blank">
    <img src="https://img.shields.io/pypi/v/pysqlx-engine?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/pysqlx-engine" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/pysqlx-engine.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://pepy.tech/project/pysqlx-engine" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/pysqlx-engine?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads" alt="Downloads">
</a>
</p>

---

**Documentation**: <a href="https://carlos-rian.github.io/pysqlx-engine/" target="_blank">https://carlos-rian.github.io/pysqlx-engine/</a>

**Source Code**: <a href="https://github.com/carlos-rian/pysqlx-engine" target="_blank">https://github.com/carlos-rian/pysqlx-engine</a>

---

PySQLXEngine supports the option of sending **Raw SQL** to your database.

The PySQLXEngine is a minimalist [SQL Engine](https://github.com/carlos-rian/pysqlx-engine).

The PySQLXEngine was created and thought to be minimalistic, but very efficient. The core is write in [**Rust**](https://www.rust-lang.org), making communication between Databases and [**Python**](https://python-poetry.org) more efficient.

All SQL executed using PySQLXEngine is atomic; only one instruction is executed at a time. Only the first one will be completed if you send an Insert and a select. This is one of the ways to handle SQL ingestion. As of version **0.2.0**, PySQLXEngine supports transactions, where you can control [`BEGIN`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver16), [`COMMIT`](https://www.geeksforgeeks.org/difference-between-commit-and-rollback-in-sql), [ `ROLLBACK` ](https://www.geeksforgeeks.org/difference-between-commit-and-rollback-in-sql), [`ISOLATION LEVEL`](https://levelup.gitconnected.com/understanding-isolation-levels-in-a-database-transaction-af78aea3f44), etc. as you wish.


> **NOTE**:
    Minimalism is not the lack of something, but having exactly what you need.
    PySQLXEngine aims to expose an easy interface for you to communicate with the database in a simple, intuitive way and with good help through documentation, autocompletion, typing, and good practices.
---

Database Support:

* [`SQLite`](https://www.sqlite.org/index.html)
* [`PostgreSQL`](https://www.postgresql.org/)
* [`MySQL`](https://www.mysql.com/)
* [`Microsoft SQL Server`](https://www.microsoft.com/sql-server)

OS Support:

* [`Linux`](https://pt.wikipedia.org/wiki/Linux)
* [`MacOS`](https://pt.wikipedia.org/wiki/Macos)
* [`Windows`](https://pt.wikipedia.org/wiki/Microsoft_Windows)


## Installation


PIP

```console
$ pip install pysqlx-engine
```

Poetry

```console
$ poetry add pysqlx-engine
```

## Async Example

Create a `main.py` file and add the code examples below.

```python
from pysqlx_engine import PySQLXEngine

async def main():
    db = PySQLXEngine(uri="sqlite:./db.db")
    await db.connect()

    await db.execute(sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            age INT
        )
    """)
    await db.execute(sql="INSERT INTO users (name, age) VALUES ('Rian', '28')")
    await db.execute(sql="INSERT INTO users (name, age) VALUES ('Carlos', '29')")

    rows = await db.query(sql="SELECT * FROM users")

    print(rows)

import asyncio
asyncio.run(main())
```

## Sync Example

Create a `main.py` file and add the code examples below.

```python
from pysqlx_engine import PySQLXEngineSync

def main():
    db = PySQLXEngineSync(uri="sqlite:./db.db")
    db.connect()

    db.execute(sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            age INT
        )
    """)
    db.execute(sql="INSERT INTO users (name, age) VALUES ('Rian', '28')")
    db.execute(sql="INSERT INTO users (name, age) VALUES ('Carlos', '29')")

    rows = db.query(sql="SELECT * FROM users")

    print(rows)

# running the code
main()
```

Running the code using the terminal


```console
$ python3 main.py
```
Output

```python
[
    BaseRow(id=1, name='Rian', age=28),  
    BaseRow(id=2, name='Carlos', age=29)
]
```
