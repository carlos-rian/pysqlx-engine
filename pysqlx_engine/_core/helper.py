import json
from functools import lru_cache

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, PythonLexer
from pygments.lexers.sql import SqlLexer

from .const import LOG_CONFIG


def _colorizer_json_message(dumps: str):
	return highlight(dumps, JsonLexer(), TerminalFormatter())


def fe_json(data: dict) -> str:
	"""create a error message format for python code"""
	dumps = json.dumps(data, indent=2)
	if LOG_CONFIG.PYSQLX_USE_COLOR:
		return "\n" + _colorizer_json_message(dumps)
	return "\n" + dumps


def _colorizer_py_code_message(message: str):
	return highlight(message, PythonLexer(), TerminalFormatter())


def fe_py(message: str) -> str:
	"""create a error message format for python code"""
	if LOG_CONFIG.PYSQLX_USE_COLOR:
		return _colorizer_py_code_message(message)
	return message


@lru_cache(maxsize=None)
def _colorizer_sql_message(sql: str):
	return highlight(sql, SqlLexer(), TerminalFormatter())


def fe_sql(sql: str) -> str:
	"""create a error message format for python code"""
	if LOG_CONFIG.PYSQLX_USE_COLOR:
		return _colorizer_sql_message(sql)
	return sql


def isolation_error_message():
	return f"""
    the isolation_level must be a valid value.

    possible values:
        >> ReadUncommitted
        >> ReadCommitted
        >> RepeatableRead
        >> Snapshot
        >> Serializable

    example of use:
        >> {fe_py('isolation_level = "ReadUncommitted"')}
    """


def not_connected_error_message():
	return f"""
        not connected to the database.

        before using the methods, you must connect to the database.
            
        example of use:
            Async:
                {fe_py('''uri = "postgresql://user:pass@host:port/db?schema=sample"
                db = PySQLXEngine(uri=uri)
                await db.connect()
                ''')}
            Sync:
                {fe_py('''uri = "postgresql://user:pass@host:port/db?schema=sample"
                db = PySQLXEngineSync(uri=uri)
                db.connect()
                ''')}
    """


def model_parameter_error_message():
	return f"""
        model parameter must be a subclass of BaseRow or Pydantic BaseModel.

        try importing the BaseRow class from the pysqlx_engine package.

        example of use:
            {fe_py('''
            
            # import the BaseRow class
            from pysqlx_engine import BaseRow

            class MyModel(BaseRow): # <- subclass of BaseRow
                id: int
                name: str
    
            # async
            db = PySQLXEngine(uri="postgresql://user:pass@host:port/db?schema=sample")
            await db.connect()
            await db.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel) # <- using how model parameter

            # sync
            db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db?schema=sample")
            db.connect()
            db.query(sql="SELECT 1 AS id, 'Rian' AS name", model=MyModel) # <- using how model parameter
            ''')
            }
        """


def sql_type_error_message():
	return f"""
        the queries and statements must be a valid string.

        you can not use a type other than string.

        example of use:
            {fe_py('''
            
            # async
            db = PySQLXEngine(uri="postgresql://user:pass@host:port/db?schema=sample")
            await db.connect()
            await db.query(sql="SELECT 1 AS id, 'Rian' AS name") # <- Literal string
            # or
            sql = "SELECT 1 AS id, 'Rian' AS name"
            await db.query(sql=sql) # <- Variable string


            # sync
            db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db?schema=sample")
            db.connect()
            db.query(sql="SELECT 1 AS id, 'Rian' AS name") # <- Literal string
            # or
            sql = "SELECT 1 AS id, 'Rian' AS name"
            db.query(sql=sql) # <- Variable string

            ''')}
    """


def parameters_type_error_message():
	return f"""
        the parameters must be a valid dict.

        you can not use a type other than dict[str, any].

        * dict key must be a valid string.
        * dict value can be a types: bool, str, int, list, dict, tuple, UUID, time, date, datetime, float, bytes, Decimal

        Python types vs SQL types:
            bool     -> bool/bit/boolean/tinyint/etc
            str      -> varchar/text/nvarchar/char/etc
            int      -> int/integer/smallint/bigint/tinyint/etc
            list     -> json/jsonb/nvarchar/varchar/string/etc
            dict     -> json/jsonb/nvarchar/varchar/string/etc
            tuple    -> array(Postgres Native)
            UUID     -> uuid/varchar/text/nvarchar/etc
            time     -> time/nvarchar/varchar/string/etc
            date     -> date/nvarchar/varchar/string/etc
            datetime -> timestamp/timestamptz/datetime/datetime2/nvarchar/varchar/string/etc
            float    -> float/real/numeric
            bytes    -> bytea/binary/varbinary
            Decimal  -> decimal/numeric
            None     -> null


        example of use:
            {fe_py('''
            
            # ===== async
            db = PySQLXEngine(uri="postgresql://user:pass@host:port/db?schema=sample")
            await db.connect()

            # Literal string with parameters
            await db.query(sql="SELECT :id AS id, :name AS name", parameters={"id": 1, "name": "Rian"})
            
            # or

            # Variable string with parameters
            sql = "SELECT :id AS id, :name AS name"
            parameters = {"id": 1, "name": "Rian"}
            await db.query(sql=sql, parameters=parameters) 


            # ===== sync
            db = PySQLXEngineSync(uri="postgresql://user:pass@host:port/db?schema=sample")
            db.connect()

            # Literal string with parameters
            db.query(sql="SELECT :id AS id, :name AS name", parameters={"id": 1, "name": "Rian"})
            
            # or
            
            # Variable string with parameters
            sql = "SELECT :id AS id, :name AS name"
            parameters = {"id": 1, "name": "Rian"}
            db.query(sql=sql, parameters=parameters) 

            ''')}
    """
