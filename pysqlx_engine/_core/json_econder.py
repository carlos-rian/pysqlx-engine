import json
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from .errors import ParameterInvalidJsonValueError


class PySQLXJsonEnconder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return obj.hex()

		elif isinstance(obj, (UUID, time, date, datetime, Decimal)):
			return str(obj)
		try:
			return super().default(obj)
		except TypeError as err:
			raise ParameterInvalidJsonValueError(
				typ_from=type(obj),
				typ_to="json",
				details=str(err),
			)
