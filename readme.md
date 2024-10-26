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

PySQLXEngine supports the option of sending **raw sql** to your database.

The PySQLXEngine is a minimalist **Async and Sync** SQL engine. Currently this lib have supports *async and sync programming*.

The PySQLXEngine was created and thought to be minimalistic, but very efficient. The core is write in Rust, making communication between database and Python more efficient.


Database Support:

* `SQLite`
* `PostgreSQL`
* `MySQL`
* `Microsoft SQL Server`

OS Support:

* `Linux`
* `MacOS`
* `Windows`

## Installation

UV
    
```console
$ uv add pysqlx-engine
```


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