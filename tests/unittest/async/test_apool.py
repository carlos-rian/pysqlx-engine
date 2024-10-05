import asyncio
import unittest.mock

import pytest

from pysqlx_engine import PySQLXEnginePool
from pysqlx_engine._core.errors import (
	PoolAlreadyClosedError,
	PoolAlreadyStartedError,
	PoolClosedError,
	PoolTimeoutError,
)
from pysqlx_engine._core.pool.apool import Monitor
from tests.common import MSSQL_URI, MYSQL_URI, PGSQL_URI, SQLITE_URI


async def get_pool(uri: str, min_size=3, check_interval=1, keep_alive=60 * 15, **kwargs):
	pool = PySQLXEnginePool(uri=uri, min_size=min_size, check_interval=check_interval, keep_alive=keep_alive, **kwargs)
	await pool.start()
	return pool


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_pool_initialization(uri: str):
	pool = await get_pool(uri, check_interval=10)
	assert pool._min_size == 3, "Min size should be 3"
	await asyncio.sleep(1)
	assert pool._opened is True
	async with pool._lock:
		assert pool._pool.qsize() == 3, "Pool should have 3 connections"
	# Additional assertions can be made here regarding the pool's initial state
	await pool.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_get_connection_uses_all_min_connections(uri: str):
	pool = await get_pool(uri)
	contexts = [pool.connection() for _ in range(3)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 3, "Should use all min connections"
	for context in contexts:
		await context.__aexit__(None, None, None)
	assert pool._pool.qsize() == 3, "All connections should be returned to the pool"
	await pool.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_return_connection_to_pool(uri: str):
	pool = await get_pool(uri=uri, check_interval=10)
	await asyncio.sleep(1)
	async with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 3, "Connection should be removed from the pool"
	assert pool._pool.qsize() == 3, "Connection should be returned to the pool"
	await pool.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_pool_stoped(uri: str):
	pool = await get_pool(uri=uri)
	await pool.stop()

	with pytest.raises(PoolClosedError):
		async with pool.connection() as _:
			...  # pragma: no cover


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_reuse_connection(uri: str):
	pool = await get_pool(uri=uri, min_size=2, keep_alive=5)
	contexts = [pool.connection() for _ in range(2)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	conn_ids = [id(conn) for conn in connections]
	for context in contexts:
		await context.__aexit__(None, None, None)

	# Connection should be renewed
	await asyncio.sleep(6)
	contexts = [pool.connection() for _ in range(2)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	new_conn_ids = [id(conn) for conn in connections]

	conn_ids.sort()
	new_conn_ids.sort()
	assert conn_ids == new_conn_ids, "Connections should be renewed"
	await pool.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("uri", [SQLITE_URI, PGSQL_URI, MSSQL_URI, MYSQL_URI])
async def test_renew_connection(uri: str):
	pool = await get_pool(uri=uri, min_size=2, max_size=2, keep_alive=1, check_interval=1, conn_timeout=5)
	contexts = [pool.connection() for _ in range(2)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	conn_ids = [id(conn) for conn in connections]
	for context in contexts:
		await context.__aexit__(None, None, None)

	# Connection should be renewed
	await asyncio.sleep(6)
	contexts = [pool.connection() for _ in range(2)]
	connections = [await ctx.__aenter__() for ctx in contexts]
	assert len(connections) == 2, "Should use all min connections"
	assert pool._size == 2, "Should have 2 connections"
	new_conn_ids = [id(conn) for conn in connections]

	conn_ids.sort()
	new_conn_ids.sort()
	assert conn_ids != new_conn_ids, "Connections should be renewed"
	await pool.stop()


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


@pytest.mark.asyncio
async def test_monitor_break_if_queue_is_empty():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool._opened = True
	with unittest.mock.patch.object(pool._pool, "get_nowait", side_effect=asyncio.QueueEmpty):
		monitor = Monitor(pool=pool)
		pool._pool.put_nowait("test")
		assert pool._name in repr(monitor)
		t = asyncio.create_task(monitor.run())
		await asyncio.sleep(1)
		pool._opened = False
		await t


@pytest.mark.asyncio
async def test_monitor_break_if_size_is_above_max():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	pool._opened = True
	pool._pool.put_nowait(await pool._new_conn_unchecked())
	assert pool._size == 1
	assert pool._opened is True

	monitor = Monitor(pool=pool)
	pool._size = 2
	t = asyncio.create_task(monitor.run())
	await asyncio.sleep(1)
	pool._opened = False
	await t


@pytest.mark.asyncio
async def test_pool_stop_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	with pytest.raises(PoolAlreadyClosedError):
		await pool.stop()


@pytest.mark.asyncio
async def test_pool_timeout_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1, conn_timeout=1)
	await pool.start()
	await asyncio.sleep(1)
	async with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
		with pytest.raises(PoolTimeoutError):
			async with pool.connection() as _:
				...  # pragma: no cover
	await pool.stop()


@pytest.mark.asyncio
async def test_pool_raise_during_connection():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	await pool.start()
	await asyncio.sleep(1)
	with pytest.raises(ZeroDivisionError):
		async with pool.connection() as conn:
			assert conn is not None, "Connection should not be None"
			assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
			1 / 0

	await pool.stop()


@pytest.mark.asyncio
async def test_pool_on_transaction():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1, check_interval=10)
	await pool.start()
	await asyncio.sleep(1)
	async with pool.connection() as conn:
		assert conn is not None, "Connection should not be None"
		assert pool._pool.qsize() < 1, "Connection should be removed from the pool"
		await conn.start_transaction()
	pool._pool.qsize() == 0
	await pool.stop()


@pytest.mark.asyncio
async def test_pool_start_twice():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	await pool.start()
	with pytest.raises(PoolAlreadyStartedError):
		await pool.start()
	await pool.stop()


@pytest.mark.asyncio
async def test_pool_start_generate_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	with unittest.mock.patch.object(pool._pool, "put", side_effect=Exception):
		with pytest.raises(Exception):
			await pool.start()


@pytest.mark.asyncio
async def test_pool_get_conn():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	await pool.start()
	with unittest.mock.patch.object(pool._semaphore, "acquire", side_effect=asyncio.TimeoutError):
		with pytest.raises(PoolTimeoutError):
			await pool._get_conn()

	await pool.stop()


@pytest.mark.asyncio
async def test_pool_get_ready_conn():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=1)
	await pool.start()
	with unittest.mock.patch.object(pool._pool, "get", side_effect=asyncio.TimeoutError):
		with pytest.raises(PoolTimeoutError):
			async with pool.connection() as _:
				await pool._get_ready_conn()

	await pool.stop()


@pytest.mark.asyncio
async def test_pool_put_conn_unchecked_raise():
	pool = PySQLXEnginePool(uri=SQLITE_URI, min_size=1, max_size=10)
	await pool.start()
	with unittest.mock.patch.object(pool._pool, "put", side_effect=asyncio.QueueFull):
		conn = await pool._new_conn_unchecked()
		await pool._put_conn_unchecked(conn)

	await pool.stop()
