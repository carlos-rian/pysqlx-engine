from datetime import datetime

import pytest
from sqlx_engine import SQLXEngineSync

from tests.common import get_all_dbs


@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
def test_01_query_all_rows_with_base_row(name: SQLXEngineSync):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    rows = db.query(query="SELECT * FROM test_table")
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
    db.close()


@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
def test_02_query_all_rows_with_dict(name: SQLXEngineSync):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    rows = db.query(query="SELECT * FROM test_table", as_base_row=False)
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
    db.close()
