from os import environ

import pytest
from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine.errors import ConnectError


def test_success_connect_success():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngineSync(uri=uri)
    engine.connect()
    assert engine.is_connected() is True


def test_error_connect_with_wrong_driver():
    with pytest.raises(ValueError):
        PySQLXEngineSync(uri="postgres://wrong_host:5432")


def test_error_connect_with_wrong_password():
    with pytest.raises(ConnectError):
        db = PySQLXEngineSync(uri="postgresql://postgres:wrongPass@localhost:4442")
        db.connect()


def test_success_is_healthy():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngineSync(uri=uri)
    engine.connect()
    assert engine.is_healthy() is True


def test_success_requires_isolation_first():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngineSync(uri=uri)
    engine.connect()
    assert engine.requires_isolation_first() is True


def test_success_close():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngineSync(uri=uri)
    engine.connect()
    assert engine.is_connected() is True
    engine.close()
    assert engine.is_connected() is False


def test_success_using_context_manager():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    with PySQLXEngineSync(uri=uri) as engine:
        assert engine.is_connected() is True
        engine.close()
        assert engine.is_connected() is False


def test_error_using_context_manager():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        with PySQLXEngineSync(uri=uri):
            ...
