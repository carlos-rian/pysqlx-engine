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

    print("total", time() - ini)


main()
