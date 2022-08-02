import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)


async def main():
    await db.connect()

    sql = """sql
        INSERT INTO user (
            first_name, 
            last_name, 
            created_at, 
            updated_at)
        OUTPUT Inserted.id
        VALUES (
            'bob', 
            'test', 
            '2022-05-30 05:47:51', 
            '2022-05-30 05:47:51'
        );
    """

    row = await db.query(sql)
    print(row)


asyncio.run(main())
