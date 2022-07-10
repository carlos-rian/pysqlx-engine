import os

from sqlx_engine import SQLXEngine


async def db_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = SQLXEngine(provider="sqlite", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


async def db_postgresql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = SQLXEngine(provider="postgresql", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


async def db_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = SQLXEngine(provider="sqlserver", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


async def db_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = SQLXEngine(provider="mysql", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


def get_all_dbs(db: str):
    return {
        "db_sqlite": db_sqlite,
        "db_postgresql": db_postgresql,
        "db_mssql": db_mssql,
        "db_mysql": db_mysql,
    }.get(db)
