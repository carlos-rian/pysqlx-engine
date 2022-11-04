from datetime import datetime

import pytest
from pydantic import BaseModel

from pysqlx_engine import BaseRow, PySQLXEngine
from pysqlx_engine._core.errors import QueryError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query(query="SELECT 1 as number")
    assert rows[0].number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query(query="SELECT * FROM pysql_empty")
    assert rows == []

    await conn.execute(stmt="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first(query="SELECT 1 as number")
    assert row.number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query_first(query="SELECT * FROM pysql_empty")
    assert rows is None

    await conn.execute(stmt="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query(query="SELECT 1 as number", as_dict=True)
    assert rows[0]["number"] == 1

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query(query="SELECT * FROM pysql_empty", as_dict=True)
    assert rows == []

    await conn.execute(stmt="DROP TABLE pysql_empty")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first(query="SELECT 1 as number", as_dict=True)
    assert row["number"] == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    row = await conn.query_first(query="SELECT * FROM pysql_empty", as_dict=True)
    assert row is None

    await conn.execute(stmt="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_complex_query_pgsql():
    from datetime import date, datetime, time
    from decimal import Decimal
    from typing import List
    from uuid import UUID

    conn: PySQLXEngine = await adb_pgsql()
    assert conn.connected is True

    with open("tests/unittest/sql/postgresql/create.sql", "r") as f:
        type_, table, *_ = f.read().split(";")
        await conn.execute(stmt=type_)
        await conn.execute(stmt=table)

    with open("tests/unittest/sql/postgresql/insert.sql", "r") as f:
        insert = f.read().split(";")[0]
        await conn.execute(stmt=insert)

    row = (await conn.query(query="SELECT * FROM pysqlx_table"))[0]

    assert isinstance(row.type_smallint, int)
    assert isinstance(row.type_bigint, int)
    assert isinstance(row.type_serial, int)
    assert isinstance(row.type_smallserial, int)
    assert isinstance(row.type_bigserial, int)
    assert isinstance(row.type_numeric, Decimal)
    assert isinstance(row.type_float, float)
    assert isinstance(row.type_double, float)
    assert isinstance(row.type_money, Decimal)
    assert isinstance(row.type_char, str)
    assert isinstance(row.type_varchar, str)
    assert isinstance(row.type_text, str)
    assert isinstance(row.type_boolean, bool)
    assert isinstance(row.type_date, date)
    assert isinstance(row.type_time, time)
    assert isinstance(row.type_datetime, datetime)
    assert isinstance(row.type_datetimetz, datetime)
    assert isinstance(row.type_enum, str)
    assert isinstance(row.type_uuid, UUID)
    assert isinstance(row.type_json, (dict, list))
    assert isinstance(row.type_jsonb, (dict, list))
    assert isinstance(row.type_xml, str)
    assert isinstance(row.type_inet, str)
    assert isinstance(row.type_bytes, bytes)
    assert isinstance(row.type_array_text, List)
    assert isinstance(row.type_array_text[0], str)
    assert isinstance(row.type_array_integer, List)
    assert isinstance(row.type_array_integer[0], int)
    assert isinstance(row.type_array_date, list)
    assert isinstance(row.type_array_date[0], date)
    assert isinstance(row.type_array_uuid, list)
    assert isinstance(row.type_array_uuid[0], UUID)

    await conn.execute(stmt="DROP TABLE pysqlx_table")
    await conn.execute(stmt="DROP TYPE colors CASCADE")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query(query="SELECT * FROM invalid_table")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query(query="SELECT * FROM invalid_table", as_dict=True)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_first(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query_first(query="SELECT * FROM invalid_table")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_first_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query_first(query="SELECT * FROM invalid_table", as_dict=True)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_query_with_null_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(stmt=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = await conn.execute(stmt=row.replace("\n", ""))
        assert resp == 1

    rows = await conn.query(query="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row.first_name, str)
        assert isinstance(row.last_name, (str, type(None)))
        assert isinstance(row.age, (int, type(None)))
        assert isinstance(row.email, (str, type(None)))
        assert isinstance(row.phone, (str, type(None)))
        assert isinstance(row.created_at, (str, datetime))
        assert isinstance(row.updated_at, (str, datetime))

    resp = await conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_query_with_null_dict_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(stmt=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = await conn.execute(stmt=row.replace("\n", ""))
        assert resp == 1

    rows = await conn.query(query="SELECT * FROM test_table", as_dict=True)
    for row in rows:
        assert isinstance(row["first_name"], str)
        assert isinstance(row["last_name"], (str, type(None)))
        assert isinstance(row["age"], (int, type(None)))
        assert isinstance(row["email"], (str, type(None)))
        assert isinstance(row["phone"], (str, type(None)))
        assert isinstance(row["created_at"], str)
        assert isinstance(row["updated_at"], str)

    resp = await conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_query_first_with_null_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(stmt=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(stmt=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first(query="SELECT * FROM test_table")

    assert isinstance(row.first_name, str)
    assert isinstance(row.last_name, (str, type(None)))
    assert isinstance(row.age, (int, type(None)))
    assert isinstance(row.email, (str, type(None)))
    assert isinstance(row.phone, (str, type(None)))
    assert isinstance(row.created_at, (str, datetime))
    assert isinstance(row.updated_at, (str, datetime))

    resp = await conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_query_first_with_null_dict_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(stmt=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(stmt=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first(query="SELECT * FROM test_table", as_dict=True)

    assert isinstance(row["first_name"], str)
    assert isinstance(row["last_name"], (str, type(None)))
    assert isinstance(row["age"], (int, type(None)))
    assert isinstance(row["email"], (str, type(None)))
    assert isinstance(row["phone"], (str, type(None)))
    assert isinstance(row["created_at"], str)
    assert isinstance(row["updated_at"], str)

    resp = await conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db,typ", [(adb_sqlite, "sqlite"), (adb_pgsql, "pgsql"), (adb_mssql, "mssql"), (adb_mysql, "mysql")]
)
async def test_query_first_get_column_types(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngine = await db()

    assert conn.connected is True

    resp = await conn.execute(stmt=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(stmt=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first(query="SELECT * FROM test_table")

    assert isinstance(row.first_name, str)
    assert isinstance(row.last_name, (str, type(None)))
    assert isinstance(row.age, (int, type(None)))
    assert isinstance(row.email, (str, type(None)))
    assert isinstance(row.phone, (str, type(None)))
    assert isinstance(row.created_at, (str, datetime))
    assert isinstance(row.updated_at, (str, datetime))

    columns = row.get_columns()
    assert isinstance(columns, dict)
    assert len(columns) == 8

    assert columns["first_name"] == str
    assert columns["last_name"] == str
    assert columns["age"] == int
    assert columns["email"] == str
    assert columns["phone"] == str
    assert columns["created_at"] == str or columns["created_at"] == datetime  # sqlite not support datetime
    assert columns["updated_at"] == str or columns["updated_at"] == datetime  # sqlite not support datetime

    resp = await conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_with_my_model(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseRow):
        id: int
        name: str

    rows = await conn.query(query="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    row = rows[0]
    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_with_invalid_model(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseModel):
        id: int
        name: str

    with pytest.raises(TypeError):
        await conn.query(query="SELECT 1 AS id, 'Rian' AS name", model=MyModel)


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_first_with_my_model(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseRow):
        id: int
        name: str

    row = await conn.query_first(query="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_first_with_invalid_model(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseModel):
        id: int
        name: str

    with pytest.raises(TypeError):
        await conn.query_first(query="SELECT 1 AS id, 'Rian' AS name", model=MyModel)
