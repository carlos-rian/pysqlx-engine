from enum import Enum
from typing import Union

from .const import PROVIDER
from .errors import ParameterInvalidValueError
from .param import SupportedValueType, get_method, try_enum, try_tuple_enum


def convert(provider: PROVIDER, value: SupportedValueType, field: str = "") -> Union[str, int, float]:
	if value is None:
		return "NULL"

	elif isinstance(value, Enum):
		return try_enum(provider, value, field)

	elif isinstance(value, tuple) and len(value) > 0 and isinstance(value[0], Enum):
		return try_tuple_enum(provider, value, field)

	typ_ = type(value)
	method = get_method(typ=typ_)
	if method is None:
		raise ParameterInvalidValueError(
			field=field,
			provider=provider,
			typ_from=typ_,
			typ_to="str|int|float|etc",
			details="invalid type, the value is not a allowed type.",
		)

	return method(provider, value, field)
