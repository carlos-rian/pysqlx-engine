from pysqlx_engine import PySQLXEngineSync

uri = "sqlite:./db.db"
db = PySQLXEngineSync(uri=uri)


def create_table(db: PySQLXEngineSync):
    stmt = """CREATE TABLE IF NOT EXISTS user (
        id          INTEGER   PRIMARY KEY,
        first_name  TEXT      not null,
        last_name   TEXT      null,
        created_at  TEXT      not null,
        updated_at  TEXT      not null
    );
    """
    print("creating...")
    resp = db.execute(stmt)
    print(f"created: {resp}")


def insert_row(db: PySQLXEngineSync):
    stmt = """
        INSERT INTO user(
            first_name,
            last_name,
            created_at,
            updated_at
        ) VALUES (
            'carlos', 
            'rian', 
            '2022-05-30 05:47:51', 
            '2022-05-30 05:47:51'
        );
    """
    print(f"inserting...")
    resp = db.execute(stmt)
    print(f"inserted: {resp} affect")


def main():
    db.connect()

    # create table user
    create_table(db)
    # insert row
    insert_row(db)


main()
