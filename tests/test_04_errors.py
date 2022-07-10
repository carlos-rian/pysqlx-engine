import pytest
from sqlx_engine import SQLXEngine
from sqlx_engine.errors import (
    AlreadyConnectedError,
    GenericSQLXEngineError,
    NotConnectedError,
)

from tests.common import get_all_dbs


def test_01_generic_sqlx_engine_error():
    error = GenericSQLXEngineError("error")
    assert error.name == "GenericSQLXEngineError"


def test_02_engine_raises_provider():
    with pytest.raises(ValueError):
        SQLXEngine(provider="test", uri=None)


def test_03_engine_raises_url():
    with pytest.raises(ValueError):
        SQLXEngine(provider="mysql", uri="test")


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_04_engine_raises_already_connected(name: str):
    db = get_all_dbs(name)
    db: SQLXEngine = await db()
    with pytest.raises(AlreadyConnectedError):
        await db.connect()

    await db.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_05_engine_raises_not_connected_error(name: str):
    db = get_all_dbs(name)
    db: SQLXEngine = await db()
    await db.close()
    with pytest.raises(NotConnectedError):
        await db.close()

    with pytest.raises(NotConnectedError):
        await db.execute("select 1")

    with pytest.raises(NotConnectedError):
        await db.query("select 1")
