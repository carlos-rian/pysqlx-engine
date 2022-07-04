class GenericSQLXEngineError(Exception):
    @property
    def name(self):
        return self.__class__.__name__


class SQLXEngineError(GenericSQLXEngineError):
    ...
