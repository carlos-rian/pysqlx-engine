import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


import pytest
from sqlx_engine import SQLXEngine


@pytest.fixture
async def db_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = SQLXEngine(provider="sqlite", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


@pytest.fixture
async def db_postgresql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = SQLXEngine(provider="postgresql", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


@pytest.fixture
async def db_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = SQLXEngine(provider="sqlserver", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


@pytest.fixture
async def db_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = SQLXEngine(provider="mysql", uri=uri, improved_error_log=False)
    await _db.connect()
    return _db


@pytest.fixture(name="all_dbs")
def get_all_dbs(db_sqlite, db_postgresql, db_mssql, db_mysql):
    return {
        "db_sqlite": db_sqlite,
        "db_postgresql": db_postgresql,
        "db_mssql": db_mssql,
        "db_mysql": db_mysql,
    }


@pytest.fixture(name="table", scope="session")
def get_table_sql():
    return {
        "sqlite": """
            create table test_table (
                id          integer   PRIMARY KEY,
                first_name  text      not null,
                last_name   text      null,
                age         integer   null,
                email       text      null,
                phone       text      null,
                created_at  text      not null,
                updated_at  text      not null
            );
        """,
        "postgresql": """
            create table test_table (
                id         serial        not null,
                first_name varchar(100)  not null,
                last_name  varchar(100)  null,
                age        int           null,
                email      text          null,
                phone      text          null,
                created_at timestamp     not null,
                updated_at timestamp     not null,
                constraint test_table_pk
                    primary key (id)
            );
        """,
        "mssql": """
            create table test_table (
                id         int           not null IDENTITY(1,1),
                first_name nvarchar(100) not null,
                last_name  nvarchar(100) null,
                age        int           null,
                email      varchar(max)  null,
                phone      varchar(max)  null,
                created_at datetime      not null,
                updated_at datetime      not null,
                constraint test_table_pk
                    primary key (id)
            );
        """,
        "mysql": """
            create table test_table (
                id         int           not null auto_increment,
                first_name nvarchar(100) not null,
                last_name  nvarchar(100) null,
                age        int           null,
                email      text          null,
                phone      text          null,
                created_at datetime      not null,
                updated_at datetime      not null,
                constraint test_table_pk
                    primary key (id)
            );
        """,
    }


@pytest.fixture(name="rows", scope="session")
def get_rows():
    with open("tests/rows.json", mode="r") as f:
        data = json.loads(f.read())
        return data


@pytest.fixture(name="inserts", scope="session", autouse=True)
def get_inserts(rows):
    sql = """
        INSERT INTO test_table(
            first_name,
            last_name,
            age,
            email,
            phone,
            created_at,
            updated_at
        ) VALUES ('{0}', '{1}', {2}, '{3}', '{4}', '{5}', '{6}');
    """

    return [
        sql.format(
            row.get("first_name"),
            row.get("last_name"),
            row.get("age"),
            row.get("email"),
            row.get("phone"),
            row.get("created_at"),
            row.get("updated_at"),
        )
        for row in rows
    ]
