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
