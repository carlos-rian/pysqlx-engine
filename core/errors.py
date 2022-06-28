class PrismaError(Exception):
    ...


class AlreadyConnectedError(PrismaError):
    ...


class EngineConnectionError(PrismaError):
    ...
