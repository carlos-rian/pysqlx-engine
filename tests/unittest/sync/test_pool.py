import queue
import threading
import time
import unittest.mock

import pytest

from pysqlx_engine import PySQLXEnginePoolSync as PySQLXEnginePool
from pysqlx_engine._core.errors import (
	PoolAlreadyClosedError,
	PoolAlreadyStartedError,
	PoolClosedError,
	PoolTimeoutError,
)
from pysqlx_engine._core.pool.pool import Monitor
from tests.common import MSSQL_URI, MYSQL_URI, PGSQL_URI, SQLITE_URI


def get_pool(uri: str, min_size=3, check_interval=1, keep_alive=60 * 15, **kwargs):
	pool = PySQLXEnginePool(uri=uri, min_size=min_size, check_interval=check_interval, keep_alive=keep_alive, **kwargs)
	pool.start()
	return pool


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_pool_initialization(uri: str):
	pool = get_pool(uri=uri, check_interval=10)
	assert pool._min_size == 3, "Min size should be 3"
	time.sleep(1)
	assert pool._opened is True
	with pool._lock:
		assert pool._pool.qsize() == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state
	pool.stop()


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_get_connection_uses_all_min_connections(uri: str):
	pool = get_pool(uri=uri)
	contexts = [pool.connection() for _ in range(3)]
	connections = [ctx.__enter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		context.__exit__(None, None, None)
	assert pool._pool.qsize() == 3, "All connections should be returned to the pool"
	pool.stop()


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_return_connection_to_pool(uri: str):
	pool = get_pool(uri=uri, check_interval=10)
	time.sleep(1)
	with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 3, "Connection should be removed from the pool"
	assert pool._pool.qsize() == 3, "Connection should be returned to the pool"
	pool.stop()


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_pool_stoped(uri: str):
	pool = get_pool(uri=uri)
	pool.stop()

	with pytest.raises(PoolClosedError):
		with pool.connection() as _:
			...  # pragma: no cover


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_reuse_connection(uri: str):
	pool = get_pool(uri=uri, min_size=2, keep_alive=5)
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


@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
def test_renew_connection(uri: str):
	pool = get_pool(uri=uri, min_size=2, max_size=2, keep_alive=1, check_interval=1, conn_timeout=5)
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


def test_pool_initialization_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, max_size=None, min_size=10)
	assert pool._max_size == 10, "Max size should be 10"
	assert pool._min_size == 10, "Min size should be 10"
	assert "at 0x" in repr(pool)

	with pytest.raises(ValueError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=0)

	with pytest.raises(ValueError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=-1)

	with pytest.raises(ValueError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=10, max_size=5)

	with pytest.raises(AssertionError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, conn_timeout=0)

	with pytest.raises(AssertionError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, keep_alive=0)

	with pytest.raises(AssertionError):
		pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, check_interval=0)


def test_monitor_break_if_queue_is_empty():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool._opened = True
	with unittest.mock.patch.object(pool._pool, "get_nowait", side_effect=queue.Empty):
		monitor = Monitor(pool=pool)
		assert pool._name in repr(monitor)
		pool._pool.put_nowait("test")
		t = threading.Thread(target=monitor.run, daemon=True)
		t.start()
		time.sleep(1)
		pool._opened = False
		t.join()


def test_monitor_break_if_size_is_above_max():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool._opened = True
	pool._pool.put_nowait(pool._new_conn_unchecked())
	assert pool._size == 1
	assert pool._opened is True

	monitor = Monitor(pool=pool)
	pool._size = 2
	t = threading.Thread(target=monitor.run, daemon=True)
	t.start()
	time.sleep(1)
	pool._opened = False
	t.join()


def test_pool_stop_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	with pytest.raises(PoolAlreadyClosedError):
		pool.stop()


def test_pool_timeout_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1, conn_timeout=1)
	pool.start()
	time.sleep(1)
	with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
		with pytest.raises(PoolTimeoutError):
			with pool.connection() as _:
				...  # pragma: no cover
	pool.stop()


def test_pool_raise_during_connection():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool.start()
	time.sleep(1)
	with pytest.raises(ZeroDivisionError):
		with pool.connection() as conn:
			assert conn is not None, "Connection should not be None"
			assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
			1 / 0

	pool.stop()


def test_pool_on_transaction():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1, check_interval=10)
	pool.start()
	time.sleep(1)
	with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
		conn.start_transaction()
	pool._pool.qsize() == 0
	pool.stop()


def test_pool_start_twice():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool.start()
	with pytest.raises(PoolAlreadyStartedError):
		pool.start()
	pool.stop()


def test_pool_start_generate_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	with unittest.mock.patch.object(pool._pool, "put", side_effect=Exception):
		with pytest.raises(Exception):
			pool.start()


def test_pool_get_conn():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool.start()
	with unittest.mock.patch.object(pool._semaphore, "acquire", return_value=None):
		with pytest.raises(PoolTimeoutError) as e:
			pool._get_conn()
	assert "Timeout waiting for a connection semaphore" in str(e.value)
	pool.stop()


def test_pool_get_ready_conn():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool.start()
	with unittest.mock.patch.object(pool._pool, "get", side_effect=queue.Empty):
		assert pool._get_ready_conn() is None

	pool.stop()


def test_pool_put_conn_unchecked_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1, check_interval=10)
	pool.start()
	time.sleep(1)
	pool._max_size = 10
	conn = pool._new_conn_unchecked()
	pool._put_conn(conn)

	pool.stop()
