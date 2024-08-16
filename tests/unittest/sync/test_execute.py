import pytest

from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine.errors import ExecuteError
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite


@pytest.mark.parametrize(
	"db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_execute_create_table(db, typ, create_table: dict):
	table = create_table.get(typ)

	conn: PySQLXEngineSync = db()

	assert conn.connected is True

	resp = conn.execute(sql=table)
	assert resp == 0

	resp = conn.execute(sql="DROP TABLE test_table;")
	assert resp == 0

	conn.close()
	assert conn.connected is False


@pytest.mark.parametrize(
	"db,typ", [(db_sqlite, "sqlite"), (db_pgsql, "pgsql"), (db_mssql, "mssql"), (db_mysql, "mysql")]
)
def test_execute_insert(db, typ, create_table: dict):
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

	resp = conn.execute(sql="DROP TABLE test_table;")
	assert isinstance(resp, int)

	conn.close()
	assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_error_execute_invalid_table_insert(db):
	conn: PySQLXEngineSync = db()
	assert conn.connected is True

	with pytest.raises(ExecuteError):
		conn.execute(sql="INSERT INTO invalid_table (id) VALUES (1)")

	conn.close()
	assert conn.connected is False


@pytest.mark.parametrize("db", [db_mysql])
def test_execute_sql_with_complex_param(db: PySQLXEngineSync):
	conn: PySQLXEngineSync = db()
	assert conn.connected is True

	from tests.unittest.sql.mysql.value import data
	from datetime import date, datetime, time
	from decimal import Decimal

	conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")

	with open("tests/unittest/sql/mysql/create.sql", "r") as f:
		sql = f.read()
		resp = conn.execute(sql=sql)
		assert resp == 0

	with open("tests/unittest/sql/mysql/insert.sql", "r") as f:
		sql = f.read()
		resp = conn.execute(sql=sql, parameters=data)
		assert resp == 1

	resp = conn.query_first(sql="SELECT * FROM pysqlx_table")

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

	resp = conn.execute(sql="DROP TABLE IF EXISTS pysqlx_table;")
	assert resp == 0
	conn.close()
