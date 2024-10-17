import os

from pysqlx_engine import PySQLXEngine, PySQLXEngineSync

SQLITE_URI = os.environ["DATABASE_URI_SQLITE"]
PGSQL_URI = os.environ["DATABASE_URI_POSTGRESQL"]
MSSQL_URI = os.environ["DATABASE_URI_MSSQL"]
MYSQL_URI = os.environ["DATABASE_URI_MYSQL"]


async def adb_sqlite():
	db = PySQLXEngine(uri=SQLITE_URI)
	await db.connect()
	return db


async def adb_pgsql():
	db = PySQLXEngine(uri=PGSQL_URI)
	await db.connect()
	return db


async def adb_mssql():
	db = PySQLXEngine(uri=MSSQL_URI)
	await db.connect()
	return db


async def adb_mysql():
	db = PySQLXEngine(uri=MYSQL_URI)
	await db.connect()
	return db


def db_sqlite():
	db = PySQLXEngineSync(uri=SQLITE_URI)
	db.connect()
	return db


def db_pgsql():
	db = PySQLXEngineSync(uri=PGSQL_URI)
	db.connect()
	return db


def db_mssql():
	db = PySQLXEngineSync(uri=MSSQL_URI)
	db.connect()
	return db


def db_mysql():
	db = PySQLXEngineSync(uri=MYSQL_URI)
	db.connect()
	return db
