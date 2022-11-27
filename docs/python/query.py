import asyncio

from pysqlx_engine import PySQLXEngine

uri = "sqlite:./db.db"
db = PySQLXEngine(uri=uri)


async def select(db: PySQLXEngine):
    query = "SELECT * FROM user"
    # use arg as_base_row=False to return a list of dict
    return await db.query(sql=query)


async def main():
    await db.connect()
    rows = await select(db)
    print(rows)


asyncio.run(main())
