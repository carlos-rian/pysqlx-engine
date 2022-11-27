import asyncio

from pysqlx_engine import PySQLXEngine

uri = "sqlite:./db.db"
db = PySQLXEngine(uri=uri)


async def main():
    await db.connect()

    sql = """sql
        INSERT INTO user (
            first_name, 
            last_name, 
            created_at, 
            updated_at) 
        VALUES (
            'bob', 
            'test', 
            '2022-05-30 05:47:51', 
            '2022-05-30 05:47:51'
        )
        RETURNING id;
    """

    row = await db.query(sql)
    print(row)


asyncio.run(main())
