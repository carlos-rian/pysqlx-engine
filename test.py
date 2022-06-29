import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sqlx_engine import SQLXEngine

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


async def main():
    uri = "postgresql://postgres:password@localhost:5432/fastapi_prisma?schema=public"
    db = SQLXEngine(provider="postgresql", uri=uri)

    await db.connect()

    data = await db.query("SELECT * FROM public.peoples")

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
