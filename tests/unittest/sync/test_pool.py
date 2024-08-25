from asyncio import sleep

import pytest

from pysqlx_engine import PySQLXEnginePoolSync


@pytest.fixture
def sync_pool():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePoolSync(uri=uri, min_size=3)
	sleep(1)
	yield pool
	pool.stop()


def test_sync_pool_initialization(sync_pool):
	assert sync_pool._min_size == 3, "Min size should be 3"
	assert sync_pool._opened is True
	with sync_pool._lock:
		assert len(sync_pool._pool) == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state


def test_sync_get_connection_uses_all_min_connections(sync_pool):
	contexts = [sync_pool.connection() for _ in range(3)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		context.__exit__(None, None, None)
	assert len(sync_pool._pool) == 3, "All connections should be returned to the pool"


def test_sync_return_connection_to_pool(sync_pool):
	with sync_pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert len(sync_pool._pool) == 2, "Connection should be removed from the pool"
	assert len(sync_pool._pool) == 3, "Connection should be returned to the pool"
