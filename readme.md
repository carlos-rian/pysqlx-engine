# PySQLXEngine

<p align="center">
  <a href="/"><img src="https://carlos-rian.github.io/pysqlx-engine/img/logo-text3.png" alt="PySQLXEngine Logo"></a>
</p>
<p align="center">
    <em>PySQLXEngine, a minimalist asynchronous SQL engine</em>
</p>

<p align="center">
<a href="https://github.com/carlos-rian/pysqlx-engine/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/carlos-rian/pysqlx-engine/workflows/Test/badge.svg?event=push&branch=main" alt="Test">
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
</p>

---

**Documentation**: <a href="https://carlos-rian.github.io/pysqlx-engine/" target="_blank">https://carlos-rian.github.io/pysqlx-engine/</a>

**Source Code**: <a href="https://github.com/carlos-rian/pysqlx-engine" target="_blank">https://github.com/carlos-rian/pysqlx-engine</a>

---

PySQLXEngine supports the option of sending **raw sql** to your database.

The PySQLXEngine is a minimalist **Async** SQL engine. Currently this lib only supports *asynchronous programming*, you need to use `await` in all methods.

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


PIP

```console
$ pip install pysqlx-engine
```

Poetry

```console
$ poetry add pysqlx-engine
```


## Example

* Create `main.py` file.

```python
import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def main():
    await db.connect()
    rows = await db.query(query="select 1 as number")
    print(rows)

asyncio.run(main())
```

* Run it

<div class="termy">

```console
$ python3 main.py

[BaseRow(number=1)]
```
</div>