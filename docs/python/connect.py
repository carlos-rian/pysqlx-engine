from pysqlx_engine import PySQLXEngineSync

uri = "sqlite:./db.db"
db = PySQLXEngineSync(uri=uri)


def main():
    print("connecting...")
    db.connect()
    print(f"it`s connected: {db.connected}")


main()
