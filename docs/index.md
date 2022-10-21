# PySQLXEngine

<p align="center">
  <a href="/"><img src="./img/logo-text3.png" alt="PySQLXEngine Logo"></a>
</p>
<p align="center">
    <em>PySQLXEngine, a minimalist SQL engine, ready for production</em>
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

!!! warning
    I'm writing a new version with native support between Rust and Python using the Pyo3 lib, making this lib smaller and extremely faster, in some tests it's even 10x faster than the current version! 

    *The version 1.0.0 may have some changes in the type core, but it will become very friendly, but there will be a break in compatibility between version zero and 1.0.0!*


PySQLXEngine supports the option of sending **raw sql** to your database.

The PySQLXEngine is a minimalist [SQL engine](https://github.com/carlos-rian/pysqlx-engine). Supports [**async**](https://docs.python.org/3/library/asyncio.html) and [**sync**](https://deepsource.io/glossary/synchronous-programming/) programming.

All SQL that is executed using the PySQLXEngine is atomic; that is, only one statement is performed at a time. Only the first one will be completed if you send an Insert and a select. This is one of the ways to deal with SQL ingestion. 
_One detail is that [`COMMIT`](https://www.geeksforgeeks.org/difference-between-commit-and-rollback-in-sql) and [`ROLLBACK`](https://www.geeksforgeeks.org/difference-between-commit-and-rollback-in-sql) are automatic!!! This is not changeable now_ (__version 1.0.0 will bring this future__).



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


=== "PIP"
    <small>[Pip](https://pypi.org)</small>
    <div class="termy">

    ```console
    $ pip install pysqlx-engine
    ```
    
    </div>

=== "Poetry"
    <small>[Poetry](https://python-poetry.org)</small>
    <div class="termy">

    ```console
    $ poetry add pysqlx-engine
    ```
    
    </div>


## Example

* Create `main.py` file.

=== "Async"
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
=== "Sync"
    ```python
    
    from sqlx_engine import SQLXEngineSync

    uri = "file:./db.db"
    db = SQLXEngineSync(provider="sqlite", uri=uri)

    def main():
        db.connect()
        rows = db.query(query="select 1 as number")
        print(rows)

    main()
    ```

* Run it

<div class="termy">

```console
$ python3 main.py

[BaseRow(number=1)]
```
</div>
