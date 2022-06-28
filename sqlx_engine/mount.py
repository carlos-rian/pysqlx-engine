from typing import Literal

from typing_extensions import LiteralString


def mount_body(_type: Literal["queryRaw", "executeRaw"], _sql: LiteralString) -> str:
    return {
        "variables": {},
        "operation_name": "mutation",
        "query": {
            """
                mutation {
                    result: {_type} 
                    (
                        query: "{_sql}"
                        parameters: "[]"
                    )
                }
            """
        },
    }
