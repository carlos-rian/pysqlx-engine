# Advanced Guide

Although PySQLXEngine has only two methods to deal with the database, being the `query` and `execute`.

`execute` always returns the number of rows affected. Maybe this is not useful, because if you make an `insert` and want the `id` as a return, the `execute` will limit you.

Although sql statements are atomic, one execution at a time, most modern databases bring sensational features like **`RETUNING`** or **`OUTPUT`** in the case of *SQL Server* that can return a value after the insert .

So since we need something to be returned, we can use the `query`.

## Examples

In this examples we use the user table, which has the structure below. 
Change the types to your database types. In this `SQLite` is used.

```sql
CREATE TABLE user (
    id          INTEGER  PRIMARY KEY,
    first_name  TEXT
    last_name   TEXT
    created_at  TEXT
    updated_at  TEXT
)
```

!!! warning
    In this example, **MySQL** is not mentioned because it does not have reliable support for this type of execution.

    You can use `SELECT LAST_INSERT_ID();` after **inserting the row**, but it is not guaranteed to be the correct ID, given that in a concurrent DB, many inserts at the same time, and the `LAST_INSERT_ID(`) function takes only the last one. *If possible, start using MariaDB; in addition to being more reliable, it is also an up-to-date open source.*

### PostgreSQL, SQLite and MariaDB

* Create `main.py` file with:

```Python hl_lines="24 27"
{!./python/advanced.py!}
```

* Run it

<div class="termy">

```console
$ python3 main.py

[BaseRow(id=1)]
```
</div>

### Microsoft SQL Server 

* Create `main.py` file with:

```Python hl_lines="18 27"
{!./python/advanced_sql_server.py!}
```

* Run it

<div class="termy">

```console
$ python3 main.py

[BaseRow(id=1)]
```
</div>