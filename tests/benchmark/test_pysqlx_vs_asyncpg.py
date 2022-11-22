import asyncpg
import pytest

from pysqlx_engine import PySQLXEngine
from tests.benchmark import db, prepare
from pysqlx_engine._core.until import force_sync


@pytest.mark.benchmark(group="async query 100 rows")
def test_pysqlx_query_all(benchmark):
    pgsql = db.pysqlx_pgsql()
    prepare.pgsql_sample_create_and_insert_100_rows(conn=pgsql)
    pgsql.close()

    @force_sync
    async def query():
        db = PySQLXEngine(uri="postgresql://postgres:Build!Test321@localhost:4442/engine")
        await db.connect()
        result = await db.query(sql="select * from test_benchmark_sample_table_100", as_dict=True)
        db.close()
        assert len(result) == 100

    benchmark.pedantic(query, iterations=100, rounds=100)


@pytest.mark.benchmark(group="async query 100 rows")
def test_asyncpg_query_all(benchmark):
    pgsql = db.pysqlx_pgsql()
    prepare.pgsql_sample_create_and_insert_100_rows(conn=pgsql)
    pgsql.close()

    @force_sync
    async def query():
        conn = await asyncpg.connect(
            database="engine", user="postgres", password="Build!Test321", host="localhost", port="4442"
        )

        result = await conn.fetch("select * from test_benchmark_sample_table_100")
        await conn.close()
        assert len(result) == 100

    benchmark.pedantic(query, iterations=100, rounds=100)
