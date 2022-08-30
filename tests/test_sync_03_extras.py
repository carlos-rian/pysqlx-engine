import os
import subprocess

import pytest
from sqlx_engine import SQLXEngineSync
from sqlx_engine._core.engine import SyncEngine
from sqlx_engine._core.errors import (
    BaseStartEngineError,
    EngineConnectionError,
    EngineRequestError,
    SQLXEngineTimeoutError,
    StartEngineError,
    handler_error,
)
from sqlx_engine.errors import (
    AlreadyConnectedError,
    GenericSQLXEngineError,
    NotConnectedError,
    RawQueryError,
    SQLXEngineError,
)

from tests.common import get_all_dbs


def test_01_generic_sqlx_engine_error():
    error = GenericSQLXEngineError("error")
    assert error.name == "GenericSQLXEngineError"


def test_02_engine_raises_provider():
    with pytest.raises(ValueError):
        SQLXEngineSync(provider="test", uri=None)


def test_03_engine_raises_url():
    with pytest.raises(ValueError):
        SQLXEngineSync(provider="mysql", uri="test")


@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
def test_04_engine_raises_already_connected(name: str):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    with pytest.raises(AlreadyConnectedError):
        db.connect()

    db.close()


@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
def test_05_engine_raises_not_connected_error(name: str):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    db.close()
    with pytest.raises(NotConnectedError):
        db.close()

    with pytest.raises(NotConnectedError):
        db.execute("select 1")

    with pytest.raises(NotConnectedError):
        db.query("select 1")


def test_06_engine_raises_already_connected_error_sqlite():
    engine = SyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    engine.connect()
    with pytest.raises(AlreadyConnectedError):
        engine.connect()


def test_07_engine_raises_not_connected_error_sqlite():
    engine = SyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    engine.connect()
    engine.disconnect()
    with pytest.raises(NotConnectedError):
        engine.disconnect()


def test_08_engine_request_raises_not_connected_error_sqlite():
    engine = SyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    engine.connect()
    engine.disconnect()
    with pytest.raises(NotConnectedError):
        engine.request(method="GET", path="/status")


def test_09_engine_raises_not_connected_error_sqlite():
    engine = SyncEngine(
        db_uri="postgresql://postgres:WrongPass@localhost:4442/engine",
        db_provider="postgresql",
    )
    with pytest.raises(StartEngineError):
        engine.connect()

    engine.process = subprocess.Popen(
        ["echo", "''"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    with pytest.raises(BaseStartEngineError):
        engine._try_comunicate()

    engine.process = subprocess.Popen(
        ["sleep", "30"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    with pytest.raises(EngineConnectionError):
        engine._check_connect()


def test_10_engine_engine_request_error_sqlite():
    engine = SyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    engine.connect()
    with pytest.raises(EngineRequestError):
        engine.request(method="POST", path="/", content="invalid body")


def test_11_engine_handler_error_sqlite():
    engine = SQLXEngineSync(uri=os.getenv("DATABASE_URI_SQLITE"), provider="sqlite")
    engine.connect()
    with pytest.raises(RawQueryError):
        engine.query(query="invalid query")


def test_12_engine_handler_error_not_mapping_sqlite():
    errors = [
        {
            "error": "generic",
            "user_farcing": {
                "is_panic": False,
                "message": "Raw query failed. Co...tax error`",
                "meta": {"code": "1", "message": 'near "invalid": syntax error'},
                "error_code": "",
            },
        }
    ]
    with pytest.raises(SQLXEngineError):
        handler_error(errors=errors)


def test_13_engine_handler_error_not_mapping_generic_sqlite():
    errors = []
    with pytest.raises(GenericSQLXEngineError):
        handler_error(errors=errors)


def test_14_engine_auto_close_connection():
    engine = engine = SyncEngine(
        db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite"
    )
    engine.connect()

    engine.__del__()

    assert engine.url is None
    assert engine.connected == False
    assert engine.session is None
    assert engine.process is None


def test_14_engine_connect_timeout_none():
    engine = SQLXEngineSync(uri=os.getenv("DATABASE_URI_SQLITE"), provider="sqlite")

    with pytest.raises(ValueError):
        engine.connect(timeout=None)


def test_15_engine_using_async_with():
    with SQLXEngineSync(provider="sqlite", uri="file:./dev.db") as db:
        query = "SELECT * FROM test_table"
        resp = db.query(query)
        assert resp is not None


def test_16_engine_timeout_error():
    db = SQLXEngineSync(provider="sqlite", uri="file:./dev.db")
    db.connect()
    db._connection.session.timeout = 0.001
    with pytest.raises(SQLXEngineTimeoutError):
        query = "SELECT * FROM test_table"
        db.query(query)

    with pytest.raises(SQLXEngineTimeoutError):
        query = "SELECT * FROM test_table"
        db.execute(query)
