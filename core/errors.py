import httpx


class PrismaError(Exception):
    @property
    def name(self):
        return self.__class__.__name__


class AlreadyConnectedError(PrismaError):
    ...


class EngineConnectionError(PrismaError):
    ...


class NotConnectedError(PrismaError):
    ...


class EngineRequestError(PrismaError):
    ...


class UnprocessableEntityError(PrismaError):
    def __init__(self, resp: httpx.Response, *args) -> None:
        error_msg = f"status_code: {resp.status_code}\n" f"body: {resp.json()}"
        super().__init__(error_msg, *args)
