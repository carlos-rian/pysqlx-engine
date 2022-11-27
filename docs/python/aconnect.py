import asyncio

from pysqlx_engine import PySQLXEngine

uri = "sqlite:./db.db"
db = PySQLXEngine(uri=uri)


async def main():
    print("connecting...")
    await db.connect()
    print(f"it`s connected: {db.connected}")


asyncio.run(main())
