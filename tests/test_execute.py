from typing import Dict, Literal

import pytest
from sqlx_engine import SQLXEngine


@pytest.mark.asyncio
async def test_create_table_sqlite(
    db_sqlite: SQLXEngine,
    table: Dict[Literal["sqlite"], str],
):
    sql = table["sqlite"]
    db = await db_sqlite
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_create_table_postgresql(
    db_postgresql: SQLXEngine,
    table: Dict[Literal["postgresql"], str],
):
    sql = table["postgresql"]
    db = await db_postgresql
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_create_table_mssql(
    db_mssql: SQLXEngine,
    table: Dict[Literal["mssql"], str],
):
    sql = table["mssql"]
    db = await db_mssql
    row_count = await db.execute(sql)
    assert row_count == 0


@pytest.mark.asyncio
async def test_create_table_mysql(
    db_mysql: SQLXEngine,
    table: Dict[Literal["mysql"], str],
):
    sql = table["mysql"]
    db = await db_mysql
    row_count = await db.execute(sql)
    assert row_count == 0
