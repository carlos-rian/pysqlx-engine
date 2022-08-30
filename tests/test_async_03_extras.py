import os
import subprocess

import pytest
from sqlx_engine import SQLXEngine
from sqlx_engine._core.aengine import AsyncEngine
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
from sqlx_engine.types import BaseRow  # noqa

from tests.common import get_all_adbs, get_all_dbs


def test_01_generic_sqlx_engine_error():
    error = GenericSQLXEngineError("error")
    assert error.name == "GenericSQLXEngineError"


def test_02_aengine_raises_provider():
    with pytest.raises(ValueError):
        SQLXEngine(provider="test", uri=None)


def test_03_aengine_raises_url():
    with pytest.raises(ValueError):
        SQLXEngine(provider="mysql", uri="test")


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_04_aengine_raises_already_connected(name: str):
    db = get_all_adbs(name)
    db: SQLXEngine = await db()
    with pytest.raises(AlreadyConnectedError):
        await db.connect()

    await db.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_05_aengine_raises_not_connected_error(name: str):
    db = get_all_adbs(name)
    db: SQLXEngine = await db()
    await db.close()
    with pytest.raises(NotConnectedError):
        await db.close()

    with pytest.raises(NotConnectedError):
        await db.execute("select 1")

    with pytest.raises(NotConnectedError):
        await db.query("select 1")


@pytest.mark.asyncio
async def test_06_aengine_raises_already_connected_error_sqlite():
    aengine = AsyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    await aengine.connect()
    with pytest.raises(AlreadyConnectedError):
        await aengine.connect()


@pytest.mark.asyncio
async def test_07_aengine_raises_not_connected_error_sqlite():
    aengine = AsyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    await aengine.connect()
    await aengine.disconnect()
    with pytest.raises(NotConnectedError):
        await aengine.disconnect()


@pytest.mark.asyncio
async def test_08_aengine_request_raises_not_connected_error_sqlite():
    aengine = AsyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    await aengine.connect()
    await aengine.disconnect()
    with pytest.raises(NotConnectedError):
        await aengine.request(method="GET", path="/status")


@pytest.mark.asyncio
async def test_09_aengine_raises_not_connected_error_sqlite():
    aengine = AsyncEngine(
        db_uri="postgresql://postgres:WrongPass@localhost:4442/engine",
        db_provider="postgresql",
    )
    with pytest.raises(StartEngineError):
        await aengine.connect()

    aengine.process = subprocess.Popen(
        ["echo", "''"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    with pytest.raises(BaseStartEngineError):
        await aengine._try_comunicate()

    aengine.process = subprocess.Popen(
        ["sleep", "30"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    with pytest.raises(EngineConnectionError):
        await aengine._check_connect()


@pytest.mark.asyncio
async def test_10_aengine_engine_request_error_sqlite():
    aengine = AsyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    await aengine.connect()
    with pytest.raises(EngineRequestError):
        await aengine.request(method="POST", path="/", content="invalid body")


@pytest.mark.asyncio
async def test_11_aengine_handler_error_sqlite():
    aengine = SQLXEngine(uri=os.getenv("DATABASE_URI_SQLITE"), provider="sqlite")
    await aengine.connect()
    with pytest.raises(RawQueryError):
        await aengine.query(query="invalid query")


def test_12_aengine_handler_error_not_mapping_sqlite():
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


def test_13_aengine_handler_error_not_mapping_generic_sqlite():
    errors = []
    with pytest.raises(GenericSQLXEngineError):
        handler_error(errors=errors)


@pytest.mark.asyncio
async def test_14_aengine_auto_close_connection():
    aengine = AsyncEngine(db_uri=os.getenv("DATABASE_URI_SQLITE"), db_provider="sqlite")
    await aengine.connect()

    aengine.__del__()

    assert aengine.url is None
    assert aengine.connected == False
    assert aengine.session is None
    assert aengine.process is None


@pytest.mark.asyncio
async def test_14_aengine_connect_timeout_none():
    aengine = SQLXEngine(uri=os.getenv("DATABASE_URI_SQLITE"), provider="sqlite")

    with pytest.raises(ValueError):
        await aengine.connect(timeout=None)


@pytest.mark.asyncio
async def test_15_aengine_using_async_with():
    async with SQLXEngine(provider="sqlite", uri="file:./dev.db") as db:
        query = "SELECT * FROM test_table"
        resp = await db.query(query)
        assert resp is not None


@pytest.mark.asyncio
async def test_16_aengine_timeout_error():
    db = SQLXEngine(provider="sqlite", uri="file:./dev.db")
    await db.connect()
    db._connection.session.timeout = 0.00001
    with pytest.raises(SQLXEngineTimeoutError):
        query = "SELECT * FROM test_table"
        await db.query(query)
    await db.close()
    #
    db = SQLXEngine(provider="sqlite", uri="file:./dev.db")
    await db.connect()
    db._connection.session.timeout = 0.00001
    with pytest.raises(SQLXEngineTimeoutError):
        query = "SELECT * FROM test_table"
        await db.execute(query)
    await db.close()
