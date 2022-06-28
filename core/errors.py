import json
from typing import Any, Dict, List

import httpx

from ._errors_mapping import ERRORS_MAPPING


class PrismaError(Exception):
    @property
    def name(self):
        return self.__class__.__name__


class AlreadyConnectedError(PrismaError):
    ...


class EngineConnectionError(PrismaError):
    ...


class NotConnectedError(PrismaError):
    ...


class EngineRequestError(PrismaError):
    ...


class UnprocessableEntityError(PrismaError):
    def __init__(self, resp: httpx.Response, *args) -> None:
        error_msg = f"status_code: {resp.status_code} -> body: {resp.json()}"
        super().__init__(error_msg, *args)


class EngineError(PrismaError):
    ...


def handler_error(errors: List[Dict[str, Any]]):
    try:
        for error in errors:
            user_facing_error = error.get("user_facing_error", {})
            error_code = user_facing_error.get("error_code")

            message = user_facing_error.get("message", "")
            error_msg = ERRORS_MAPPING.get(error_code)
            if error_msg:
                complete_msg = json.dumps(
                    {
                        "code": error_code,
                        "message": message,
                        "description": error_msg,
                        "helper": (
                            "https://www.prisma.io/docs/reference/"
                            "api-reference/error-reference#error-codes"
                        ),
                        "trace": error,
                    },
                    indent=2,
                )
                raise EngineError(complete_msg)
        raise PrismaError()
    except PrismaError:
        raise PrismaError(f"Could not process erroneous response: {errors}")
