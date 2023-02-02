from tests.unittest.sql.mysql.value import data
from datetime import date, datetime, time
from decimal import Decimal

import uuid

import pytest
from pydantic import BaseModel

from pysqlx_engine import BaseRow, PySQLXEngine
from pysqlx_engine._core.const import LOG_CONFIG
from pysqlx_engine._core.errors import ParameterInvalidProviderError, ParameterInvalidValueError, QueryError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite
import enum


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query(sql="SELECT 1 as number")
    assert rows[0].number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query(sql="SELECT * FROM pysql_empty")
    assert rows == []

    await conn.execute(sql="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first(sql="SELECT 1 as number")
    assert row.number == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_empty_table(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query_first(sql="SELECT * FROM pysql_empty")
    assert rows is None

    await conn.execute(sql="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    rows = await conn.query_as_dict(sql="SELECT 1 as number")
    assert rows[0]["number"] == 1

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = await conn.query_as_dict(sql="SELECT * FROM pysql_empty")
    assert rows == []

    await conn.execute(sql="DROP TABLE pysql_empty")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    row = await conn.query_first_as_dict(sql="SELECT 1 as number")
    assert row["number"] == 1
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_sample_query_first_with_empty_table_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    row = await conn.query_first_as_dict(sql="SELECT * FROM pysql_empty")
    assert row is None

    await conn.execute(sql="DROP TABLE pysql_empty")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_complex_query_pgsql():
    from datetime import date, datetime, time
    from decimal import Decimal
    from uuid import UUID

    conn: PySQLXEngine = await adb_pgsql()
    assert conn.connected is True

    await conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")
    await conn.execute(sql="DROP TYPE IF EXISTS colors;")

    with open("tests/unittest/sql/postgresql/create.sql", "r") as f:
        type_, table, *_ = f.read().split(";")
        await conn.execute(sql=type_)
        await conn.execute(sql=table)

    with open("tests/unittest/sql/postgresql/insert.sql", "r") as f:
        insert = f.read().split(";")[0]
        await conn.execute(sql=insert)

    row = (await conn.query(sql="SELECT * FROM pysqlx_table"))[0]

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
    assert isinstance(row.type_array_text, tuple)
    assert isinstance(row.type_array_text[0], str)
    assert isinstance(row.type_array_integer, tuple)
    assert isinstance(row.type_array_integer[0], int)
    assert isinstance(row.type_array_date, tuple)
    assert isinstance(row.type_array_date[0], date)
    assert isinstance(row.type_array_uuid, tuple)
    assert isinstance(row.type_array_uuid[0], UUID)

    await conn.execute(sql="DROP TABLE IF EXISTS  pysqlx_table")
    await conn.execute(sql="DROP TYPE IF EXISTS colors CASCADE")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query(sql="SELECT * FROM invalid_table")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query_as_dict(sql="SELECT * FROM invalid_table")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_first(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query_first(sql="SELECT * FROM invalid_table")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_error_invalid_query_first_as_dict(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        await conn.query_first_as_dict(sql="SELECT * FROM invalid_table")

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

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = await conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    rows = await conn.query(sql="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row.first_name, str)
        assert isinstance(row.last_name, (str, type(None)))
        assert isinstance(row.age, (int, type(None)))
        assert isinstance(row.email, (str, type(None)))
        assert isinstance(row.phone, (str, type(None)))
        assert isinstance(row.created_at, (str, datetime))
        assert isinstance(row.updated_at, (str, datetime))

    resp = await conn.execute(sql="DROP TABLE test_table;")
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

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = await conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    rows = await conn.query_as_dict(sql="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row["first_name"], str)
        assert isinstance(row["last_name"], (str, type(None)))
        assert isinstance(row["age"], (int, type(None)))
        assert isinstance(row["email"], (str, type(None)))
        assert isinstance(row["phone"], (str, type(None)))
        assert isinstance(row["created_at"], str)
        assert isinstance(row["updated_at"], str)

    resp = await conn.execute(sql="DROP TABLE test_table;")
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

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first(sql="SELECT * FROM test_table")

    assert isinstance(row.first_name, str)
    assert isinstance(row.last_name, (str, type(None)))
    assert isinstance(row.age, (int, type(None)))
    assert isinstance(row.email, (str, type(None)))
    assert isinstance(row.phone, (str, type(None)))
    assert isinstance(row.created_at, (str, datetime))
    assert isinstance(row.updated_at, (str, datetime))

    resp = await conn.execute(sql="DROP TABLE test_table;")
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

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first_as_dict(sql="SELECT * FROM test_table")

    assert isinstance(row["first_name"], str)
    assert isinstance(row["last_name"], (str, type(None)))
    assert isinstance(row["age"], (int, type(None)))
    assert isinstance(row["email"], (str, type(None)))
    assert isinstance(row["phone"], (str, type(None)))
    assert isinstance(row["created_at"], str)
    assert isinstance(row["updated_at"], str)

    resp = await conn.execute(sql="DROP TABLE test_table;")
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

    resp = await conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = await conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = await conn.query_first(sql="SELECT * FROM test_table")

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

    resp = await conn.execute(sql="DROP TABLE test_table;")
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

    rows = await conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

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
        await conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_first_with_my_model(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseRow):
        id: int
        name: str

    row = await conn.query_first(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

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
        await conn.query_first(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_with_my_model_get_columns(db):
    conn: PySQLXEngine = await db()

    class MyModel(BaseRow):
        id: int
        name: str

    rows = await conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    row = rows[0]
    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"

    columns = row.get_columns()

    assert columns["id"] == int
    assert columns["name"] == str


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_pgsql])
async def test_py_sqlx_error_invalid_query_type(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(TypeError):
        await conn.query_first(sql=1)

    with pytest.raises(TypeError):
        await conn.query(sql=None)

    with pytest.raises(TypeError):
        await conn.raw_cmd(sql={})

    with pytest.raises(TypeError):
        await conn.execute(sql=[])

    await conn.close()
    assert conn.connected is False


# new tests
@pytest.mark.asyncio
async def test_sample_query_first_with_param_db_pgsql(db: PySQLXEngine = adb_pgsql):
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"""
        SELECT 
        :id                             AS id, 
        :name                           AS name, 
        :age                            AS age,
        CAST(:bytes AS bytea)           AS bytes,
        CAST(:uuid AS UUID)             AS uid,
        CAST(:is_active AS BOOL)        AS is_active, 
        CAST(:created_at AS TIMESTAMP)  AS created_at, 
        CAST(:updated_at AS TIMESTAMP)  AS updated_at, 
        CAST(:date AS DATE)             AS date;
    """
    parameters = {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "bytes": b"1234567890",
        "uuid": uuid.uuid4(),
        "is_active": True,
        "created_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "updated_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "date": date.fromisoformat("2021-01-01"),
    }

    resp = await conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert isinstance(resp.uid, uuid.UUID)
    assert resp.is_active is True
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_sample_query_first_with_param_db_mssql(db: PySQLXEngine = adb_mssql):
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"""
        SELECT 
        :id                             AS id, 
        :name                           AS name, 
        :age                            AS age,
        :bytes                          AS bytes,
        CAST(:uuid AS UNIQUEIDENTIFIER) AS uid,
        CAST(:is_active AS BIT)         AS is_active, 
        CAST(:created_at AS DATETIME)   AS created_at, 
        CAST(:updated_at AS DATETIME)   AS updated_at, 
        CAST(:date AS DATE)             AS date;
    """
    parameters = {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "bytes": b"1234567890",
        "uuid": uuid.uuid4(),
        "is_active": True,
        "created_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "updated_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "date": date.fromisoformat("2021-01-01"),
    }

    resp = await conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert isinstance(resp.uid, uuid.UUID)
    assert resp.is_active is True
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_sample_query_first_with_param_db_mysql(db: PySQLXEngine = adb_mysql):
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"""
        SELECT 
        :id                           AS id, 
        :name                         AS name, 
        :age                          AS age, 
        :null_value                   AS null_value,
        CAST(:created_at              AS DATETIME) AS created_at, 
        CAST(:updated_at              AS DATETIME) AS updated_at, 
        CAST(:date AS DATE)           AS date;
    """
    parameters = {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "null_value": None,
        "created_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "updated_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "date": date.fromisoformat("2021-01-01"),
    }

    resp = await conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_sample_query_first_with_param_db_sqlite(db: PySQLXEngine = adb_sqlite):
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"""
        SELECT 
        :id                     AS id, 
        :name                   AS name, 
        :age                    AS age, 
        :null_value             AS null_value,
        CAST(:bytes AS BLOB)    AS bytes,
        :created_at             AS created_at, 
        :updated_at             AS updated_at, 
        :date                   AS date;
    """
    parameters = {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "null_value": None,
        "bytes": b"1234567890",
        "created_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "updated_at": datetime.fromisoformat("2021-01-01 00:00:00"),
        "date": date.fromisoformat("2021-01-01"),
    }

    resp = await conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert resp.created_at == "2021-01-01 00:00:00"
    assert resp.updated_at == "2021-01-01 00:00:00"
    assert resp.date == "2021-01-01"

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_invalid_param_type_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :id AS id"

    class MyType:
        i = 1

    with pytest.raises(TypeError):
        await conn.query_first(sql=sql, parameters={"id": MyType()})

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_invalid_param_array_with_heterogeneous_types_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = False
    LOG_CONFIG.PYSQLX_USE_COLOR = False
    LOG_CONFIG.PYSQLX_SQL_LOG = False

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (1, 2, 3.1)}

    with pytest.raises(ParameterInvalidValueError):
        await conn.query_first(sql=sql, parameters=parameters)

    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    with pytest.raises(ParameterInvalidValueError):
        await conn.query_first(sql=sql, parameters=parameters)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_invalid_param_array_with_same_types_but_not_supported_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = False
    LOG_CONFIG.PYSQLX_USE_COLOR = False
    LOG_CONFIG.PYSQLX_SQL_LOG = False

    class MyType:
        i = 1

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (MyType(), MyType(), MyType())}

    with pytest.raises(ParameterInvalidProviderError):
        await conn.query_first(sql=sql, parameters=parameters)

    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    with pytest.raises(ParameterInvalidProviderError):
        await conn.query_first(sql=sql, parameters=parameters)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_valid_param_with_empty_array_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as int[]) AS tuple"
    parameters = {"tuple": tuple()}

    resp = await conn.query_first(sql=sql, parameters=parameters)
    assert resp.tuple == ()

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_valid_param_with_int_array_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as int[]) AS tuple"
    parameters = {"tuple": (1, 2, 3, 4, 5)}

    resp = await conn.query_first(sql=sql, parameters=parameters)
    assert resp.tuple == (1, 2, 3, 4, 5)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_valid_param_with_float_array_db_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as float[]) AS tuple"
    parameters = {"tuple": (1.3, 2.4, 3.5, 4.1, 5.2)}

    resp = await conn.query_first(sql=sql, parameters=parameters)
    assert isinstance(resp.tuple, tuple)
    assert resp.tuple == (1.3, 2.4, 3.5, 4.1, 5.2)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_mssql, adb_mysql])
async def test_invalid_provider_to_array_param(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (1, 2, 3)}

    with pytest.raises(ParameterInvalidProviderError):
        await conn.query_first(sql=sql, parameters=parameters)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_sample_param_type_db_pgsql_show_sql_colored(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :id AS id"

    await conn.query_first(sql=sql, parameters={"id": 1})

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_with_complex_param_query_adb_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    parameters = {
        "type_int": 1,
        "type_smallint": 2,
        "type_bigint": 3,
        "type_numeric": 14.8389,
        "type_float": 13343400,
        "type_double": 1.6655444,
        "type_decimal": Decimal("19984"),
        "type_char": "r",
        "type_varchar": "hfhfjjieurjnnd",
        "type_nvarchar": "$~k;dldëjdjd",
        "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
        "type_boolean": True,
        "type_date": date.fromisoformat("2022-01-01"),
        "type_time": time.fromisoformat("12:10:11"),
        "type_timestamp": datetime.fromisoformat("2022-12-20 08:59:55"),
        "type_json": ["name", "age"],
        "type_bytes": "super bytes".encode("utf-8"),
        "type_int_array": (1, 2, 3, 4, 5),
        "type_float_array": (1.3, 2.4, 3.5, 4.1, 5.2),
    }

    sql = f"""
        SELECT
            :type_int AS type_int,
            :type_smallint AS type_smallint,
            :type_bigint AS type_bigint,
            
            CAST(:type_float AS FLOAT) AS type_float,
            CAST(:type_double AS FLOAT) AS type_double,
            CAST(:type_decimal AS DECIMAL) AS type_decimal,
            CAST(:type_numeric AS DECIMAL) AS type_numeric,

            :type_char AS type_char,
            :type_varchar AS type_varchar,
            :type_nvarchar AS type_nvarchar,
            :type_text AS type_text,

            :type_boolean AS type_boolean,
            CAST(:type_date AS DATE) AS type_date,
            CAST(:type_time AS TIME) AS type_time,
            CAST(:type_timestamp AS TIMESTAMP) AS type_timestamp,
            CAST(:type_json AS JSON) AS type_json,
            CAST(:type_bytes AS bytea) AS type_bytes,
            CAST(:type_int_array AS int[]) AS type_int_array,
            CAST(:type_float_array AS float[]) AS type_float_array

    """

    resp = await conn.query(sql=sql, parameters=parameters)

    assert isinstance(resp[0].type_int, int)
    assert isinstance(resp[0].type_smallint, int)
    assert isinstance(resp[0].type_bigint, int)

    assert isinstance(resp[0].type_float, float)
    assert isinstance(resp[0].type_double, float)

    assert isinstance(resp[0].type_decimal, Decimal)
    assert isinstance(resp[0].type_numeric, Decimal)

    assert isinstance(resp[0].type_char, str)
    assert isinstance(resp[0].type_varchar, str)
    assert isinstance(resp[0].type_nvarchar, str)
    assert isinstance(resp[0].type_text, str)

    assert isinstance(resp[0].type_boolean, bool)

    assert isinstance(resp[0].type_date, date)
    assert isinstance(resp[0].type_time, time)
    assert isinstance(resp[0].type_timestamp, datetime)

    assert isinstance(resp[0].type_json, list)
    assert isinstance(resp[0].type_bytes, bytes)

    assert isinstance(resp[0].type_int_array, tuple)
    assert isinstance(resp[0].type_float_array, tuple)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_with_complex_param_query_first_adb_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    parameters = {
        "type_int": 1,
        "type_smallint": 2,
        "type_bigint": 3,
        "type_numeric": 14.8389,
        "type_float": 13343400,
        "type_double": 1.6655444,
        "type_decimal": Decimal("19984"),
        "type_char": "r",
        "type_varchar": "hfhfjjieurjnnd",
        "type_nvarchar": "$~k;dldëjdjd",
        "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
        "type_boolean": True,
        "type_date": date.fromisoformat("2022-01-01"),
        "type_time": time.fromisoformat("12:10:11"),
        "type_timestamp": datetime.fromisoformat("2022-12-20 08:59:55"),
        "type_json": ["name", "age"],
        "type_bytes": "super bytes".encode("utf-8"),
        "type_int_array": (1, 2, 3, 4, 5),
        "type_float_array": (1.3, 2.4, 3.5, 4.1, 5.2),
    }

    sql = f"""
        SELECT
            :type_int AS type_int,
            :type_smallint AS type_smallint,
            :type_bigint AS type_bigint,
            
            CAST(:type_float AS FLOAT) AS type_float,
            CAST(:type_double AS FLOAT) AS type_double,
            CAST(:type_decimal AS DECIMAL) AS type_decimal,
            CAST(:type_numeric AS DECIMAL) AS type_numeric,

            :type_char AS type_char,
            :type_varchar AS type_varchar,
            :type_nvarchar AS type_nvarchar,
            :type_text AS type_text,

            :type_boolean AS type_boolean,
            CAST(:type_date AS DATE) AS type_date,
            CAST(:type_time AS TIME) AS type_time,
            CAST(:type_timestamp AS TIMESTAMP) AS type_timestamp,
            CAST(:type_json AS JSON) AS type_json,
            CAST(:type_bytes AS bytea) AS type_bytes,
            CAST(:type_int_array AS int[]) AS type_int_array,
            CAST(:type_float_array AS float[]) AS type_float_array

    """

    resp = await conn.query_first(sql=sql, parameters=parameters)

    assert isinstance(resp.type_int, int)
    assert isinstance(resp.type_smallint, int)
    assert isinstance(resp.type_bigint, int)

    assert isinstance(resp.type_float, float)
    assert isinstance(resp.type_double, float)

    assert isinstance(resp.type_decimal, Decimal)
    assert isinstance(resp.type_numeric, Decimal)

    assert isinstance(resp.type_char, str)
    assert isinstance(resp.type_varchar, str)
    assert isinstance(resp.type_nvarchar, str)
    assert isinstance(resp.type_text, str)

    assert isinstance(resp.type_boolean, bool)

    assert isinstance(resp.type_date, date)
    assert isinstance(resp.type_time, time)
    assert isinstance(resp.type_timestamp, datetime)

    assert isinstance(resp.type_json, list)
    assert isinstance(resp.type_bytes, bytes)

    assert isinstance(resp.type_int_array, tuple)
    assert isinstance(resp.type_float_array, tuple)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_with_complex_param_query_as_dict_adb_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    parameters = {
        "type_int": 1,
        "type_smallint": 2,
        "type_bigint": 3,
        "type_numeric": 14.8389,
        "type_float": 13343400,
        "type_double": 1.6655444,
        "type_decimal": Decimal("19984"),
        "type_char": "r",
        "type_varchar": "hfhfjjieurjnnd",
        "type_nvarchar": "$~k;dldëjdjd",
        "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
        "type_boolean": True,
        "type_date": date.fromisoformat("2022-01-01"),
        "type_time": time.fromisoformat("12:10:11"),
        "type_timestamp": datetime.fromisoformat("2022-12-20 08:59:55"),
        "type_json": ["name", "age"],
        "type_bytes": "super bytes".encode("utf-8"),
        "type_int_array": (1, 2, 3, 4, 5),
        "type_float_array": (1.3, 2.4, 3.5, 4.1, 5.2),
    }

    sql = f"""
        SELECT
            :type_int AS type_int,
            :type_smallint AS type_smallint,
            :type_bigint AS type_bigint,
            
            CAST(:type_float AS FLOAT) AS type_float,
            CAST(:type_double AS FLOAT) AS type_double,
            CAST(:type_decimal AS DECIMAL) AS type_decimal,
            CAST(:type_numeric AS DECIMAL) AS type_numeric,

            :type_char AS type_char,
            :type_varchar AS type_varchar,
            :type_nvarchar AS type_nvarchar,
            :type_text AS type_text,

            :type_boolean AS type_boolean,
            CAST(:type_date AS DATE) AS type_date,
            CAST(:type_time AS TIME) AS type_time,
            CAST(:type_timestamp AS TIMESTAMP) AS type_timestamp,
            CAST(:type_json AS JSON) AS type_json,
            CAST(:type_bytes AS bytea) AS type_bytes,
            CAST(:type_int_array AS int[]) AS type_int_array,
            CAST(:type_float_array AS float[]) AS type_float_array

    """

    resp = await conn.query_as_dict(sql=sql, parameters=parameters)

    assert isinstance(resp[0].get("type_int"), int)
    assert isinstance(resp[0].get("type_smallint"), int)
    assert isinstance(resp[0].get("type_bigint"), int)

    assert isinstance(resp[0].get("type_float"), float)
    assert isinstance(resp[0].get("type_double"), float)

    assert isinstance(resp[0].get("type_decimal"), str)
    assert isinstance(resp[0].get("type_numeric"), str)

    assert isinstance(resp[0].get("type_char"), str)
    assert isinstance(resp[0].get("type_varchar"), str)
    assert isinstance(resp[0].get("type_nvarchar"), str)
    assert isinstance(resp[0].get("type_text"), str)

    assert isinstance(resp[0].get("type_boolean"), bool)

    assert isinstance(resp[0].get("type_date"), str)
    assert isinstance(resp[0].get("type_time"), str)
    assert isinstance(resp[0].get("type_timestamp"), str)

    assert isinstance(resp[0].get("type_json"), str)
    assert isinstance(resp[0].get("type_bytes"), bytes)

    assert isinstance(resp[0].get("type_int_array"), tuple)
    assert isinstance(resp[0].get("type_float_array"), tuple)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
async def test_with_complex_param_query_first_as_dict_adb_pgsql(db: PySQLXEngine = adb_pgsql):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    parameters = {
        "type_int": 1,
        "type_smallint": 2,
        "type_bigint": 3,
        "type_numeric": 14.8389,
        "type_float": 13343400,
        "type_double": 1.6655444,
        "type_decimal": Decimal("19984"),
        "type_char": "r",
        "type_varchar": "hfhfjjieurjnnd",
        "type_nvarchar": "$~k;dldëjdjd",
        "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
        "type_boolean": True,
        "type_date": date.fromisoformat("2022-01-01"),
        "type_time": time.fromisoformat("12:10:11"),
        "type_timestamp": datetime.fromisoformat("2022-12-20 08:59:55"),
        "type_json": ["name", "age"],
        "type_bytes": "super bytes".encode("utf-8"),
        "type_int_array": (1, 2, 3, 4, 5),
        "type_float_array": (1.3, 2.4, 3.5, 4.1, 5.2),
    }

    sql = f"""
        SELECT
            :type_int AS type_int,
            :type_smallint AS type_smallint,
            :type_bigint AS type_bigint,
            
            CAST(:type_float AS FLOAT) AS type_float,
            CAST(:type_double AS FLOAT) AS type_double,
            CAST(:type_decimal AS DECIMAL) AS type_decimal,
            CAST(:type_numeric AS DECIMAL) AS type_numeric,

            :type_char AS type_char,
            :type_varchar AS type_varchar,
            :type_nvarchar AS type_nvarchar,
            :type_text AS type_text,

            :type_boolean AS type_boolean,
            CAST(:type_date AS DATE) AS type_date,
            CAST(:type_time AS TIME) AS type_time,
            CAST(:type_timestamp AS TIMESTAMP) AS type_timestamp,
            CAST(:type_json AS JSON) AS type_json,
            CAST(:type_bytes AS bytea) AS type_bytes,
            CAST(:type_int_array AS int[]) AS type_int_array,
            CAST(:type_float_array AS float[]) AS type_float_array

    """

    resp = await conn.query_first_as_dict(sql=sql, parameters=parameters)

    assert isinstance(resp.get("type_int"), int)
    assert isinstance(resp.get("type_smallint"), int)
    assert isinstance(resp.get("type_bigint"), int)

    assert isinstance(resp.get("type_float"), float)
    assert isinstance(resp.get("type_double"), float)

    assert isinstance(resp.get("type_decimal"), str)
    assert isinstance(resp.get("type_numeric"), str)

    assert isinstance(resp.get("type_char"), str)
    assert isinstance(resp.get("type_varchar"), str)
    assert isinstance(resp.get("type_nvarchar"), str)
    assert isinstance(resp.get("type_text"), str)

    assert isinstance(resp.get("type_boolean"), bool)

    assert isinstance(resp.get("type_date"), str)
    assert isinstance(resp.get("type_time"), str)
    assert isinstance(resp.get("type_timestamp"), str)

    assert isinstance(resp.get("type_json"), str)
    assert isinstance(resp.get("type_bytes"), bytes)

    assert isinstance(resp.get("type_int_array"), tuple)
    assert isinstance(resp.get("type_float_array"), tuple)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql, adb_pgsql])
async def test_query_first_col_without_the_name(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.query_first("SELECT 1, 2")
    assert resp.col_0 == 1
    assert resp.col_1 == 2

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql, adb_sqlite])
async def test_query_first_col_is_number(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.query_first("SELECT 1, 2")

    assert resp.col_1 == 1
    assert resp.col_2 == 2

    assert isinstance(resp.col_1, int)
    assert isinstance(resp.col_2, int)

    resp = await conn.query_first("SELECT -11.43, -24432")

    assert isinstance(resp.col_11_43, (Decimal, float))
    assert isinstance(resp.col_24432, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql, adb_sqlite])
async def test_query_first_col_with_same_name(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.query_first("SELECT 1 as x, 2 as x")

    assert resp.x == 1
    assert resp.x_1 == 2

    assert isinstance(resp.x, int)
    assert isinstance(resp.x_1, int)

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql, adb_sqlite])
async def test_query_first_col_with_same_name_as_str(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.query_first("SELECT 1 as x, 2 as x")

    assert str(resp) == "BaseRow(x=1, x_1=2)" or str(resp) == "BaseRow(x_1=2, x=1)"

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql])
async def test_query_first_json_param_to_sql_server(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    param = {"a": 1, "b": "what's", "c": 3}
    resp = await conn.query_first(sql="SELECT :x as data", parameters={"x": param})

    assert resp.data == '{"a": 1, "b": "what\'s", "c": 3}'

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql, adb_mysql, adb_sqlite, adb_pgsql])
async def test_query_first_enum_param(db: PySQLXEngine):
    class EnumType(enum.Enum):
        ADGROUP = "ADGROUP"
        CAMPAIGN = "CAMPAIGN"
        KEYWORD = "KEYWORD"
        TARGETAD = "TARGETAD"

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = "SELECT :adgroup AS adgroup, :campaign AS campaign, :keyword AS keyword, :targetad AS targetad"
    param = {
        "adgroup": EnumType.ADGROUP,
        "campaign": EnumType.CAMPAIGN,
        "keyword": EnumType.KEYWORD,
        "targetad": EnumType.TARGETAD,
    }
    resp = await conn.query_first(sql=sql, parameters=param)

    assert resp.adgroup == "ADGROUP"
    assert resp.campaign == "CAMPAIGN"
    assert resp.keyword == "KEYWORD"
    assert resp.targetad == "TARGETAD"

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql, adb_mysql, adb_sqlite, adb_pgsql])
async def test_query_first_enum_param_invalid_value(db: PySQLXEngine):
    class MyType:
        i = 1

    class EnumType(enum.Enum):
        ADGROUP = MyType()

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    sql = "SELECT :adgroup AS adgroup"
    param = {"adgroup": EnumType.ADGROUP}

    with pytest.raises(ParameterInvalidValueError):
        await conn.query_first(sql=sql, parameters=param)

    await conn.close()
    assert conn.connected is False
