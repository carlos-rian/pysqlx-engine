from json import dumps
from typing import Literal

from typing_extensions import LiteralString


def mount_body(_type: Literal["queryRaw", "executeRaw"], _sql: LiteralString) -> str:
    query = """
        mutation {
            result: _type 
            (
                query: "_sql"
                parameters: "[]"
            )
        }
    """
    query = query.replace("_type", _type)
    query = query.replace("_sql", _sql)
    data = {"variables": {}, "operation_name": "mutation", "query": query}

    return dumps(data)
