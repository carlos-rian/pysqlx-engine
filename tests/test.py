import asyncio
import logging

from pysqlx_engine._core.pool._apool import PySQLXEnginePool

logging.basicConfig(level=logging.DEBUG)


async def setup_engine_pool():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePool(uri=uri, min_size=3)
	while pool._opened is False:
		await asyncio.sleep(1)

	return pool


async def test_pool_initialization(pool):
	assert pool._min_size == 3, "Min size should be 3"
	# Additional assertions can be made here regarding the pool's initial state


async def test_get_connection_uses_all_min_connections(pool):
	contexts = [pool.connection() for _ in range(3)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		await context.__aexit__(None, None, None)
	assert len(pool._pool) == 3, "All connections should be returned to the pool"


async def test_return_connection_to_pool(pool):
	async with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert len(pool._pool) == 2, "Connection should be removed from the pool"
	assert len(pool._pool) == 3, "Connection should be returned to the pool"


async def run_tests():
	pool = await setup_engine_pool()
	await test_pool_initialization(pool)
	await test_get_connection_uses_all_min_connections(pool)
	await test_return_connection_to_pool(pool)
	print("All tests passed!")


# Running the test suite
# loop = asyncio.get_event_loop()
# loop.run_until_complete(run_tests())
