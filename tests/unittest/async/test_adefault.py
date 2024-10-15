import asyncio
import os
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum

import pytest
from pysqlx_core import PySQLxStatement

from pysqlx_engine import LOG_CONFIG, PySQLXEngine
from pysqlx_engine._core.abc.workers import PySQLXTask
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

	LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

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
@pytest.mark.parametrize("provider", ["sqlite", "postgresql", "mysql", "sqlserver"])
async def test_build_statement(provider):
	import base64
	from datetime import timezone

	class EnumColorsAsStr(str, Enum):
		BLUE = "blue"
		RED = "red"
		GRAY = "gray"
		BLACK = "black"

	p = PySQLxStatement(
		provider=provider,
		sql="""
			INSET INTO pysqlx_table (
				type_int, type_smallint, type_bigint, type_numeric, type_float, type_double, type_decimal, 
				type_char, type_varchar, type_nvarchar, type_text, type_boolean, type_date, type_time, 
				type_timestamp, type_datetime, type_enum, type_json, type_bytes, type_enum_as_str, enum_json_list
			)
			VALUES (
				:type_int, :type_smallint, :type_bigint, :type_numeric, :type_float, :type_double, :type_decimal,
				:type_char, :type_varchar, :type_nvarchar, :type_text, :type_boolean, :type_date, :type_time,
				:type_timestamp, :type_datetime, :type_enum, :type_json, :type_bytes :type_enum_as_str, :enum_json_list
			);
			""",
		params={
			"type_int": 1,
			"type_smallint": 2,
			"type_bigint": 3,
			"type_numeric": 14.8389,
			"type_float": 13343400,
			"type_double": 1.6655444,
			"type_decimal": Decimal("19984"),
			"type_char": "r",
			"type_varchar": "hfhfjjieurjnnd",
			"type_nvarchar": "$~k;dldëjdjd",
			"type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
			"type_boolean": True,
			"type_date": date(2022, 1, 1),
			"type_time": time(12, 10, 11),
			"type_timestamp": datetime(2022, 12, 20, 8, 59, 55),
			"type_datetime": datetime(2022, 12, 20, 9, 0),
			"type_enum": EnumColorsAsStr.BLUE,
			"type_json": [
				{"type_int": 1},
				{"type_smallint": 2},
				{"type_bigint": 3},
				14.8389,
				13343400,
				1.6655444,
				Decimal("19984"),
				"r",
				"hfhfjjieurjnnd",
				"$~k;dldëjdjd",
				"hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
				True,
				date(2022, 1, 1),
				time(12, 10, 11),
				datetime(2022, 12, 20, 8, 59, 55),
				datetime(2022, 12, 20, 9, 0),
				EnumColorsAsStr.BLUE,
				["name", "age"],
				("name", "age"),
				b"super bytes",
				EnumColorsAsStr.BLUE,
				[
					EnumColorsAsStr.BLUE,
					EnumColorsAsStr.RED,
					EnumColorsAsStr.GRAY,
					EnumColorsAsStr.BLACK,
				],
			],
			"type_bytes": b"super bytes",
			"type_enum_as_str": EnumColorsAsStr.BLUE,
			"enum_json_list": [
				EnumColorsAsStr.BLUE,
				EnumColorsAsStr.RED,
				EnumColorsAsStr.GRAY,
				EnumColorsAsStr.BLACK,
			],
		},
	)

	params = p.params()
	assert isinstance(params, list)

	assert params[0] == 1
	assert params[1] == 2
	assert params[2] == 3
	assert params[3] == 14.8389
	assert params[4] == 13343400
	assert params[5] == 1.6655444
	assert params[6] == Decimal("19984")
	assert params[7] == "r"
	assert params[8] == "hfhfjjieurjnnd"
	assert params[9] == "$~k;dldëjdjd"
	assert params[10] == "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf"
	assert params[11] is True
	assert params[12] == date(2022, 1, 1)
	assert params[13] == time(12, 10, 11)
	assert params[14] == datetime(2022, 12, 20, 8, 59, 55, tzinfo=timezone.utc)
	assert params[15] == datetime(2022, 12, 20, 9, 0, tzinfo=timezone.utc)
	assert params[16] == "blue"

	assert params[17][0] == {"type_int": 1}
	assert params[17][1] == {"type_smallint": 2}
	assert params[17][2] == {"type_bigint": 3}
	assert params[17][3] == 14.8389
	assert params[17][4] == 13343400
	assert params[17][5] == 1.6655444
	assert params[17][6] == "19984"
	assert params[17][7] == "r"
	assert params[17][8] == "hfhfjjieurjnnd"
	assert params[17][9] == "$~k;dldëjdjd"
	assert params[17][10] == "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf"
	assert params[17][11] is True
	assert params[17][12] == "2022-01-01"
	assert params[17][13] == "12:10:11"
	assert params[17][14] == "2022-12-20T08:59:55.000Z"
	assert params[17][15] == "2022-12-20T09:00:00.000Z"
	assert params[17][16] == "blue"
	assert params[17][17] == ["name", "age"]
	assert params[17][18] == ["name", "age"]
	assert params[17][19] == base64.b64encode(b"super bytes").decode()
	assert params[17][20] == "blue"
	assert params[17][21] == ["blue", "red", "gray", "black"]

	assert params[18] == b"super bytes"
	assert params[19] == "blue"
	assert params[20] == ["blue", "red", "gray", "black"]


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
