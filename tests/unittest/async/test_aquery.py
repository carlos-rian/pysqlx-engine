from os import environ

import pytest
import pytest_asyncio

from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.errors import ConnectError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query(query="SELECT 1 as number")
    assert rows[0].number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    try:
        await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")
    except:
        ...

    rows = await conn.query(query="SELECT * FROM pysql_empty")
    assert rows == []
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_first(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first(query="SELECT 1 as number")
    assert row.number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_first_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    try:
        await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")
    except:
        ...

    rows = await conn.query_first(query="SELECT * FROM pysql_empty")
    assert rows is None

    conn.execute(stmt="DROP TABLE pysql_empty")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query(query="SELECT 1 as number", as_dict=True)
    assert rows[0]["number"] == 1

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    try:
        await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")
    except:
        ...

    rows = await conn.query(query="SELECT * FROM pysql_empty", as_dict=True)
    assert rows == []

    conn.execute(stmt="DROP TABLE pysql_empty")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_first_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first(query="SELECT 1 as number", as_dict=True)
    assert row["number"] == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_sample_query_first_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    try:
        await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")
    except:
        ...

    row = await conn.query_first(query="SELECT * FROM pysql_empty", as_dict=True)
    assert row is None

    conn.execute(stmt="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_success_complex_query_pgsql():
    conn: PySQLXEngine = await adb_pgsql()
    assert conn.connected is True

    with open("tests/unittest/sql/postgresql/create.sql", "r") as f:
        type_, table, *_ = f.read().split(";")
        await conn.execute(stmt=type_)
        await conn.execute(stmt=table)
    with open("tests/unittest/sql/postgresql/insert.sql", "r") as f:
        insert = f.read().split(";")[0]
        await conn.execute(stmt=insert)

    rows = await conn.query(query="SELECT * FROM pysqlx_table")
    assert rows[0].type_int == 1957483605

    await conn.execute(stmt="DROP TABLE pysqlx_table")
    await conn.execute(stmt="DROP TYPE colors CASCADE")

    await conn.close()
    assert conn.connected is False
