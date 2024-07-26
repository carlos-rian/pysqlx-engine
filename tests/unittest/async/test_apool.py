import asyncio
import pytest
from pysqlx_engine._core.const import LOG_CONFIG
import os
from pysqlx_engine import PySQLXEnginePool, PySQLXEngine
from pysqlx_engine.errors import PoolMaxConnectionsError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
async def test_apool(environment: str):
    uri = os.environ[environment]
    pool = PySQLXEnginePool(uri=uri, max_connections=3)

    conn1 = await pool.new_connection()
    conn2 = await pool.new_connection()
    conn3 = await pool.new_connection()
    # multiple queries can be run in parallel
    coro = [
        conn1.query_first("SELECT 1 AS one"),
        conn2.query_first("SELECT 2 AS two"),
        conn3.query_first("SELECT 3 AS three"),
    ]
    # wait for all queries to finish
    results = await asyncio.gather(*coro)

    assert len(results) == 3
    assert results[0].one == 1
    assert results[1].two == 2
    assert results[2].three == 3

    with pytest.raises(PoolMaxConnectionsError):
        await pool.new_connection()


@pytest.mark.asyncio
async def test_apool_error():
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    uri = "postgresql://postgres:Build!Test321@localhost:4442/engine"
    pool = PySQLXEnginePool(uri=uri, max_connections=3)

    await pool.new_connection()
    await pool.new_connection()
    await pool.new_connection()

    with pytest.raises(PoolMaxConnectionsError):
        await pool.new_connection()


@pytest.mark.asyncio
async def test_apool_error_no_color_logs():
    LOG_CONFIG.PYSQLX_USE_COLOR = False
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = False

    uri = "postgresql://postgres:Build!Test321@localhost:4442/engine"
    pool = PySQLXEnginePool(uri=uri, max_connections=3)

    await pool.new_connection()
    await pool.new_connection()
    await pool.new_connection()

    with pytest.raises(PoolMaxConnectionsError):
        await pool.new_connection()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
async def test_apool_using_context(environment: str):
    uri = os.environ[environment]
    pool = PySQLXEnginePool(uri=uri, max_connections=3)

    async with pool as conn:
        assert conn.connected is True
        assert isinstance(conn, PySQLXEngine)
