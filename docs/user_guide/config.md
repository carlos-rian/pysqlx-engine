# Config

PySQLXEngine has some settings that can help the developer identify problems and have a better experience when dealing with the application's logs and errors.

You can configure these settings using environment variables or `LOG_CONFIG` const to change logs and errors.

---
## Keyword

* `PYSQLX_SQL_LOG`: default(`False`) If `True`, the SQL statements will be printed in the console. This log is available at the `INFO` level of the `logging`.
* `PYSQLX_USE_COLOR`: default(`False`) If `True`, the messages will be printed in color.
* `PYSQLX_ERROR_JSON_FMT`: default(`False`) If `True`, the error messages will be printed in JSON format.

---

## Set environment variables

=== "**Linux**"

    ```bash
    export PYSQLX_SQL_LOG=1
    export PYSQLX_USE_COLOR=1
    export PYSQLX_ERROR_JSON_FMT=1
    ```
=== "**Windows**"

    ```bash
    set PYSQLX_SQL_LOG=1
    set PYSQLX_USE_COLOR=1
    set PYSQLX_ERROR_JSON_FMT=1
    ```
---

## Set LOG_CONFIG const

``` py linenums="1"
from pysqlx_engine import LOG_CONFIG

LOG_CONFIG.PYSQLX_SQL_LOG = True
LOG_CONFIG.PYSQLX_USE_COLOR = True
LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

```

---

## Config the logger

After setting the environment variables or `LOG_CONFIG` const, you can configure the logger as you wish.

The PySQLXEngine logger is available at root logger.

=== "Environment variables"

    ``` py linenums="1" hl_lines="5" title="main.py"
    import logging
    from pysqlx_engine import PySQLXEngineSync

    # set the logger level to INFO
    logging.basicConfig(level=logging.INFO)

    # connect to the database
    db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db")
    db.connect()

    # run the query and see the log
    db.query("SELECT * FROM valid_table") # change the 'valid_table' 
    db.query("SELECT * FROM invalid_table")

    ```

=== "LOG_CONFIG const"

    ``` py linenums="1" hl_lines="5" title="main.py"
    import logging
    from pysqlx_engine import PySQLXEngineSync, LOG_CONFIG

    LOG_CONFIG.PYSQLX_SQL_LOG = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    # set the logger level to INFO
    logging.basicConfig(level=logging.INFO)

    # connect to the database
    db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db")
    db.connect()

    # run the query and see the log
    db.query("SELECT * FROM valid_table") # change the 'valid_table'
    db.query("SELECT * FROM invalid_table")
    ```

---

### **Running the code**

Running the code using the terminal

<div class="termy">

```console
$ python3 main.py
```

</div>

**Output**

```sql title="SQL log"
INFO:root:SELECT * FROM valid_table
INFO:root:SELECT * FROM invalid_table
```

```json title="Error log"
pysqlx_engine._core.errors.QueryError: 
{
    "code": "42P01",
    "message": "relation 'invalid_table' does not exist",
    "error": "QueryError"
}
```
