from datetime import datetime, date
import uuid

import pytest
from pydantic import BaseModel

from pysqlx_engine import BaseRow, PySQLXEngineSync
from pysqlx_engine._core.const import CONFIG
from pysqlx_engine._core.errors import ParameterInvalidProviderError, ParameterInvalidValueError, QueryError
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    rows = conn.query(sql="SELECT 1 as number")
    assert rows[0].number == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_empty_table(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query(sql="SELECT * FROM pysql_empty")
    assert rows == []

    conn.execute(sql="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    row = conn.query_first(sql="SELECT 1 as number")
    assert row.number == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_empty_table(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query_first(sql="SELECT * FROM pysql_empty")
    assert rows is None

    conn.execute(sql="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    rows = conn.query_as_dict(sql="SELECT 1 as number")
    assert rows[0]["number"] == 1

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_empty_table_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query_as_dict(sql="SELECT * FROM pysql_empty")
    assert rows == []

    conn.execute(sql="DROP TABLE pysql_empty")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    row = conn.query_first_as_dict(sql="SELECT 1 as number")
    assert row["number"] == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_empty_table_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(sql="CREATE TABLE pysql_empty (id INT)")

    row = conn.query_first_as_dict(sql="SELECT * FROM pysql_empty")
    assert row is None

    conn.execute(sql="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


def test_complex_query_pgsql():
    from datetime import date, datetime, time
    from decimal import Decimal
    from uuid import UUID

    conn: PySQLXEngineSync = db_pgsql()
    assert conn.connected is True

    conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")
    conn.execute(sql="DROP TYPE IF EXISTS colors;")

    with open("tests/unittest/sql/postgresql/create.sql", "r") as f:
        type_, table, *_ = f.read().split(";")
        conn.execute(sql=type_)
        conn.execute(sql=table)

    with open("tests/unittest/sql/postgresql/insert.sql", "r") as f:
        insert = f.read().split(";")[0]
        conn.execute(sql=insert)

    row = (conn.query(sql="SELECT * FROM pysqlx_table"))[0]

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

    conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table")
    conn.execute(sql="DROP TYPE IF EXISTS colors CASCADE")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query(sql="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query_as_dict(sql="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_first(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query_first(sql="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_first_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query_first_as_dict(sql="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_query_with_null_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngineSync = db()

    assert conn.connected is True

    resp = conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    rows = conn.query(sql="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row.first_name, str)
        assert isinstance(row.last_name, (str, type(None)))
        assert isinstance(row.age, (int, type(None)))
        assert isinstance(row.email, (str, type(None)))
        assert isinstance(row.phone, (str, type(None)))
        assert isinstance(row.created_at, (str, datetime))
        assert isinstance(row.updated_at, (str, datetime))

    resp = conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_query_with_null_dict_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngineSync = db()

    assert conn.connected is True

    resp = conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    rows = conn.query_as_dict(sql="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row["first_name"], str)
        assert isinstance(row["last_name"], (str, type(None)))
        assert isinstance(row["age"], (int, type(None)))
        assert isinstance(row["email"], (str, type(None)))
        assert isinstance(row["phone"], (str, type(None)))
        assert isinstance(row["created_at"], str)
        assert isinstance(row["updated_at"], str)

    resp = conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_query_first_with_null_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngineSync = db()

    assert conn.connected is True

    resp = conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = conn.query_first(sql="SELECT * FROM test_table")

    assert isinstance(row.first_name, str)
    assert isinstance(row.last_name, (str, type(None)))
    assert isinstance(row.age, (int, type(None)))
    assert isinstance(row.email, (str, type(None)))
    assert isinstance(row.phone, (str, type(None)))
    assert isinstance(row.created_at, (str, datetime))
    assert isinstance(row.updated_at, (str, datetime))

    resp = conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_query_first_with_null_dict_values(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngineSync = db()

    assert conn.connected is True

    resp = conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = conn.query_first_as_dict(sql="SELECT * FROM test_table")

    assert isinstance(row["first_name"], str)
    assert isinstance(row["last_name"], (str, type(None)))
    assert isinstance(row["age"], (int, type(None)))
    assert isinstance(row["email"], (str, type(None)))
    assert isinstance(row["phone"], (str, type(None)))
    assert isinstance(row["created_at"], str)
    assert isinstance(row["updated_at"], str)

    resp = conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_query_first_get_column_types(db, typ, create_table: dict):
    table = create_table.get(typ)

    conn: PySQLXEngineSync = db()

    assert conn.connected is True

    resp = conn.execute(sql=table)
    assert resp == 0

    with open("tests/unittest/sql/insert.sql", "r") as f:
        rows = f.readlines()

    resp = conn.execute(sql=rows[0].replace("\n", ""))
    assert resp == 1

    row = conn.query_first(sql="SELECT * FROM test_table")

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

    resp = conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_with_my_model(db):
    conn: PySQLXEngineSync = db()

    class MyModel(BaseRow):
        id: int
        name: str

    rows = conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    row = rows[0]
    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_with_invalid_model(db):
    conn: PySQLXEngineSync = db()

    class MyModel(BaseModel):
        id: int
        name: str

    with pytest.raises(TypeError):
        conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_first_with_my_model(db):
    conn: PySQLXEngineSync = db()

    class MyModel(BaseRow):
        id: int
        name: str

    row = conn.query_first(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_first_with_invalid_model(db):
    conn: PySQLXEngineSync = db()

    class MyModel(BaseModel):
        id: int
        name: str

    with pytest.raises(TypeError):
        conn.query_first(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_with_my_model_get_columns(db):
    conn: PySQLXEngineSync = db()

    class MyModel(BaseRow):
        id: int
        name: str

    rows = conn.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel)

    row = rows[0]
    assert isinstance(row, MyModel)
    assert row.id == 1
    assert row.name == "Rian"

    columns = row.get_columns()

    assert columns["id"] == int
    assert columns["name"] == str


def test_invalid_sql_type_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(TypeError):
        conn.query_first(sql=1)

    with pytest.raises(TypeError):
        conn.query(sql=None)

    with pytest.raises(TypeError):
        conn.raw_cmd(sql={})

    with pytest.raises(TypeError):
        conn.execute(sql=[])

    conn.close()
    assert conn.connected is False


# new tests
def test_sample_query_first_with_param_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    from datetime import datetime, date

    CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngineSync = db()
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

    resp = conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert isinstance(resp.uid, uuid.UUID)
    assert resp.is_active is True
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))


def test_sample_query_first_with_param_db_mssql(db: PySQLXEngineSync = db_mssql):

    CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngineSync = db()
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

    resp = conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert isinstance(resp.uid, uuid.UUID)
    assert resp.is_active is True
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))


def test_sample_query_first_with_param_db_mysql(db: PySQLXEngineSync = db_mysql):
    from datetime import datetime, date

    CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngineSync = db()
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

    resp = conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
    assert isinstance(resp.date, (date, datetime))


def test_sample_query_first_with_param_db_sqlite(db: PySQLXEngineSync = db_sqlite):

    CONFIG.PYSQLX_SQL_LOG = True

    conn: PySQLXEngineSync = db()
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

    resp = conn.query_first(sql=sql, parameters=parameters)

    assert resp.id == 1
    assert resp.name == "John Doe"
    assert resp.age == 30
    assert resp.bytes == b"1234567890"
    assert resp.created_at == "2021-01-01 00:00:00"
    assert resp.updated_at == "2021-01-01 00:00:00"
    assert resp.date == "2021-01-01"


def test_invalid_param_type_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    CONFIG.PYSQLX_MSG_COLORIZE = True
    CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :id AS id"

    class MyType:
        i = 1

    with pytest.raises(TypeError):
        conn.query_first(sql=sql, parameters={"id": MyType()})

    conn.close()
    assert conn.connected is False


def test_invalid_param_array_with_heterogeneous_types_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    CONFIG.PYSQLX_ERROR_JSON_FMT = False
    CONFIG.PYSQLX_MSG_COLORIZE = False
    CONFIG.PYSQLX_SQL_LOG = False

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (1, 2, 3.1)}

    with pytest.raises(ParameterInvalidValueError):
        conn.query_first(sql=sql, parameters=parameters)

    CONFIG.PYSQLX_ERROR_JSON_FMT = True
    CONFIG.PYSQLX_MSG_COLORIZE = True
    CONFIG.PYSQLX_SQL_LOG = True

    with pytest.raises(ParameterInvalidValueError):
        conn.query_first(sql=sql, parameters=parameters)

    conn.close()
    assert conn.connected is False


def test_invalid_param_array_with_same_types_but_not_supported_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    CONFIG.PYSQLX_ERROR_JSON_FMT = False
    CONFIG.PYSQLX_MSG_COLORIZE = False
    CONFIG.PYSQLX_SQL_LOG = False

    class MyType:
        i = 1

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (MyType(), MyType(), MyType())}

    with pytest.raises(ParameterInvalidProviderError):
        conn.query_first(sql=sql, parameters=parameters)

    CONFIG.PYSQLX_ERROR_JSON_FMT = True
    CONFIG.PYSQLX_MSG_COLORIZE = True
    CONFIG.PYSQLX_SQL_LOG = True

    with pytest.raises(ParameterInvalidProviderError):
        conn.query_first(sql=sql, parameters=parameters)

    conn.close()
    assert conn.connected is False


def test_valid_param_with_empty_array_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as int[]) AS tuple"
    parameters = {"tuple": tuple()}

    resp = conn.query_first(sql=sql, parameters=parameters)
    assert resp.tuple == ()

    conn.close()
    assert conn.connected is False


def test_valid_param_with_int_array_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as int[]) AS tuple"
    parameters = {"tuple": (1, 2, 3, 4, 5)}

    resp = conn.query_first(sql=sql, parameters=parameters)
    assert resp.tuple == (1, 2, 3, 4, 5)

    conn.close()
    assert conn.connected is False


def test_valid_param_with_float_array_db_pgsql(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    sql = f"SELECT cast(:tuple as float[]) AS tuple"
    parameters = {"tuple": (1.3, 2.4, 3.5, 4.1, 5.2)}

    resp = conn.query_first(sql=sql, parameters=parameters)
    assert isinstance(resp.tuple, tuple)
    assert resp.tuple == (1.3, 2.4, 3.5, 4.1, 5.2)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_mssql, db_mysql])
def test_invalid_provider_to_array_param(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    CONFIG.PYSQLX_MSG_COLORIZE = True
    CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :tuple AS tuple"
    parameters = {"tuple": (1, 2, 3)}

    with pytest.raises(ParameterInvalidProviderError):
        conn.query_first(sql=sql, parameters=parameters)

    conn.close()
    assert conn.connected is False


def test_sample_param_type_db_pgsql_show_sql_colored(db: PySQLXEngineSync = db_pgsql):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    CONFIG.PYSQLX_MSG_COLORIZE = True
    CONFIG.PYSQLX_SQL_LOG = True

    sql = f"SELECT :id AS id"

    conn.query_first(sql=sql, parameters={"id": 1})

    conn.close()
    assert conn.connected is False
