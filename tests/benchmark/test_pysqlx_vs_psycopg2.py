import psycopg2
import pytest

from pysqlx_engine import PySQLXEngineSync
from tests.benchmark import db, prepare


@pytest.mark.benchmark(group="sync query 100 rows")
def test_pysqlx_query_all(benchmark):
    pgsql = db.pysqlx_pgsql()
    prepare.pgsql_sample_create_and_insert_100_rows(conn=pgsql)
    pgsql.close()

    def query():
        db = PySQLXEngineSync(uri="postgresql://postgres:Build!Test321@localhost:4442/engine")
        db.connect()
        result = db.query(sql="select * from test_benchmark_sample_table_100", as_dict=True)
        db.close()
        return result

    result = benchmark.pedantic(query, iterations=10, rounds=100)
    assert len(result) == 100


@pytest.mark.benchmark(group="sync query 100 rows")
def test_psycopg2_query_all(benchmark):
    pgsql = db.pysqlx_pgsql()
    prepare.pgsql_sample_create_and_insert_100_rows(conn=pgsql)
    pgsql.close()

    def query():
        conn = psycopg2.connect(
            database="engine", user="postgres", password="Build!Test321", host="localhost", port="4442"
        )
        cursor = conn.cursor()
        cursor.execute("select * from test_benchmark_sample_table_100")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    result = benchmark.pedantic(query, iterations=10, rounds=100)
    assert len(result) == 100
