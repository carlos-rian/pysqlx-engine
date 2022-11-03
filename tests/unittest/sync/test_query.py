import pytest

from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine._core.errors import QueryError
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    rows = conn.query(query="SELECT 1 as number")
    assert rows[0].number == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_empty_table(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query(query="SELECT * FROM pysql_empty")
    assert rows == []

    conn.execute(stmt="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    row = conn.query_first(query="SELECT 1 as number")
    assert row.number == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_empty_table(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query_first(query="SELECT * FROM pysql_empty")
    assert rows is None

    conn.execute(stmt="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    rows = conn.query(query="SELECT 1 as number", as_dict=True)
    assert rows[0]["number"] == 1

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_with_empty_table_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    rows = conn.query(query="SELECT * FROM pysql_empty", as_dict=True)
    assert rows == []

    conn.execute(stmt="DROP TABLE pysql_empty")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    row = conn.query_first(query="SELECT 1 as number", as_dict=True)
    assert row["number"] == 1
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_sample_query_first_with_empty_table_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.execute(stmt="CREATE TABLE pysql_empty (id INT)")

    row = conn.query_first(query="SELECT * FROM pysql_empty", as_dict=True)
    assert row is None

    conn.execute(stmt="DROP TABLE pysql_empty")
    conn.close()
    assert conn.connected is False


def test_complex_query_pgsql():
    from datetime import date, datetime, time
    from decimal import Decimal
    from typing import List
    from uuid import UUID

    conn: PySQLXEngineSync = db_pgsql()
    assert conn.connected is True

    with open("tests/unittest/sql/postgresql/create.sql", "r") as f:
        type_, table, *_ = f.read().split(";")
        conn.execute(stmt=type_)
        conn.execute(stmt=table)

    with open("tests/unittest/sql/postgresql/insert.sql", "r") as f:
        insert = f.read().split(";")[0]
        conn.execute(stmt=insert)

    row = (conn.query(query="SELECT * FROM pysqlx_table"))[0]

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

    conn.execute(stmt="DROP TABLE pysqlx_table")
    conn.execute(stmt="DROP TYPE colors CASCADE")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query(query="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query(query="SELECT * FROM invalid_table", as_dict=True)

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_first(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query_first(query="SELECT * FROM invalid_table")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_invalid_query_first_as_dict(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(QueryError):
        conn.query_first(query="SELECT * FROM invalid_table", as_dict=True)

    conn.close()
    assert conn.connected is False
