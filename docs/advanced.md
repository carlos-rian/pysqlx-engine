# Advanced Guide

Although PySQLXEngine has only two methods to deal with the database, being the [`query`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbquery) and [`execute`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbexecute).

[`execute`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbexecute) always returns the number of rows affected. Maybe this is not useful, because if you make an `insert` and want the `id` as a return, the [`execute`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbexecute) will limit you.

Although sql statements are atomic, one execution at a time, most modern databases bring sensational features like [**`RETUNING`**](https://www.postgresql.org/docs/current/dml-returning.html) or [**`OUTPUT`**](https://docs.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql) in the case of [*SQL Server*](https://www.microsoft.com/sql-server) that can return a value after the insert .

So since we need something to be returned, we can use the [`query`](https://carlos-rian.github.io/pysqlx-engine/tutorial/#dbquery).

## Examples

In this examples we use the user table, which has the structure below. 
Change the types to your database types. In this [`SQLite`](https://www.sqlite.org/index.html) is used.

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
    In this example, [**MySQL**](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) is not mentioned because it does not have reliable support for this type of execution.

    You can use [`SELECT LAST_INSERT_ID();`](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) after **inserting the row**, but it is not guaranteed to be the correct ID, given that in a concurrent DB, many inserts at the same time, and the [`LAST_INSERT_ID()`](https://www.w3schools.com/sql/func_mysql_last_insert_id.asp) function takes only the last one. *If possible, start using [MariaDB](https://mariadb.org/); in addition to being more reliable, it is also an up-to-date open source.*

### PostgreSQL, SQLite and MariaDB

* Create [`main.py`](./python/advanced.py) file with:

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

* Create [`main.py`](./python/advanced_sql_server.py) file with:

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