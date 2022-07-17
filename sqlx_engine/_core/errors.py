import json
from typing import Any, Dict, List

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer

from .._config import config
from ._base_error import GenericSQLXEngineError, SQLXEngineError
from ._errors_mapping import COMMON_ERRORS_MAPPING, ENGINE_ERRORS_MAPPING
from ._except_mapping import ERRORS_MAPPING


class AlreadyConnectedError(SQLXEngineError):
    ...


class EngineConnectionError(SQLXEngineError):
    ...


class NotConnectedError(SQLXEngineError):
    ...


class EngineRequestError(SQLXEngineError):
    ...


# class UnprocessableEntityError(SQLXEngineError):
#    def __init__(self, resp: httpx.Response, *args) -> None:
#        error_msg = f"status_code: {resp.status_code} -> body: {resp.json()}"
#        super().__init__(error_msg, *args)


class EngineError(SQLXEngineError):
    ...


class BaseStartEngineError(SQLXEngineError):
    ...


class StartEngineError(BaseStartEngineError):
    def __init__(self, error: dict, *args: object) -> None:
        error_code = error.get("error_code")
        message = error.get("message", "")
        is_panic = error.get("is_panic", False)
        meta = error.get("meta", None)
        error_msg = COMMON_ERRORS_MAPPING.get(error_code)
        complete_msg = _mount_msg(
            error_code=error_code,
            message=message,
            error_msg=error_msg,
            meta=meta,
            is_panic=is_panic,
        )
        super().__init__(complete_msg)


class SQLXEngineTimeoutError(SQLXEngineError):
    ...


def _colorizer_json(dumps: str):
    return highlight(dumps, JsonLexer(), TerminalFormatter())


def _mount_msg(
    error_code: str, message: str, error_msg: str, meta: dict, is_panic: bool
):
    error_msg = json.dumps(
        {
            "is_panic": is_panic,
            "error_code": error_code,
            "error_message": message,
            "meta": meta,
            "helper": (
                "https://www.prisma.io/docs/reference/"
                "api-reference/error-reference#error-codes"
            ),
            "description": error_msg,
        },
        indent=2 if config.improved_error_log else None,
        sort_keys=False,
    )
    if not config.improved_error_log:
        return "\n" + error_msg
    return "\n" + _colorizer_json(error_msg)


def handler_error(errors: List[Dict[str, Any]]):

    for error in errors:
        user_facing_error = error.get("user_facing_error", {})

        error_code = user_facing_error.get("error_code")
        message = user_facing_error.get("message", "")
        is_panic = user_facing_error.get("is_panic", False)
        meta = user_facing_error.get("meta", False)

        error_msg = ENGINE_ERRORS_MAPPING.get(error_code)

        complete_msg = _mount_msg(
            error_code=error_code,
            message=message,
            error_msg=error_msg,
            meta=meta,
            is_panic=is_panic,
        )
        error_mapping = ERRORS_MAPPING.get(error_code)
        if error_mapping:
            raise error_mapping(complete_msg)
        raise SQLXEngineError(complete_msg)

    raise GenericSQLXEngineError(
        f"Could not process erroneous response: {json.dumps(errors, indent=2)}"
    )
