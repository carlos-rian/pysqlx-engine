from sqlx_engine import SQLXEngineSync

uri = "file:./db.db"
db = SQLXEngineSync(provider="sqlite", uri=uri)


def main():
    print("connecting...")
    db.connect()
    print(f"it`s connected: {db.connected}")


main()
