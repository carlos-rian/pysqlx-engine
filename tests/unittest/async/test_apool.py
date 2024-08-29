import asyncio

import pytest
import pytest_asyncio

from pysqlx_engine import PySQLXEnginePool
from pysqlx_engine._core.errors import PoolClosedError


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def pool():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePool(uri=uri, min_size=3)
	await pool.start()
	return pool


@pytest.mark.asyncio
async def test_pool_initialization(pool: PySQLXEnginePool):
	assert pool._min_size == 3, "Min size should be 3"
	await asyncio.sleep(1)
	assert pool._opened is True
	async with pool._lock:
		assert len(pool._pool) == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state
	await pool.stop()


@pytest.mark.asyncio
async def test_get_connection_uses_all_min_connections(pool: PySQLXEnginePool):
	contexts = [pool.connection() for _ in range(3)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		await context.__aexit__(None, None, None)
	assert len(pool._pool) == 3, "All connections should be returned to the pool"
	await pool.stop()


@pytest.mark.asyncio
async def test_return_connection_to_pool(pool: PySQLXEnginePool):
	async with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert len(pool._pool) == 2, "Connection should be removed from the pool"
	assert len(pool._pool) == 3, "Connection should be returned to the pool"


@pytest.mark.asyncio
async def test_pool_stoped(pool: PySQLXEnginePool):
	await pool.stop()

	with pytest.raises(PoolClosedError):
		async with pool.connection() as _:
			...  # pragma: no cover
