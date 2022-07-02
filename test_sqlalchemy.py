from time import time

from sqlalchemy import create_engine


def main():
    ini = time()
    uri = "postgresql://postgres:password@localhost:5432/fastapi_prisma"
    engine = create_engine(uri)
    conn = engine.connect()
    print("connect", time() - ini)

    init = time()
    data = conn.execute("SELECT * FROM public.peoples").fetchall()
    print("serial", time() - init)

    init = time()
    conn.execute(
        """INSERT INTO public.peoples (
            id, 
            name, 
            age, 
            created_at, 
            updated_at) 
            VALUES (
                'a7e382c9-8d6d-4233-b1be-be9ef6024bd7', 
                'string\\n', 
                0, 
                '2022-06-21 12:53:46.278', 
                '2022-06-21 12:53:46.278');"""
    )
    print("insert", time() - init)

    print("total", time() - ini)


main()
