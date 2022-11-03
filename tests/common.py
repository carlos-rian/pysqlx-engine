import os

from pysqlx_engine import PySQLXEngine, PySQLXEngineSync


async def adb_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = PySQLXEngine(uri=uri)
    await _db.connect()
    return _db


async def adb_pgsql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = PySQLXEngine(uri=uri)
    await _db.connect()
    return _db


async def adb_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = PySQLXEngine(uri=uri)
    await _db.connect()
    return _db


async def adb_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = PySQLXEngine(uri=uri)
    await _db.connect()
    return _db


def db_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def db_pgsql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def db_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def db_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db
