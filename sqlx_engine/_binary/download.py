import logging
from functools import lru_cache
from time import time

from httpx import HTTPStatusError

from .engine import Engine

log: logging.Logger = logging.getLogger()


@lru_cache(maxsize=None)
def check_binary(*args, **kwargs) -> str:
    log.debug("Checking engine binary file.")
    ini = time()
    try:
        engine = Engine()
        path = engine.binary_path
        log.debug(f"Check binary ok. time: {time() - ini}")
        return path
    except HTTPStatusError:
        log.error("Error: Download of the query binary.")
        raise
