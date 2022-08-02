import asyncio

from sqlx_engine import SQLXEngine

uri = "file:./db.db"
db = SQLXEngine(provider="sqlite", uri=uri)

async def main():
    print("connecting...")
    await db.connect()
    print(f"it`s connected: {db.connected}")

asyncio.run(main())
