import json
from os import getenv

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, PythonLexer


def _colorizer_py_code_message(message: str):
    return highlight(message, PythonLexer(), TerminalFormatter())


def _colorizer_json_message(data: dict):
    dumps = json.dumps(data, indent=2)
    return highlight(dumps, JsonLexer(), TerminalFormatter())


def fe_py(message: str) -> str:
    """create a error message format for python code"""
    if getenv("PYSQLX_ERROR_COLORIZE", "1") == "1":
        return _colorizer_py_code_message(message)
    return message


def fe_json(data: dict) -> str:
    """create a error message format for python code"""
    if getenv("PYSQLX_ENGINE_COLORIZE", "1") == "1":
        return "\n" + _colorizer_json_message(data)
    return "\n" + json.dumps(data, indent=2)


def isolation_error_message():
    return f"""
    isolation_level must be of type IsolationLevel.

    try import:
        {fe_py('from pysqlx_engine import IsolationLevel')}.

    possible values:
        >> IsolationLevel.ReadUncommitted
        >> IsolationLevel.ReadCommitted
        >> IsolationLevel.RepeatableRead
        >> IsolationLevel.Snapshot
        >> IsolationLevel.Serializable

    example of use:
        >> {fe_py('isolation_level = IsolationLevel.ReadUncommitted')}
    """


def not_connected_error_message():
    return f"""
        not connected to the database.

        before using the methods, you must connect to the database.
            
        example of use:

            {fe_py('''uri = "postgresql://user:pass@host:port/db?schema=sample"
            db = PySQLXEngine(uri=uri)
            await db.connect()
            ''')}
    """


if __name__ == "__main__":
    # try using value error
    raise ValueError(isolation_error_message())
