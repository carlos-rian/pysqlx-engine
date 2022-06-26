from .abc import AbstractEngine


class ProcessDB(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()
        self._uri
