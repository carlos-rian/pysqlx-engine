import os
from os import environ

import pytest
from pysqlx_engine import PySQLXEngine
from pysqlx_engine.errors import AlreadyConnectedError, ConnectError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_connect_success(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True


@pytest.mark.asyncio
async def test_error_connect_with_wrong_driver():
    with pytest.raises(ValueError):
        PySQLXEngine(uri="postgres://wrong_host:5432")


@pytest.mark.asyncio
async def test_error_connect_with_wrong_password():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        db = PySQLXEngine(uri=uri)
        await db.connect()


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_is_healthy(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.is_healthy() is True


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_requires_isolation_first(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.requires_isolation_first() is True


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_success_query_success(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    await conn.query("SELECT 1 AS number")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "uri",
    [
        os.environ["DATABASE_URI_SQLITE"],
        os.environ["DATABASE_URI_POSTGRESQL"],
        os.environ["DATABASE_URI_MSSQL"],
        os.environ["DATABASE_URI_MYSQL"],
    ],
)
async def test_success_using_context_manager(uri: str):
    async with PySQLXEngine(uri=uri) as conn:
        assert conn.connect is True
    assert conn.connected is False


@pytest.mark.asyncio
async def test_error_using_context_manager():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        async with PySQLXEngine(uri=uri):
            ...


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_delete_default_connection(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    conn.__del__()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_connection_already_exists_error(db: PySQLXEngine):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    with pytest.raises(AlreadyConnectedError):
        await conn.connect()
