import os
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from uuid import UUID

import pytest

from pysqlx_engine import PySQLXEngineSync, types
from pysqlx_engine._core import param, param_converter
from pysqlx_engine._core.const import LOG_CONFIG
from pysqlx_engine._core.errors import (
    ParameterInvalidJsonValueError,
    ParameterInvalidValueError,
)
from pysqlx_engine._core.util import force_sync, pysqlx_get_error
from pysqlx_engine.errors import (
    AlreadyConnectedError,
    ConnectError,
    NotConnectedError,
    RawCmdError,
)
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite
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
        param_converter.convert(provider="postgresql", value=MyType(), field="invalid_type")


def test_invalid_convert_type_to_json_pgsql():
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = False
    LOG_CONFIG.PYSQLX_USE_COLOR = False
    LOG_CONFIG.PYSQLX_SQL_LOG = False

    class MyType:
        i = 1

    with pytest.raises(ParameterInvalidJsonValueError):
        param.try_json("postgresql", MyType(), "invalid_type")

    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True

    with pytest.raises(ParameterInvalidJsonValueError):
        param.try_json("postgresql", MyType(), "invalid_type")


def test_valid_json_convert_type_mysql():
    value = param.try_json("mysql", data, "json")

    assert isinstance(value, str)
    assert value == (
        """\'{"type_int": 1, "type_smallint": 2, "type_bigint": 3, "type_numeric": 14.8389, "type_float": 13343400, """
        """"type_double": 1.6655444, "type_decimal": "19984", "type_char": "r", "type_varchar": "hfhfjjieurjnnd", """
        """"type_nvarchar": "$~k;dldëjdjd", "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf", """
        """"type_boolean": true, "type_date": "2022-01-01", "type_time": "12:10:11", "type_timestamp": """
        """"2022-12-20 08:59:55", "type_datetime": "2022-12-20 09:00:00", "type_enum": "black", """
        """"type_json": ["name", "age"], "type_bytes": "7375706572206279746573"}\'"""
    )


def test_class_types_sql_server():
    provider: str = "sqlserver"
    assert param_converter.convert(provider=provider, value=types.BooleanType(True), field="xpto") == "1"
    assert param_converter.convert(provider=provider, value=types.StringType("string"), field="xpto") == "'string'"
    assert (
        param_converter.convert(provider=provider, value=types.NStringType("жизнь,حياة,生活,❤️😒😁"), field="xpto")
        == "N'жизнь,حياة,生活,❤️😒😁'"
    )
    assert param_converter.convert(provider=provider, value=types.IntegerType(12345), field="xpto") == 12345
    assert (
        param_converter.convert(provider=provider, value=types.JsonType({"name": "John", "age": 30}), field="xpto")
        == '\'{"name": "John", "age": 30}\''
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.NJsonType({"name": "жизнь,حياة,生活,❤️😒😁", "age": 30}), field="xpto"
        )
        == 'N\'{"name": "жизнь,حياة,生活,❤️😒😁", "age": 30}\''
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.UUIDType(UUID("550e8400-e29b-41d4-a716-446655440000")), field="xpto"
        )
        == "'550e8400-e29b-41d4-a716-446655440000'"
    )
    assert (
        param_converter.convert(provider=provider, value=types.TimeType(time(12, 10, 11)), field="xpto") == "'12:10:11'"
    )
    assert (
        param_converter.convert(provider=provider, value=types.DateType(date(2022, 1, 1)), field="xpto")
        == "'2022-01-01'"
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.DateTimeType(datetime(2022, 12, 20, 9, 0, 0)), field="xpto"
        )
        == "'2022-12-20T09:00:00.000'"
    )
    assert param_converter.convert(provider=provider, value=types.FloatType(1.6655444), field="xpto") == 1.6655444
    assert (
        param_converter.convert(provider=provider, value=types.BytesType(b"super bytes"), field="xpto")
        == "0x7375706572206279746573"
    )

    class Enum2(Enum):
        black = "black"
        white = "white"

    assert (
        param_converter.convert(provider=provider, value=types.DecimalType(Decimal("19984")), field="xpto") == "'19984'"
    )
    assert param_converter.convert(provider=provider, value=types.EnumType(Enum2("black")), field="xpto") == "'black'"


@pytest.mark.parametrize("provider", ["postgresql", "mysql", "sqlite"])
def test_class_types_parametrize(provider):
    assert param_converter.convert(provider=provider, value=types.BooleanType(True), field="xpto") in ("TRUE", "1")
    assert param_converter.convert(provider=provider, value=types.StringType("string"), field="xpto") == "'string'"
    assert (
        param_converter.convert(provider=provider, value=types.NStringType("жизнь,حياة,生活,❤️😒😁"), field="xpto")
        == "'жизнь,حياة,生活,❤️😒😁'"
    )
    assert param_converter.convert(provider=provider, value=types.IntegerType(12345), field="xpto") == 12345
    assert (
        param_converter.convert(provider=provider, value=types.JsonType({"name": "John", "age": 30}), field="xpto")
        == '\'{"name": "John", "age": 30}\''
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.NJsonType({"name": "жизнь,حياة,生活,❤️😒😁", "age": 30}), field="xpto"
        )
        == '\'{"name": "жизнь,حياة,生活,❤️😒😁", "age": 30}\''
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.UUIDType(UUID("550e8400-e29b-41d4-a716-446655440000")), field="xpto"
        )
        == "'550e8400-e29b-41d4-a716-446655440000'"
    )
    assert (
        param_converter.convert(provider=provider, value=types.TimeType(time(12, 10, 11)), field="xpto") == "'12:10:11'"
    )
    assert (
        param_converter.convert(provider=provider, value=types.DateType(date(2022, 1, 1)), field="xpto")
        == "'2022-01-01'"
    )
    assert (
        param_converter.convert(
            provider=provider, value=types.DateTimeType(datetime(2022, 12, 20, 9, 0, 0)), field="xpto"
        )
        == "'2022-12-20 09:00:00'"
    )
    assert param_converter.convert(provider=provider, value=types.FloatType(1.6655444), field="xpto") == 1.6655444
    assert param_converter.convert(provider=provider, value=types.BytesType(b"super bytes"), field="xpto") in (
        "0x7375706572206279746573",
        "x'7375706572206279746573'",
        "X'7375706572206279746573'",
        "'\\x7375706572206279746573'",
    )

    class Enum2(Enum):
        black = "black"
        white = "white"

    assert (
        param_converter.convert(provider=provider, value=types.DecimalType(Decimal("19984")), field="xpto") == "'19984'"
    )
    assert param_converter.convert(provider=provider, value=types.EnumType(Enum2("black")), field="xpto") == "'black'"


def test_class_types_postgresql():
    provider: str = "postgresql"

    class Enum2(Enum):
        black = "black"
        white = "white"

    assert param_converter.convert(provider=provider, value=types.TupleType((1, 2, 3)), field="xpto") == "'{1, 2, 3}'"
    assert param_converter.convert(provider=provider, value=types.NTupleType((1, 2, 3)), field="xpto") == "'{1, 2, 3}'"

    assert (
        param_converter.convert(
            provider=provider, value=types.TupleEnumType((Enum2("black"), Enum2("white"))), field="xpto"
        )
        == "'{black,white}'"
    )
