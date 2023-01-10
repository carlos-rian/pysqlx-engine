import os

from pysqlx_engine import PySQLXEngineSync


def pysqlx_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def pysqlx_pgsql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def pysqlx_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db


def pysqlx_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = PySQLXEngineSync(uri=uri)
    _db.connect()
    return _db
