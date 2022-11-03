import os

import pytest

from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine._core.until import force_sync, pysqlx_get_error
from pysqlx_engine.errors import (
    AlreadyConnectedError,
    ConnectError,
    NotConnectedError,
    RawCmdError,
)
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_connect_success(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True


def test_error_connect_with_wrong_driver():
    with pytest.raises(ValueError):
        PySQLXEngineSync(uri="postgres://wrong_host:5432")


def test_error_connect_with_wrong_password():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        db = PySQLXEngineSync(uri=uri)
        db.connect()


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_is_healthy(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.is_healthy() is True


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql])
def test_requires_isolation_first_equal_false(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.requires_isolation_first() is False


@pytest.mark.parametrize("db", [db_mssql, db_mysql])
def test_requires_isolation_first_equal_true(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.requires_isolation_first() is True


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_query_success(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    conn.query("SELECT 1 AS number")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
def test_using_context_manager(environment: str):
    uri = os.environ[environment]
    with PySQLXEngineSync(uri=uri) as conn:
        assert conn.connected is True
    assert conn.connected is False


def test_error_using_context_manager():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        with PySQLXEngineSync(uri=uri):
            ...  # pragma: no cover


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_delete_default_connection(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    conn.__del__()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_connection_already_exists_error(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    with pytest.raises(AlreadyConnectedError):
        conn.connect()


@pytest.mark.parametrize(
    "environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
def test_connection_not_connected_error(environment: str):
    uri = os.environ[environment]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri=uri)
    assert conn.connected is False

    with pytest.raises(NotConnectedError):
        conn.query("SELECT 1 AS number")


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_execute_raw_cmd_error(db: PySQLXEngineSync):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    with pytest.raises(RawCmdError):
        conn.raw_cmd("wrong_cmd = 1")

    conn.close()
    assert conn.connected is False


def test_pysqlx_get_error_default():
    class GenericError(Exception):
        def error(self):
            return "generic"

    error = pysqlx_get_error(err=GenericError())
    assert isinstance(error, GenericError)


def test_force_sync():
    @force_sync
    def sync_func():
        return 1

    assert sync_func() == 1
