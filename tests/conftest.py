import os
import sys

import pytest
import pytest_asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from tests import common


@pytest_asyncio.fixture
async def adb_sqlite():
    return await common.adb_sqlite()


@pytest_asyncio.fixture
async def adb_pgsql():
    return await common.adb_pgsql()


@pytest_asyncio.fixture
async def adb_mssql():
    return await common.adb_mssql()


@pytest_asyncio.fixture
async def adb_mysql():
    return await common.adb_mysql()


@pytest.fixture
def db_sqlite():
    return common.db_sqlite()


@pytest.fixture
def db_postgresql():
    return common.db_postgresql()


@pytest.fixture
def db_mssql():
    return common.db_mssql()


@pytest.fixture
def db_mysql():
    return common.db_mysql()


@pytest.fixture(name="create_table", scope="session")
def get_create_table():
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
        "pgsql": """
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
