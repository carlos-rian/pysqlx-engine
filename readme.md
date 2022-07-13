# PySQLXEngine

<p align="center">
  <a href="/"><img src="docs/img/logo-text3.png" alt="PySQLXEngine Logo"></a>
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

**Documentation**: <a href="." target="_blank">Here</a>

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
* `Windows` <small>Experimental! Unit tests were not run on Windows.</small>

## Installation


PIP

```console
$ pip install pysqlx-engine
```

Poetry

```console
$ poetry add pysqlx-engine
```