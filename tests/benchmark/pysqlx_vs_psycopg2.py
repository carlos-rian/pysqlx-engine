import pytest

from pysqlx_engine import PySQLXEngineSync


@pytest.mark.asyncio
@pytest.mark.benchmark(group="sync query")
def test_pysqlx_query_all(benchmark, pgsql: PySQLXEngineSync):
    benchmark(pgsql.query, "select * from test_table")
