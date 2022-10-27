from os import environ

import pytest
from pysqlx_engine import PySQLXEngine
from pysqlx_engine.errors import ConnectError


@pytest.mark.asyncio
async def test_success_connect_success():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngine(uri=uri)
    await engine.connect()
    assert engine.is_connected() is True


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
async def test_success_is_healthy():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngine(uri=uri)
    await engine.connect()
    assert engine.is_healthy() is True


@pytest.mark.asyncio
async def test_success_requires_isolation_first():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngine(uri=uri)
    await engine.connect()
    assert engine.requires_isolation_first() is True


@pytest.mark.asyncio
async def test_success_close():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngine(uri=uri)
    await engine.connect()
    assert engine.is_connected() is True
    await engine.close()
    assert engine.is_connected() is False


@pytest.mark.asyncio
async def test_success_using_context_manager():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    async with PySQLXEngine(uri=uri) as engine:
        assert engine.is_connected() is True
        await engine.close()
        assert engine.is_connected() is False


@pytest.mark.asyncio
async def test_error_using_context_manager():
    uri = "postgresql://postgres:wrongPass@localhost:4442"
    with pytest.raises(ConnectError):
        async with PySQLXEngine(uri=uri):
            ...
