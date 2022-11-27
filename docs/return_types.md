# Return Types

When use PySQLXEngine you have two function that return data. 
* `query` returns a list with one of the types below.
* `query_first` returns one of the types below.

## Return Types
* [**BaseRow**](https://pydantic-docs.helpmanual.io/) (default) is a class created from [Pydantic](https://pydantic-docs.helpmanual.io/).
* [**Dict**](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) is a standard and builtin python object.
* [**MyModel**](https://pydantic-docs.helpmanual.io/) is a class created from `BaseRow` where you can customize the output model.
In this case you can have the guarantee and autocomplete of the output.


!!! warning
    PySQLXEngine currently supports a reasonable amount of databases and versions; this brings many pros but also some cons as not all possible types of all supported databases were mapped; for example, particular types like PostgreSQL's macaddr, which would take a reasonable amount of time to develop, were not implemented. Maybe I'll do full coverage in the future, but for now, the engine works for "99%" of common day-to-day uses.



## BaseRow column types

Each row returned from the database is transformed to [pydantic](https://pydantic-docs.helpmanual.io) object.

| **DB Types** | **Python Types**             | **Default** |
|--------------|------------------------------|-------------|
| **int**      | int                          | -           |
| **bigint**   | int                          | -           |
| **float**    | float                        | -           |
| **double**   | float                        | -           |
| **string**   | str                          | -           |
| **bool**     | bool                         | -           |
| **char**     | str                          | -           |
| **decimal**  | Decimal                      | -           |
| **json**     | Pydantic Json(Dict, List)    | -           |
| **uuid**     | UUID                         | -           |
| **datetime** | datetime                     | -           |
| **date**     | date                         | -           |
| **time**     | time                         | -           |
| **array**    | list                         | -           |
| **xml**      | str                          | -           |
| **bytes**    | bytes                        | -           |
| **enum**     | str                          | -           |
| **null**     | NoneType                     | None        |


## Dict column types

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
| **decimal**  | str              | -           |
| **json**     | str              | -           |
| **uuid**     | str              | -           |
| **datetime** | str              | -           |
| **date**     | str              | -           |
| **time**     | str              | -           |
| **array**    | list             | -           |
| **xml**      | str              | -           |
| **bytes**    | Any              | -           |
| **enum**     | str              | -           |
| **null**     | NoneType         | None        |
