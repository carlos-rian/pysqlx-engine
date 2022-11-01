from os import environ

import pytest
import pytest_asyncio
from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.errors import ConnectError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_query_success(db):
    conn = await db()
    await conn.connect()
    assert conn.connected is True

    await conn.query("SELECT 1")
    await conn.close()
    assert conn.connected is False
