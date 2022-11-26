import pytest
from io import StringIO
from dotenv import load_dotenv
import os
from pysqlx_engine import PySQLXEnginePoolSync, PySQLXEngineSync
from pysqlx_engine.errors import PoolMaxConnectionsError


@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
def test_pool(environment: str):
    uri = os.environ[environment]
    pool = PySQLXEnginePoolSync(uri=uri, max_connections=3)

    conn1 = pool.new_connection()
    conn2 = pool.new_connection()
    conn3 = pool.new_connection()
    # multiple queries can be run in parallel
    results = [
        conn1.query_first("SELECT 1 AS one"),
        conn2.query_first("SELECT 2 AS two"),
        conn3.query_first("SELECT 3 AS three"),
    ]

    assert len(results) == 3
    assert results[0].one == 1
    assert results[1].two == 2
    assert results[2].three == 3

    with pytest.raises(PoolMaxConnectionsError):
        pool.new_connection()


def test_pool_error():
    env = StringIO(
        """
        DATABASE_URI_POSTGRESQL="postgresql://postgres:Build!Test321@localhost:4442/engine"
        PYSQLX_ERROR_COLORIZE=1
        PYSQLX_ERROR_JSON_FMT=1
        """
    )
    load_dotenv(stream=env, override=True)

    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    pool = PySQLXEnginePoolSync(uri=uri, max_connections=3)

    pool.new_connection()
    pool.new_connection()
    pool.new_connection()

    with pytest.raises(PoolMaxConnectionsError):
        pool.new_connection()


def test_pool_error_no_color_logs():
    env = StringIO(
        """
        DATABASE_URI_POSTGRESQL="postgresql://postgres:Build!Test321@localhost:4442/engine"
        PYSQLX_ERROR_COLORIZE=1
        PYSQLX_ERROR_JSON_FMT=1
        """
    )
    load_dotenv(stream=env, override=True)

    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    pool = PySQLXEnginePoolSync(uri=uri, max_connections=3)

    pool.new_connection()
    pool.new_connection()
    pool.new_connection()

    with pytest.raises(PoolMaxConnectionsError):
        pool.new_connection()


@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
def test_pool_using_context(environment: str):
    uri = os.environ[environment]
    pool = PySQLXEnginePoolSync(uri=uri, max_connections=3)

    with pool as conn:
        assert conn.connected is True
        assert isinstance(conn, PySQLXEngineSync)
