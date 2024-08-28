import asyncio
import os

import pytest

from pysqlx_engine import PySQLXEngine
from pysqlx_engine._core.abc.workers import PySQLXTask
from pysqlx_engine._core.const import LOG_CONFIG
from pysqlx_engine._core.util import pysqlx_get_error
from pysqlx_engine.errors import AlreadyConnectedError, ConnectError, NotConnectedError, PySQLXError, RawCmdError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_connect_success(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.connected is True


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
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_is_healthy(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.is_healthy() is True


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql])
async def test_requires_isolation_first_equal_false(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.requires_isolation_first() is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql, adb_mysql])
async def test_requires_isolation_first_equal_true(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.requires_isolation_first() is True


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_query_success(db):
	conn: PySQLXEngine = await db()
	assert conn.connected is True

	await conn.query("SELECT 1 AS number")
	await conn.close()
	assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
	"environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
async def test_using_context_manager(environment: str):
	uri = os.environ[environment]
	async with PySQLXEngine(uri=uri) as conn:
		assert conn.connected is True
	assert conn.connected is False


@pytest.mark.asyncio
async def test_error_using_context_manager():
	uri = "postgresql://postgres:wrongPass@localhost:4442"
	with pytest.raises(ConnectError):
		async with PySQLXEngine(uri=uri):
			...  # pragma: no cover


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_delete_default_connection(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.connected is True
	conn.__del__()
	assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_connection_already_exists_error(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.connected is True
	with pytest.raises(AlreadyConnectedError):
		await conn.connect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
	"environment", ["DATABASE_URI_SQLITE", "DATABASE_URI_POSTGRESQL", "DATABASE_URI_MSSQL", "DATABASE_URI_MYSQL"]
)
async def test_connection_not_connected_error(environment):
	uri = os.environ[environment]
	conn: PySQLXEngine = PySQLXEngine(uri=uri)
	assert conn.connected is False

	with pytest.raises(NotConnectedError):
		await conn.query("SELECT 1 AS number")


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_execute_raw_cmd_error(db: PySQLXEngine):
	conn: PySQLXEngine = await db()
	assert conn.connected is True
	with pytest.raises(RawCmdError):
		await conn.raw_cmd("wrong_cmd = 1")

	await conn.close()
	assert conn.connected is False


def test_pysqlx_get_error_default():
	class GenericError(Exception):
		def error(self):
			return "generic"

	error = pysqlx_get_error(err=GenericError())
	assert isinstance(error, GenericError)


def test_pysqlx_call_methods():
	class GenericError(Exception):
		def code(self):
			return "code"

		def message(self):
			return "message"

		def error(self):
			return "error"

	error = PySQLXError(err=GenericError())
	assert isinstance(error, PySQLXError)
	assert error.code == "code"
	assert error.message == "message"
	assert error.error() == "error"

	with pytest.raises(PySQLXError):
		raise error


@pytest.mark.asyncio
async def test_py_sqlx_error_json_fmt_no_colorize():
	LOG_CONFIG.PYSQLX_USE_COLOR = False
	LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

	class GenericError(Exception):
		def code(self):
			return "code"

		def message(self):
			return "message"

		def error(self):
			return "error"

	error = PySQLXError(err=GenericError())
	assert isinstance(error, PySQLXError)
	assert error.code == "code"
	assert error.message == "message"
	assert error.error() == "error"

	with pytest.raises(PySQLXError):
		raise error


@pytest.mark.asyncio
async def test_py_sqlx_error_json_fmt_with_colorize():
	LOG_CONFIG.PYSQLX_USE_COLOR = True
	LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

	class GenericError(Exception):
		def code(self):
			return "code"

		def message(self):
			return "message"

		def error(self):
			return "error"

	error = PySQLXError(err=GenericError())
	assert isinstance(error, PySQLXError)
	assert error.code == "code"
	assert error.message == "message"
	assert error.error() == "error"

	with pytest.raises(PySQLXError):
		raise error


@pytest.mark.asyncio
async def test_force_sleep_async():
	async def test():
		pass

	task = PySQLXTask(test, force_sleep=True)
	await asyncio.sleep(0.1)
	task.stop()
	await asyncio.sleep(0.2)

	try:
		await task.task
	except asyncio.CancelledError:
		print("Task was cancelled")
