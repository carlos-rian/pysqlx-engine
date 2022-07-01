import asyncio
import logging
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sqlx_engine import SQLXEngine

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

data = None


def time_since(start: float, precision: int = 4) -> str:
    # TODO: prettier output
    delta = round(time.monotonic() - start, precision)
    return f"{delta}s"


async def main():
    global data
    start = time.monotonic()
    uri = "postgresql://postgres:password@localhost:5432/fastapi_prisma?schema=public"
    db = SQLXEngine(provider="postgresql", uri=uri)
    await db.connect()
    print("connect:  ", time_since(start))

    start2 = time.monotonic()
    data = await db.query("SELECT * FROM public.peoples")
    print("deserial: ", time_since(start2))

    # start3 = time.monotonic()
    # data = await db.query(query="SELECT * FROM public.peoples", as_base_row=False)
    # print("serial", time() - init)
    # print(data)

    start4 = time.monotonic()
    data2 = await db.execute(
        """INSERT INTO public.peoples (
            id, 
            name, 
            age, 
            created_at, 
            updated_at) 
            VALUES (
                'a7e382c9-8d6d-4233-b1be-be9ef6024bd2', 
                'string\\n', 
                0, 
                '2022-06-21 12:53:46.278', 
                '2022-06-21 12:53:46.278');"""
    )
    print("insert:   ", time_since(start4))
    print("total:    ", time_since(start))


asyncio.run(main())
