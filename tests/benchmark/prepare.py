import os

from pysqlx_engine import PySQLXEngineSync

sample_table = """
        create table test_benchmark_sample_table_{table_name} (
            id         serial        not null,
            first_name varchar(100)  not null,
            last_name  varchar(100)  null,
            age        int           null,
            email      text          null,
            phone      text          null,
            created_at timestamp     not null,
            updated_at timestamp     not null,
            constraint test_benchmark_100_pk
                primary key (id)
        );
    """

complex_table = """
    create table test_benchmark_complex_table_{table_name}
    (
        type_int           integer,
        type_smallint      smallint,
        type_bigint        bigint,
        type_serial        serial,
        type_smallserial   smallserial,
        type_bigserial     bigserial,
        type_numeric       numeric,
        type_float         double precision,
        type_double        double precision,
        type_money         money,
        type_char          char,
        type_varchar       varchar(100),
        type_text          text,
        type_boolean       boolean,
        type_date          date,
        type_time          time,
        type_datetime      timestamp,
        type_datetimetz    timestamp with time zone,
        type_enum          colors,
        type_uuid          uuid,
        type_json          json,
        type_jsonb         jsonb,
        type_xml           xml,
        type_inet          inet,
        type_bytes         bytea,
        type_array_text    text[],
        type_array_integer integer[],
        type_array_date    date[],
        type_array_uuid    uuid[]
    );
"""


# sample
def sample_create_and_insert_100_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_sample_table_100")
    assert resp == 0

    resp = conn.execute(sql=sample_table.format(table_name=100))
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/sample.sql", "r") as f:
        rows = f.readlines()[0:100]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_sample_table_100")


def sample_create_and_insert_1_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_sample_table_1_000")
    assert resp == 0

    resp = conn.execute(sql=sample_table)
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/sample.sql", "r") as f:
        rows = f.readlines()[0:1_000]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_sample_table_1_000")


def sample_create_and_insert_10_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_sample_table_10_000")
    assert resp == 0

    resp = conn.execute(sql=sample_table)
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/sample.sql", "r") as f:
        rows = f.readlines()[0:10_000]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_sample_table_10_000")


def sample_create_and_insert_100_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_sample_table_100_000")
    assert resp == 0

    resp = conn.execute(sql=sample_table)
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/sample.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_sample_table_100_000")


# complex
def complex_create_and_insert_100_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_complex_table_100")
    assert resp == 0

    resp = conn.execute("drop type if exists colors")
    assert resp == 0

    resp = conn.execute("create type colors as enum ('blue', 'red', 'gray', 'black');")
    assert resp == 0

    resp = conn.execute(sql=sample_table.format(table_name=100))
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/complex.sql", "r") as f:
        rows = f.readlines()[0:100]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_complex_table_100")
    conn.execute("drop type if exists colors")


def complex_create_and_insert_1_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_complex_table_1_000")
    assert resp == 0

    resp = conn.execute("drop type if exists colors")
    assert resp == 0

    resp = conn.execute("create type colors as enum ('blue', 'red', 'gray', 'black');")
    assert resp == 0

    resp = conn.execute(sql=sample_table.format(table_name=1_000))
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/complex.sql", "r") as f:
        rows = f.readlines()[0:1_000]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_complex_table_1_000")
    conn.execute("drop type if exists colors")


def complex_create_and_insert_10_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_complex_table_10_000")
    assert resp == 0

    resp = conn.execute("drop type if exists colors")
    assert resp == 0

    resp = conn.execute("create type colors as enum ('blue', 'red', 'gray', 'black');")
    assert resp == 0

    resp = conn.execute(sql=sample_table.format(table_name=10_000))
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/complex.sql", "r") as f:
        rows = f.readlines()[0:10_000]

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_complex_table_10_000")
    conn.execute("drop type if exists colors")


def complex_create_and_insert_100_000_rows():
    uri = os.environ["DATABASE_URI_POSTGRESQL"]
    conn: PySQLXEngineSync = PySQLXEngineSync(uri)
    assert conn.connected is True

    resp = conn.execute("drop table if exists test_benchmark_complex_table_100_000")
    assert resp == 0

    resp = conn.execute("drop type if exists colors")
    assert resp == 0

    resp = conn.execute("create type colors as enum ('blue', 'red', 'gray', 'black');")
    assert resp == 0

    resp = conn.execute(sql=sample_table.format(table_name=100_000))
    assert resp == 0

    with open("tests/benchmark/sql/pgsql/complex.sql", "r") as f:
        rows = f.readlines()

    for row in rows:
        resp = conn.execute(sql=row.replace("\n", ""))
        assert resp == 1

    conn.execute("drop table if exists test_benchmark_complex_table_100_000")
    conn.execute("drop type if exists colors")
