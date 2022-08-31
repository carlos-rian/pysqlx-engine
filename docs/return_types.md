# Return Types

PySQLXEngine always returns a list with one of the two types below..

* [**BaseRow**](https://pydantic-docs.helpmanual.io/) (default) is a class created from [Pydantic](https://pydantic-docs.helpmanual.io/).
* [**Dict**](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) is a standard and builtin python object.


## BaseRow

Each row returned from the database is transformed to [pydantic](https://pydantic-docs.helpmanual.io) object.

| **DB Types** | **Python Types** | **Default** |
|--------------|------------------|-------------|
| **int**      | int              | -           |
| **bigint**   | int              | -           |
| **float**    | float            | -           |
| **double**   | float            | -           |
| **string**   | str              | -           |
| **bool**     | bool             | -           |
| **char**     | str              | -           |
| **decimal**  | Decimal          | -           |
| **json**     | Pydantic Json    | -           |
| **uuid**     | UUID             | -           |
| **datetime** | datetime         | -           |
| **date**     | date             | -           |
| **time**     | time             | -           |
| **array**    | list             | -           |
| **xml**      | str              | -           |
| **bytes**    | Any              | -           |
| **enum**     | Any              | -           |
| **null**     | Any              | None        |


## Dict

Each row returned from the database is transformed to [dict](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) object.

| **DB Types** | **Python Types** | **Default** |
|--------------|------------------|-------------|
| **int**      | int              | -           |
| **bigint**   | int              | -           |
| **float**    | float            | -           |
| **double**   | float            | -           |
| **string**   | str              | -           |
| **bool**     | bool             | -           |
| **char**     | str              | -           |
| **decimal**  | Any              | -           |
| **json**     | str              | -           |
| **uuid**     | str              | -           |
| **datetime** | str              | -           |
| **date**     | str              | -           |
| **time**     | int              | -           |
| **array**    | list             | -           |
| **xml**      | str              | -           |
| **bytes**    | Any              | -           |
| **enum**     | str              | -           |
| **null**     | NoneType         | None        |
