import os

import pytest

from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine._core.errors import ParameterInvalidProviderError, ParameterInvalidValueError
from pysqlx_engine._core.until import force_sync, pysqlx_get_error
from pysqlx_engine.errors import (
    AlreadyConnectedError,
    ConnectError,
    NotConnectedError,
    RawCmdError,
)
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite

from pysqlx_engine._core import param
from tests.unittest.sql.mysql.value import data


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


def test_invalid_convert_type_error_invalid_value():
    class MyType:
        i = 1

    with pytest.raises(ParameterInvalidValueError):
        param.convert(provider="postgresql", value=MyType(), field="invalid_type")


def test_invalid_convert_type_to_json_pgsql():
    class MyType:
        i = 1

    with pytest.raises(ParameterInvalidValueError):
        param.try_json(provider="postgresql", value=MyType(), field="invalid_type")


def test_valid_json_convert_type_mysql():
    value = param.try_json(provider="mysql", value=data, field="json")

    assert isinstance(value, str)
    assert value == (
        """\'{"type_int": 1, "type_smallint": 2, "type_bigint": 3, "type_numeric": 14.8389, "type_float": 13343400, """
        """"type_double": 1.6655444, "type_decimal": "19984", "type_char": "r", "type_varchar": "hfhfjjieurjnnd", """
        """"type_nvarchar": "$~k;dldëjdjd", "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf", """
        """"type_boolean": true, "type_date": "2022-01-01", "type_time": "12:10:11", "type_timestamp": """
        """"2022-12-20 08:59:55", "type_datetime": "2022-12-20 09:00:00", "type_enum": "black", """
        """"type_json": ["name", "age"], "type_bytes": "7375706572206279746573"}\'"""
    )
