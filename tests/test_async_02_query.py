from datetime import datetime

import pytest
from sqlx_engine import SQLXEngine

from tests.common import get_all_adbs


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_01_query_all_rows_with_base_row(name: SQLXEngine):
    db = get_all_adbs(name)
    db: SQLXEngine = await db()
    rows = await db.query(query="SELECT * FROM test_table")
    for row in rows:
        assert isinstance(row.id, int)
        assert isinstance(row.first_name, str)
        assert isinstance(row.last_name, str) or row.last_name is None
        assert isinstance(row.age, int) or row.age is None
        assert isinstance(row.email, str) or row.email is None
        assert isinstance(row.phone, str) or row.phone is None
        # sqlite is str
        assert isinstance(row.created_at, (datetime, str))
        assert isinstance(row.updated_at, (datetime, str))
    await db.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
async def test_02_query_all_rows_with_dict(name: SQLXEngine):
    db = get_all_adbs(name)
    db: SQLXEngine = await db()
    rows = await db.query(query="SELECT * FROM test_table", as_base_row=False)
    for row in rows:
        assert isinstance(row, dict)
        assert isinstance(row["id"], int)
        assert isinstance(row["first_name"], str)
        assert isinstance(row["last_name"], str) or row["last_name"] is None
        assert isinstance(row["age"], int) or row["age"] is None
        assert isinstance(row["email"], str) or row["email"] is None
        assert isinstance(row["phone"], str) or row["phone"] is None
        # sqlite is str
        assert isinstance(row["created_at"], (str, datetime))
        assert isinstance(row["updated_at"], (str, datetime))
    await db.close()
