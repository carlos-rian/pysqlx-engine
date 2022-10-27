from os import environ

import pytest
from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.errors import ConnectError

@pytest.mark.asyncio
async def test_success_query_success():
    uri = environ["DATABASE_URI_POSTGRESQL"]
    engine = PySQLXEngine(uri=uri)
    await engine.connect()
    assert engine.is_connected() is True
    await engine.query("SELECT 1")
    await engine.close()
    assert engine.is_connected() is False