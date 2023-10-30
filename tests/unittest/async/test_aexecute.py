from enum import Enum

import pytest

from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.errors import (
    ParameterInvalidProviderError,
    ParameterInvalidValueError,
)
from pysqlx_engine._core.param import try_tuple_enum
from pysqlx_engine.errors import ExecuteError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_execute_create_table(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(sql=table)
    assert resp == 0

    resp = await conn.execute(sql="DROP TABLE test_table;")
    assert resp == 0

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_execute_insert(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = await conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    resp = await conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_execute_invalid_table_insert(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(ExecuteError):
        await conn.execute(sql="INSERT INTO invalid_table (id) VALUES (1)")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql])
async def test_execute_sql_with_complex_param(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    from datetime import date, datetime, time
    from decimal import Decimal

    from tests.unittest.sql.mysql.value import data

    await conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")

    with open("tests/unittest/sql/mysql/create.sql", "r") as f:
        sql = f.read()
        resp = await conn.execute(sql=sql)
        assert resp == 0

    with open("tests/unittest/sql/mysql/insert.sql", "r") as f:
        sql = f.read()
        resp = await conn.execute(sql=sql, parameters=data)
        assert resp == 1

    resp = await conn.query_first(sql="SELECT * FROM pysqlx_table")

    assert isinstance(resp.type_int, int)
    assert isinstance(resp.type_smallint, int)
    assert isinstance(resp.type_bigint, int)
    assert isinstance(resp.type_numeric, Decimal)
    assert isinstance(resp.type_decimal, Decimal)
    assert isinstance(resp.type_float, float)
    assert isinstance(resp.type_double, float)
    assert isinstance(resp.type_char, str)
    assert isinstance(resp.type_varchar, str)
    assert isinstance(resp.type_nvarchar, str)
    assert isinstance(resp.type_text, str)
    assert isinstance(resp.type_boolean, bool)
    assert isinstance(resp.type_date, (date, datetime))  # type: ignore is wrong, Quaint returns datetime for date
    assert isinstance(resp.type_time, time)
    assert isinstance(resp.type_timestamp, datetime)
    assert isinstance(resp.type_datetime, datetime)
    assert isinstance(resp.type_enum, str)
    assert isinstance(resp.type_json, (dict, list))
    assert isinstance(resp.type_bytes, bytes)

    resp = await conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")
    assert resp == 0
    await conn.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_pgsql])
async def test_execute_sql_with_array_enum(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(sql="DROP TABLE IF EXISTS t_pysqlx_table;")
    await conn.execute(sql="DROP TYPE IF EXISTS t_colors;")
    await conn.execute(sql="CREATE TYPE t_colors as enum ('blue', 'red', 'gray', 'black');")
    await conn.execute(sql="CREATE TABLE t_pysqlx_table (type_array_enum t_colors[]);")

    class EnumTest(Enum):
        blue = "blue"
        red = "red"
        gray = "gray"
        black = "black"

    array = (EnumTest.blue, EnumTest.red, EnumTest.gray, EnumTest.black)
    resp = await conn.execute(
        sql="INSERT INTO t_pysqlx_table (type_array_enum) VALUES (:array)", parameters={"array": array}
    )
    assert resp == 1

    resp = await conn.query_first(sql="SELECT * FROM t_pysqlx_table")

    assert isinstance(resp.type_array_enum, tuple)
    assert isinstance(resp.type_array_enum[0], str)
    assert len(resp.type_array_enum) == 4

    await conn.execute(sql="DROP TABLE IF EXISTS t_pysqlx_table;")
    await conn.execute(sql="DROP TYPE IF EXISTS t_colors;")

    with pytest.raises(ParameterInvalidProviderError):
        try_tuple_enum("mysql", (), "")

    with pytest.raises(ParameterInvalidValueError):
        try_tuple_enum("postgresql", (EnumTest.black, 1), "")
