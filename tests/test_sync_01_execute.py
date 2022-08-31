from typing import Dict, List

import pytest
from sqlx_engine import SQLXEngineSync
from typing_extensions import Literal

from tests.common import get_all_dbs


def remove_table(db: SQLXEngineSync):
    try:
        drop = "DROP TABLE test_table;"
        resp = db.execute(drop)
        print(resp)
    except Exception as err:
        print(err)


def test_01_create_table_sqlite(
    db_sqlite: SQLXEngineSync, table: Dict[Literal["sqlite"], str]
):
    db = db_sqlite
    remove_table(db=db)

    sql = table["sqlite"]
    row_count = db.execute(sql)
    assert row_count == 0
    db.close()


def test_02_create_table_postgresql(
    db_postgresql: SQLXEngineSync,
    table: Dict[Literal["postgresql"], str],
):
    db = db_postgresql
    remove_table(db=db)

    sql = table["postgresql"]
    row_count = db.execute(sql)
    assert row_count == 0
    db.close()


def test_03_create_table_mssql(
    db_mssql: SQLXEngineSync,
    table: Dict[Literal["mssql"], str],
):
    db = db_mssql
    remove_table(db=db)

    sql = table["mssql"]
    row_count = db.execute(sql)
    assert row_count == 0
    db.close()


def test_04_create_table_mysql(
    db_mysql: SQLXEngineSync,
    table: Dict[Literal["mysql"], str],
):
    db = db_mysql
    remove_table(db=db)

    sql = table["mysql"]
    row_count = db.execute(sql)
    assert row_count == 0
    db.close()


@pytest.mark.parametrize("name", ["db_sqlite", "db_postgresql", "db_mssql", "db_mysql"])
def test_05_check_table_was_created(name: str):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    sql = "SELECT * FROM test_table;"
    row = db.query(query=sql)
    db.close()
    assert row is None


@pytest.mark.parametrize("name", ["db_sqlite", "db_mysql", "db_postgresql", "db_mssql"])
def test_06_insert_one_hundred_rows(name: SQLXEngineSync, inserts: List[Dict]):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    for sql in inserts:
        resp = db.execute(stmt=sql)
        assert isinstance(resp, int)
        assert resp == 1

    db.close()


@pytest.mark.parametrize("name", ["db_mysql", "db_postgresql", "db_mssql", "db_sqlite"])
def test_07_update_all_rows(name: SQLXEngineSync, rows: list):
    db = get_all_dbs(name)
    db: SQLXEngineSync = db()
    _rows = db.query(query="SELECT id FROM test_table")

    update = """
        UPDATE test_table
        SET first_name = '{name}',
            updated_at = '2022-07-09 22:00:01'
        WHERE id = {id}
    """
    query = "SELECT id, first_name FROM test_table WHERE id = {id}"
    for row in _rows:
        resp = db.execute(stmt=update.format(name="test", id=row.id))
        assert isinstance(resp, int)
        assert resp == 1

        new_row = db.query(query=query.format(id=row.id))
        assert isinstance(new_row[0].first_name, str)
        assert new_row[0].first_name == "test"

    for data, row in zip(rows, _rows):
        resp = db.execute(stmt=update.format(id=row.id, name=data["first_name"]))
        assert isinstance(resp, int)
        assert resp == 1

        new_row = db.query(query=query.format(id=row.id))
        assert isinstance(new_row[0].first_name, str)
        assert new_row[0].first_name == data["first_name"]

    db.close()
