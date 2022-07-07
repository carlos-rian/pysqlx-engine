import os
import sys
from ctypes import Union
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


import pytest
from sqlx_engine import SQLXEngine


@pytest.fixture(scope="session")
async def db_sqlite():
    uri = os.environ["DATABASE_URI_SQLITE"]
    _db = SQLXEngine(provider="sqlite", uri=uri)
    await _db.connect()
    return _db


@pytest.fixture(scope="session")
async def db_postgresql():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    _db = SQLXEngine(provider="postgresql", uri=uri)
    await _db.connect()
    return _db


@pytest.fixture(scope="session")
async def db_mssql():
    uri = os.environ["DATABASE_URI_MSSQL"]
    _db = SQLXEngine(provider="sqlserver", uri=uri)
    await _db.connect()
    return _db


@pytest.fixture(scope="session")
async def db_mysql():
    uri = os.environ["DATABASE_URI_MYSQL"]
    _db = SQLXEngine(provider="mysql", uri=uri)
    await _db.connect()
    return _db


@pytest.fixture(name="table", scope="session")
def get_table_sql():
    return {
        "sqlite": """
            create table test_table (
                id          integer   PRIMARY KEY,
                first_name  text      not null,
                last_name   text      null,
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
                email      text          null,
                phone      text          null,
                created_at datetime      not null,
                updated_at datetime      not null,
                constraint test_table_pk
                    primary key (id)
            );
        """,
    }
