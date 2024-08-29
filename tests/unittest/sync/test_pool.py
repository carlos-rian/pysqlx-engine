import pytest

from pysqlx_engine import PySQLXEnginePoolSync
from pysqlx_engine._core.errors import PoolClosedError


@pytest.fixture(scope="function", autouse=False)
def sync_pool():
	uri = "sqlite:./dev.db"  # SQLite database URI for testing
	pool = PySQLXEnginePoolSync(uri=uri, min_size=3)
	pool.start()
	return pool


def test_sync_pool_initialization(sync_pool: PySQLXEnginePoolSync):
	assert sync_pool._min_size == 3, "Min size should be 3"
	assert sync_pool._opened is True
	assert len(sync_pool._pool) == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state
	sync_pool.stop()


def test_sync_get_connection_uses_all_min_connections(sync_pool: PySQLXEnginePoolSync):
	contexts = [sync_pool.connection() for _ in range(3)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		context.__exit__(None, None, None)
	assert len(sync_pool._pool) == 3, "All connections should be returned to the pool"
	sync_pool.stop()


def test_sync_return_connection_to_pool(sync_pool: PySQLXEnginePoolSync):
	with sync_pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert len(sync_pool._pool) == 2, "Connection should be removed from the pool"
	assert len(sync_pool._pool) == 3, "Connection should be returned to the pool"
	sync_pool.stop()


def test_pool_stoped(sync_pool: PySQLXEnginePoolSync):
	sync_pool.stop()

	with pytest.raises(PoolClosedError):
		with sync_pool.connection() as _:
			...  # pragma: no cover
