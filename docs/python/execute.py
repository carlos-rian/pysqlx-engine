import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def create_table(db: SQLXEngine):
    stmt = """CREATE TABLE user (
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

async def insert_row(db: SQLXEngine):
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
