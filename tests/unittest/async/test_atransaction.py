import pytest
from pysqlx_engine._core.const import LOG_CONFIG

from pysqlx_engine import PySQLXEngine
from pysqlx_engine.errors import IsoLevelError, QueryError, StartTransactionError
from tests.common import adb_mssql, adb_mysql, adb_pgsql, adb_sqlite


# this test not work with mssql, because mssql have lock on table.
@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql])
async def test_execute_transaction_commit(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.begin()
    assert resp is None

    resp = await conn.execute(sql="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = await conn.execute(sql="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    conn2: PySQLXEngine = await db()

    with pytest.raises(QueryError):
        await conn2.query(sql="SELECT * FROM test_table;")

    resp = await conn.commit()
    assert resp is None

    resp = await conn2.query(sql="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = await conn.execute(sql="DROP TABLE test_table;")


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql])
async def test_execute_transaction_commit_mysql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.execute(sql="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = await conn.begin()
    assert resp is None

    resp = await conn.execute(sql="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    conn2: PySQLXEngine = await db()
    resp = await conn2.query(sql="SELECT * FROM test_table;")
    assert len(resp) == 0

    resp = await conn.commit()
    assert resp is None

    resp = await conn2.query(sql="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = await conn.execute(sql="DROP TABLE test_table;")
    assert resp == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql])
async def test_execute_transaction_commit_mssql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.begin()
    assert resp is None

    resp = await conn.execute(sql="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = await conn.execute(sql="INSERT INTO test_table VALUES (1);")
    assert resp == 1

    resp = await conn.commit()
    assert resp is None

    resp = await conn.query(sql="SELECT * FROM test_table;")
    assert len(resp) == 1

    resp = await conn.execute(sql="DROP TABLE test_table;")
    assert resp == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_execute_transaction_rollback_insert(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.execute(sql="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = await conn.begin()
    assert resp is None

    resp = await conn.execute(sql="INSERT INTO test_table VALUES (1);")

    resp = await conn.rollback()
    assert resp is None

    resp = await conn.query(sql="SELECT * FROM test_table;")
    assert len(resp) == 0

    resp = await conn.execute(sql="DROP TABLE test_table;")
    assert isinstance(resp, int)


# this test is failing for mysql, but it's not a bug
# mysql is inconsistent to create a table in a transaction
@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql])
async def test_execute_transaction_rollback_create(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    resp = await conn.begin()
    assert resp is None

    resp = await conn.execute(sql="CREATE TABLE test_table (id INT);")
    assert resp == 0

    resp = await conn.rollback()
    assert resp is None

    with pytest.raises(QueryError):
        await conn.query(sql="SELECT * FROM test_table;")


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mysql, adb_mssql, adb_pgsql])
async def test_start_transaction_with_set_isolation_level(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.start_transaction(isolation_level="ReadCommitted")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.start_transaction(isolation_level="ReadUncommitted")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.start_transaction(isolation_level="RepeatableRead")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.start_transaction(isolation_level="Serializable")
    assert resp is None
    await conn.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql])
async def test_start_transaction_with_set_isolation_level_mssql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.start_transaction(isolation_level="Snapshot")
    assert resp is None
    await conn.close()


# postgresql does not support this isolation level
@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_pgsql])
async def test_start_transaction_with_invalid_isolation_level_pgsql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(StartTransactionError):
        await conn.start_transaction(isolation_level="Snapshot")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_start_transaction_with_invalid_isolation_level(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(ValueError):
        await conn.start_transaction(isolation_level="Read")

    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_mssql])
async def test_set_isolation_level_mssql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.set_isolation_level(isolation_level="ReadCommitted")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.set_isolation_level(isolation_level="ReadUncommitted")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.set_isolation_level(isolation_level="RepeatableRead")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.set_isolation_level(isolation_level="Serializable")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    resp = await conn.set_isolation_level(isolation_level="Snapshot")
    assert resp is None
    await conn.close()

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    with pytest.raises(ValueError):
        await conn.set_isolation_level(isolation_level="Read")


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_pgsql])
async def test_set_isolation_level_pgsql(db):
    conn: PySQLXEngine = await db()
    assert conn.connected is True
    with pytest.raises(IsoLevelError):
        await conn.set_isolation_level(isolation_level="Snapshot")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_pgsql])
async def test_set_isolation_level_pgsql_with_colored_log(db):
    LOG_CONFIG.PYSQLX_MSG_COLORIZE = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True
    with pytest.raises(IsoLevelError):
        await conn.set_isolation_level(isolation_level="Snapshot")
    await conn.close()
    assert conn.connected is False


@pytest.mark.asyncio
@pytest.mark.parametrize("db", [adb_sqlite, adb_pgsql, adb_mssql, adb_mysql])
async def test_start_transaction_with_invalid_isolation_level_with_colored_log(db):
    LOG_CONFIG.PYSQLX_MSG_COLORIZE = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    conn: PySQLXEngine = await db()
    assert conn.connected is True

    with pytest.raises(ValueError):
        await conn.start_transaction(isolation_level="Read")

    await conn.close()
    assert conn.connected is False
