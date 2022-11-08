import pytest

from pysqlx_engine import PySQLXEngine
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
