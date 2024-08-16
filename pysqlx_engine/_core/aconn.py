from typing import Optional

import pysqlx_core

from .._core.const import LOG_CONFIG
from .._core.logger import logger
from .._core.parser import BaseRow, MyModel, ParserIn, ParserSQL

# ParserSQL,
# import necessary using _core to not subscribe default parser
from .const import ISOLATION_LEVEL
from .errors import AlreadyConnectedError, NotConnectedError, ParameterInvalidValueError
from .helper import fe_sql, model_parameter_error_message, not_connected_error_message
from .util import check_isolation_level, check_sql_and_parameters, pysqlx_get_error


class PySQLXEngine:
	__slots__ = ["uri", "connected", "_conn", "_provider"]

	uri: str
	connected: bool

	def __init__(self, uri: str):
		self.connected: bool = False

		_providers = ["postgresql", "mysql", "sqlserver", "sqlite"]
		if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
			raise ValueError(f"invalid uri: {uri}, check the usage uri, accepted providers: {', '.join(_providers)}")

		if uri.startswith("sqlite"):
			uri = uri.replace("sqlite", "file", 1)

		self.uri: str = uri
		self._conn: Optional[pysqlx_core.Connection] = None

		self._provider = "sqlite"

		for prov in _providers:
			if self.uri.startswith(prov):
				self._provider = prov

	def __del__(self):
		if self.connected:
			del self._conn
			self._conn = None
			self.connected = False

	def is_healthy(self):
		self._pre_validate()
		return self._conn.is_healthy()

	def requires_isolation_first(self):
		self._pre_validate()
		return self._conn.requires_isolation_first()

	async def __aenter__(self):
		await self.connect()
		return self

	async def __aexit__(self, exc_type, exc, exc_tb):
		await self.close()

	async def connect(self):
		if self.connected:
			raise AlreadyConnectedError()
		try:
			self._conn = await pysqlx_core.new(uri=self.uri)
			self.connected = True
		except pysqlx_core.PySQLxError as e:
			raise pysqlx_get_error(err=e)

	async def close(self):
		if self.connected:
			del self._conn
			self._conn = None
			self.connected = False

	async def raw_cmd(self, sql: str):
		return await self._run(func=self._conn.raw_cmd, sql=sql)

	def _dev_mode(self, sql: str, parameters: Optional[dict] = None):
		if LOG_CONFIG.PYSQLX_DEV_MODE:
			try:
				from rich.console import Console
			except ImportError:
				raise ImportError(
					"rich library is required to use the development mode, install it using: pip install rich"
				)
			console = Console()
			console.rule("THIS IS A DEVELOPMENT MODE")
			console.rule("THIS SQL STATEMENT IS NOT SEND TO THE DATABASE BELOW!")
			log_sql = ParserSQL(provider=self._provider, sql=sql, parameters=parameters).sql()
			console.log(fe_sql(sql=log_sql))
			console.rule("THIS SQL STATEMENT IS NOT SEND TO THE DATABASE ABOVE!")

	async def _run(self, func, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
		self._pre_validate(sql=sql, parameters=parameters)
		if model is not None and not issubclass(model, BaseRow):
			raise TypeError(model_parameter_error_message())

		try:
			stmt = pysqlx_core.PySQLxStatement(provider=self._provider, sql=sql, params=parameters)
			if LOG_CONFIG.PYSQLX_DEV_MODE:
				self._dev_mode(sql=sql, parameters=parameters)

			if LOG_CONFIG.PYSQLX_SQL_LOG:
				logger.info(f"SQL: {stmt.sql()}\nPARAMS: {stmt.params()}")

			return await func(stmt)

		except pysqlx_core.PySQLxError as e:
			raise pysqlx_get_error(err=e)

		except pysqlx_core.PySQLxInvalidParamError as e:
			raise ParameterInvalidValueError(
				field=e.field(),
				provider=self._provider,
				typ_from=e.typ_from(),
				typ_to=e.typ_to(),
			)

	async def query(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
		result = await self._run(func=self._conn.query_typed, sql=sql, parameters=parameters, model=model)
		return ParserIn(result=result, model=model).parse()

	async def query_as_dict(self, sql: str, parameters: Optional[dict] = None):
		return await self._run(self._conn.query_all, sql=sql, parameters=parameters)

	async def query_first(self, sql: str, parameters: Optional[dict] = None, model: Optional[MyModel] = None):
		result = await self._run(self._conn.query_typed, sql=sql, parameters=parameters, model=model)
		return ParserIn(result=result, model=model).parse_first()

	async def query_first_as_dict(self, sql: str, parameters: Optional[dict] = None):
		row = await self._run(self._conn.query_one, sql=sql, parameters=parameters)
		return row if row else None

	async def execute(self, sql: str, parameters: Optional[dict] = None):
		return await self._run(self._conn.execute, sql=sql, parameters=parameters)

	async def set_isolation_level(self, isolation_level: ISOLATION_LEVEL):
		self._pre_validate(isolation_level=isolation_level)
		try:
			await self._conn.set_isolation_level(isolation_level=isolation_level)
		except pysqlx_core.PySQLxError as e:
			raise pysqlx_get_error(err=e)

	async def begin(self):
		await self.start_transaction()

	async def commit(self):
		self._pre_validate()
		if self._provider == "sqlserver":
			await self.raw_cmd(sql="COMMIT TRANSACTION;")
		else:
			await self.raw_cmd(sql="COMMIT;")

	async def rollback(self):
		self._pre_validate()
		if self._provider == "sqlserver":
			await self.raw_cmd(sql="ROLLBACK TRANSACTION;")
		else:
			await self.raw_cmd(sql="ROLLBACK;")

	async def start_transaction(self, isolation_level: Optional[ISOLATION_LEVEL] = None):
		self._pre_validate(isolation_level=isolation_level)
		try:
			await self._conn.start_transaction(isolation_level=isolation_level)
		except pysqlx_core.PySQLxError as e:
			raise pysqlx_get_error(err=e)

	def _pre_validate(
		self,
		sql: str = "",
		parameters: Optional[dict] = None,
		isolation_level: Optional[ISOLATION_LEVEL] = None,
	):
		if not self.connected:
			raise NotConnectedError(not_connected_error_message())

		if sql != "":
			check_sql_and_parameters(sql=sql, parameters=parameters)

		if isolation_level is not None:
			check_isolation_level(isolation_level=isolation_level)
