import asyncio

from pysqlx_engine import PySQLXEngine

uri = "sqlite:./db.db"
db = PySQLXEngine(uri=uri)


async def create_table(db: PySQLXEngine):
    stmt = """CREATE TABLE IF NOT EXISTS user (
        id          INTEGER   PRIMARY KEY,
        first_name  TEXT      not null,
        last_name   TEXT      null,
        created_at  TEXT      not null,
        updated_at  TEXT      not null
    );
    """
    print("creating...")
    resp = await db.execute(stmt)
    print(f"created: {resp}")


async def insert_row(db: PySQLXEngine):
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
    resp = await db.execute(stmt)
    print(f"inserted: {resp} affect")


async def main():
    await db.connect()

    # create table user
    await create_table(db)
    # insert row
    await insert_row(db)


asyncio.run(main())
