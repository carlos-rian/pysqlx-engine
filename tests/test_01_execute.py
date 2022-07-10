from datetime import datetime
from typing import Dict, List, Literal

import pytest
from sqlx_engine import SQLXEngine


async def remove_table(db: SQLXEngine):
    try:
        drop = "DROP TABLE test_table;"
        resp = await db.execute(drop)
        print(resp)
    except Exception as err:
        print(err)


@pytest.mark.asyncio
async def test_01_create_table_sqlite(
    db_sqlite: SQLXEngine,
    table: Dict[Literal["sqlite"], str],
):
    db = await db_sqlite
    await remove_table(db=db)

    sql = table["sqlite"]
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_02_create_table_postgresql(
    db_postgresql: SQLXEngine,
    table: Dict[Literal["postgresql"], str],
):
    db = await db_postgresql
    await remove_table(db=db)

    sql = table["postgresql"]
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_03_create_table_mssql(
    db_mssql: SQLXEngine,
    table: Dict[Literal["mssql"], str],
):
    db = await db_mssql
    await remove_table(db=db)

    sql = table["mssql"]
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_04_create_table_mysql(
    db_mysql: SQLXEngine,
    table: Dict[Literal["mysql"], str],
):
    db = await db_mysql
    await remove_table(db=db)

    sql = table["mysql"]
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_postgresql", "db_mssql", "db_mysql"])
async def test_05_check_table_was_created(name: str, all_dbs):
    db = all_dbs.get(name)
    db: SQLXEngine = await db
    sql = "SELECT * FROM test_table;"
    row = await db.query(query=sql)
    await db.close()
    assert row is None


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_06_insert_one_hundred_rows(
    name: SQLXEngine, all_dbs: dict, inserts: List[Dict]
):
    db = all_dbs.get(name)
    db: SQLXEngine = await db
    for sql in inserts:
        resp = await db.execute(stmt=sql)
        assert isinstance(resp, int)
        assert resp == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_mysql", "db_postgresql", "db_mssql", "db_sqlite"])
async def test_07_update_all_rows(name: SQLXEngine, all_dbs: dict, rows: list):
    db = all_dbs.get(name)
    db: SQLXEngine = await db
    _rows = await db.query(query="SELECT id FROM test_table")

    update = """
        UPDATE test_table
        SET first_name = '{name}',
            updated_at = '2022-07-09 22:00:01'
        WHERE id = {id}
    """
    query = "SELECT id, first_name FROM test_table WHERE id = {id}"
    for row in _rows:
        resp = await db.execute(stmt=update.format(name="test", id=row.id))
        assert isinstance(resp, int)
        assert resp == 1

        new_row = await db.query(query=query.format(id=row.id))
        assert isinstance(new_row[0].first_name, str)
        assert new_row[0].first_name == "test"

    for data, row in zip(rows, _rows):
        resp = await db.execute(stmt=update.format(id=row.id, name=data["first_name"]))
        assert isinstance(resp, int)
        assert resp == 1

        new_row = await db.query(query=query.format(id=row.id))
        assert isinstance(new_row[0].first_name, str)
        assert new_row[0].first_name == data["first_name"]
