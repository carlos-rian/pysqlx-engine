import time

import pytest

from pysqlx_engine import PySQLXEnginePoolSync as PySQLXEnginePool
from pysqlx_engine._core.errors import PoolClosedError


@pytest.fixture(scope="function")
def pool():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePool(uri=uri, min_size=3, check_interval=2)
	pool.start()
	return pool


def test_pool_initialization(pool: PySQLXEnginePool):
	assert pool._min_size == 3, "Min size should be 3"
	time.sleep(1)
	assert pool._opened is True
	with pool._lock:
		assert pool._pool.qsize() == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state
	pool.stop()


def test_get_connection_uses_all_min_connections(pool: PySQLXEnginePool):
	contexts = [pool.connection() for _ in range(3)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		context.__exit__(None, None, None)
	assert pool._pool.qsize() == 3, "All connections should be returned to the pool"
	pool.stop()


def test_return_connection_to_pool(pool: PySQLXEnginePool):
	pool._check_interval = 10
	with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() == 2, "Connection should be removed from the pool"
	assert pool._pool.qsize() == 3, "Connection should be returned to the pool"


def test_pool_stoped(pool: PySQLXEnginePool):
	pool.stop()

	with pytest.raises(PoolClosedError):
		with pool.connection() as _:
			...  # pragma: no cover


def test_reuse_connection():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePool(uri=uri, min_size=2, keep_alive=5)
	pool.start()
	contexts = [pool.connection() for _ in range(2)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	conn_ids = [id(conn) for conn in connections]
	for context in contexts:
		context.__exit__(None, None, None)

	# Connection should be renewed
	time.sleep(6)
	contexts = [pool.connection() for _ in range(2)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	new_conn_ids = [id(conn) for conn in connections]

	conn_ids.sort()
	new_conn_ids.sort()
	assert conn_ids == new_conn_ids, "Connections should be renewed"
	pool.stop()


def test_renew_connection():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePool(uri=uri, min_size=2, max_size=2, keep_alive=1, check_interval=1, conn_timeout=5)
	pool.start()
	contexts = [pool.connection() for _ in range(2)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	conn_ids = [id(conn) for conn in connections]
	for context in contexts:
		context.__exit__(None, None, None)

	# Connection should be renewed
	time.sleep(6)
	contexts = [pool.connection() for _ in range(2)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	new_conn_ids = [id(conn) for conn in connections]

	conn_ids.sort()
	new_conn_ids.sort()
	assert conn_ids != new_conn_ids, "Connections should be renewed"
	pool.stop()
