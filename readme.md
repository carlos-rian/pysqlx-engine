# PySQLXEngine

<p align="center">
  <a href="/"><img src="https://carlos-rian.github.io/pysqlx-engine/img/logo-text3.png" alt="PySQLXEngine Logo"></a>
</p>
<p align="center">
    <em>PySQLXEngine, a minimalist asynchronous SQL engine</em>
</p>

<p align="center">
<a href="/" target="_blank">
    <img src="https://github.com/tiangolo/fastapi/workflows/Test/badge.svg?event=push&branch=master" alt="Test">
</a>
<a href="/" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/tiangolo/fastapi?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/guvicorn-logger" target="_blank">
    <img src="https://img.shields.io/pypi/v/guvicorn-logger?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/guvicorn-logger" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/guvicorn-logger.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: <a href="https://carlos-rian.github.io/pysqlx-engine/" target="_blank">https://carlos-rian.github.io/pysqlx-engine/</a>

**Source Code**: <a href="https://github.com/carlos-rian/pysqlx-engine" target="_blank">https://github.com/carlos-rian/pysqlx-engine</a>

---

PySQLXEngine supports the option of sending **raw sql** to your database.

The PySQLXEngine is a minimalist **Async** SQL engine. Currently this lib only supports *asynchronous programming*, you need to code your code using `await` in all methods.

Database Support:

* `SQLite`
* `PostgreSQL`
* `MySQL`
* `Microsoft SQL Server`

OS Support:

* `Linux`
* `Windows` *Experimental! Unit tests were not run on Windows.*

## Installation


PIP

```console
$ pip install pysqlx-engine
```

Poetry

```console
$ poetry add pysqlx-engine
```


## Example


```python
import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def main():
    await db.connect()
    rows = await db.query(query="select 1 as number")
    print(rows)
    # output: [ BaseRow(number=1) ]

asyncio.run(main())
```