from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum



class EnumType(Enum):
    black = "black"
    white = "white"


data = {
    "type_int": 1,
    "type_smallint": 2,
    "type_bigint": 3,
    "type_numeric": 14.8389,
    "type_float": 13343400,
    "type_double": 1.6655444,
    "type_decimal": Decimal("19984"),
    "type_char": "r",
    "type_varchar": "hfhfjjieurjnnd",
    "type_nvarchar": "$~k;dldëjdjd",
    "type_text": "hefbvrnjnvorvnojqnour3nbrububutbu9eruinrvouinbrfaoiunbsfobnfsokbf",
    "type_boolean": True,
    "type_date": date.fromisoformat("2022-01-01"),
    "type_time": time.fromisoformat("12:10:11"),
    "type_timestamp": datetime.fromisoformat("2022-12-20 08:59:55"),
    "type_datetime": datetime.fromisoformat("2022-12-20 09:00:00"),
    "type_enum": "black",
    "type_json": ["name", "age"],
    "type_bytes": "super bytes".encode("utf-8"),
}
