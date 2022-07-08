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


def get_insert():
    return """
        INSERT INTO test_table(
            first_name,
            last_name,
            email,
            phone,
            created_at,
            updated_at
        ) VALUES ('?', '?', '?', '?', '?', '?');
    """


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_postgresql", "db_mssql", "db_mysql"])
async def test_05_check_table_was_created(name: str, all_dbs):
    db = all_dbs.get(name)
    db: SQLXEngine = await db
    sql = "SELECT * FROM test_table;"
    row = await db.query(query=sql)
    await db.close()
    assert row is None


# "db_sqlite", "db_mysql"
# "db_postgresql", db_mssql
@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_postgresql"])
async def test_06_insert_one_hundred_rows(name: SQLXEngine, all_dbs, rows: List[Dict]):
    db = all_dbs.get(name)
    db: SQLXEngine = await db
    sql = get_insert()
    for row in rows:
        params = [
            row.get("first_name"),
            row.get("last_name"),
            row.get("email"),
            row.get("phone"),
            row.get("created_at"),
            row.get("updated_at"),
        ]
        for i in range(sql.count("?")):
            sql = sql.replace("?", params[i], 1)

        resp = await db.execute(stmt=sql)
        assert isinstance(resp, int)
        assert resp == 1
