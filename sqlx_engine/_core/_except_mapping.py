from typing import Dict, Type

from ._base_error import SQLXEngineError


class UniqueViolationError(SQLXEngineError):
    ...


class ForeignKeyViolationError(SQLXEngineError):
    ...


class FieldNotFoundError(SQLXEngineError):
    ...


class RawQueryError(SQLXEngineError):
    ...


class MissingRequiredValueError(SQLXEngineError):
    ...


class InputError(SQLXEngineError):
    ...


class TableNotFoundError(SQLXEngineError):
    ...


class RecordNotFoundError(SQLXEngineError):
    ...


ERRORS_MAPPING: Dict[str, Type[Exception]] = {
    "P2002": UniqueViolationError,
    "P2003": ForeignKeyViolationError,
    "P2009": FieldNotFoundError,
    "P2010": RawQueryError,
    "P2012": MissingRequiredValueError,
    "P2019": InputError,
    "P2021": TableNotFoundError,
    "P2025": RecordNotFoundError,
}
