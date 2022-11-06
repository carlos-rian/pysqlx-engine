from io import StringIO
from os import environ

import pytest
from dotenv import load_dotenv

from pysqlx_engine import PySQLXEngineSync
from pysqlx_engine.errors import IsoLevelError, QueryError, StartTransactionError
from tests.common import db_mssql, db_mysql, db_pgsql, db_sqlite


# this test not work with mssql, because mssql have lock on table.
@pytest.mark.parametrize("db", [db_sqlite, db_pgsql])
def test_execute_transaction_commit(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    resp = conn.begin()
    assert resp is None

    resp = conn.execute(stmt="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = conn.execute(stmt="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    conn2: PySQLXEngineSync = db()

    with pytest.raises(QueryError):
        conn2.query(query="SELECT * FROM test_table;")

    resp = conn.commit()
    assert resp is None

    resp = conn2.query(query="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = conn.execute(stmt="DROP TABLE test_table;")


@pytest.mark.parametrize("db", [db_mysql])
def test_execute_transaction_commit_mysql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    resp = conn.execute(stmt="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = conn.begin()
    assert resp is None

    resp = conn.execute(stmt="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    conn2: PySQLXEngineSync = db()
    resp = conn2.query(query="SELECT * FROM test_table;")
    assert len(resp) == 0

    resp = conn.commit()
    assert resp is None

    resp = conn2.query(query="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = conn.execute(stmt="DROP TABLE test_table;")
    assert resp == 0


@pytest.mark.parametrize("db", [db_mssql])
def test_execute_transaction_commit_mssql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    resp = conn.begin()
    assert resp is None

    resp = conn.execute(stmt="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = conn.execute(stmt="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    resp = conn.commit()
    assert resp is None

    resp = conn.query(query="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = conn.execute(stmt="DROP TABLE test_table;")
    assert resp == 0


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_execute_transaction_rollback_insert(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    resp = conn.execute(stmt="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = conn.begin()
    assert resp is None

    resp = conn.execute(stmt="INSERT INTO test_table VALUES (1);")

    resp = conn.rollback()
    assert resp is None

    resp = conn.query(query="SELECT * FROM test_table;")
    assert len(resp) == 0

    resp = conn.execute(stmt="DROP TABLE test_table;")
    assert isinstance(resp, int)


# this test is failing for mysql, but it's not a bug
# mysql is inconsistent to create a table in a transaction


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql])
def test_execute_transaction_rollback_create(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    resp = conn.begin()
    assert resp is None

    resp = conn.execute(stmt="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = conn.rollback()
    assert resp is None

    with pytest.raises(QueryError):
        conn.query(query="SELECT * FROM test_table;")


@pytest.mark.parametrize("db", [db_mysql, db_mssql, db_pgsql])
def test_start_transaction_with_set_isolation_level(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.start_transaction(isolation_level="ReadCommitted")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.start_transaction(isolation_level="ReadUncommitted")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.start_transaction(isolation_level="RepeatableRead")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.start_transaction(isolation_level="Serializable")
    assert resp is None
    conn.close()


@pytest.mark.parametrize("db", [db_mssql])
def test_start_transaction_with_set_isolation_level_mssql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.start_transaction(isolation_level="Snapshot")
    assert resp is None
    conn.close()


# postgresql does not support this isolation level


@pytest.mark.parametrize("db", [db_pgsql])
def test_start_transaction_with_invalid_isolation_level_pgsql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(StartTransactionError):
        conn.start_transaction(isolation_level="Snapshot")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_start_transaction_with_invalid_isolation_level(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(ValueError):
        conn.start_transaction(isolation_level="Read")

    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_mssql])
def test_set_isolation_level_mssql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.set_isolation_level(isolation_level="ReadCommitted")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.set_isolation_level(isolation_level="ReadUncommitted")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.set_isolation_level(isolation_level="RepeatableRead")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.set_isolation_level(isolation_level="Serializable")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    resp = conn.set_isolation_level(isolation_level="Snapshot")
    assert resp is None
    conn.close()

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    with pytest.raises(ValueError):
        conn.set_isolation_level(isolation_level="Read")


@pytest.mark.parametrize("db", [db_pgsql])
def test_set_isolation_level_pgsql(db):
    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    with pytest.raises(IsoLevelError):
        conn.set_isolation_level(isolation_level="Snapshot")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_pgsql])
def test_set_isolation_level_pgsql_with_colored_log(db):
    env = StringIO(
        """
        DATABASE_URI_POSTGRESQL="postgresql://postgres:Build!Test321@localhost:4442/engine"
        PYSQLX_ERROR_COLORIZE=1
        PYSQLX_ENGINE_COLORIZE=1
        """
    )
    load_dotenv(stream=env, override=True)

    conn: PySQLXEngineSync = db()
    assert conn.connected is True
    with pytest.raises(IsoLevelError):
        conn.set_isolation_level(isolation_level="Snapshot")
    conn.close()
    assert conn.connected is False


@pytest.mark.parametrize("db", [db_sqlite, db_pgsql, db_mssql, db_mysql])
def test_start_transaction_with_invalid_isolation_level_with_colored_log(db):
    env = StringIO(
        """
        DATABASE_URI_POSTGRESQL="postgresql://postgres:Build!Test321@localhost:4442/engine"
        PYSQLX_ERROR_COLORIZE=1
        PYSQLX_ENGINE_COLORIZE=1
        PYSQLX_ERROR_JSON_FMT=1
        """
    )
    load_dotenv(stream=env, override=True)

    conn: PySQLXEngineSync = db()
    assert conn.connected is True

    with pytest.raises(ValueError):
        conn.start_transaction(isolation_level="Read")

    conn.close()
    assert conn.connected is False
