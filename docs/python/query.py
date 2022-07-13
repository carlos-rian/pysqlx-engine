import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def select(db: SQLXEngine):
    query = "SELECT * FROM user"
    # use arg as_base_row=False to return a list of dict
    return await db.query(query=query)

async def main():
    await db.connect()
    rows = await select(db)
    print(rows)

asyncio.run(main())
