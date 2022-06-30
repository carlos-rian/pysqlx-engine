import asyncio
import logging
import os
import sys
from time import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sqlx_engine import SQLXEngine

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

data = None


async def main():
    global data
    ini = time()
    uri = "postgresql://postgres:password@localhost:5432/fastapi_prisma?schema=public"
    db = SQLXEngine(provider="postgresql", uri=uri)
    await db.connect()
    print("connect", time() - ini)

    # init = time()
    # data = await db.query("SELECT * FROM public.peoples")
    # print("deserial", time() - init)
    # print(data)

    init = time()
    data = await db.query(query="SELECT * FROM public.peoples", as_base_row=False)
    print("serial", time() - init)
    # print(data)

    print("total", time() - ini)

    return data
    print(data)

    data2 = await db.execute(
        """
        INSERT INTO public.peoples (
            id, 
            name, 
            age, 
            created_at, 
            updated_at
        ) VALUES (
            'a7e382c9-8d6d-4233-b1be-be9ef6024ba1', 
            'string', 
            0, 
            '2022-06-21 12:53:46.278', 
            '2022-06-21 12:53:46.278');"
        )
        """
    )

    print(data2)


asyncio.run(main())
